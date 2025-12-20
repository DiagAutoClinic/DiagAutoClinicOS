import pytest
from unittest.mock import Mock, MagicMock, patch
from ai.core.diagnostics_engine import DiagnosticsEngine
from ai.core.config import AIConfig
from ai.core.exceptions import DiagnosticError


class TestDiagnosticsEngineOrchestration:
    @pytest.fixture
    def config(self):
        return AIConfig()

    @pytest.fixture
    def mock_ml_loader(self):
        loader = Mock()
        loader.is_available.return_value = True
        return loader

    @pytest.fixture
    def mock_can_db(self):
        db = Mock()
        return db

    @pytest.fixture
    def mock_rule_engine(self):
        engine = Mock()
        engine.evaluate_all.return_value = []
        return engine

    @pytest.fixture
    def engine(self, config, mock_ml_loader, mock_can_db, mock_rule_engine):
        return DiagnosticsEngine(config, mock_ml_loader, mock_can_db, mock_rule_engine)

    @patch.object(DiagnosticsEngine, '_run_rule_diagnosis')
    @patch.object(DiagnosticsEngine, '_run_ml_diagnosis')
    def test_ml_success_prevents_rules_call(self, mock_run_ml, mock_run_rule, engine, mock_ml_loader, mock_rule_engine):
        """Test that when ML succeeds, rules are not evaluated"""
        # Setup mocks
        mock_run_ml.return_value = {
            "diagnosis": "ML diagnosis",
            "confidence": 0.8,
            "severity": "MEDIUM"
        }
        mock_run_rule.return_value = []

        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        result = engine.diagnose(test_data)

        # Verify ML was called
        mock_run_ml.assert_called_once_with(test_data)

        # Verify rules were not called (since ML succeeded)
        mock_run_rule.assert_not_called()

        assert result["diagnosis"] == "ML diagnosis"
        assert result["confidence"] == 0.8

    @patch.object(DiagnosticsEngine, '_run_rule_diagnosis')
    @patch.object(DiagnosticsEngine, '_run_ml_diagnosis')
    def test_ml_failure_triggers_rules(self, mock_run_ml, mock_run_rule, engine, mock_ml_loader, mock_rule_engine):
        """Test that when ML fails, rules are evaluated"""
        # Mock ML to fail
        mock_run_ml.return_value = None

        # Mock rules to return issues
        mock_issues = [Mock()]
        mock_issues[0].message = "Rule issue"
        mock_issues[0].severity = "HIGH"
        mock_run_rule.return_value = mock_issues

        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        result = engine.diagnose(test_data)

        # Verify ML was called
        mock_run_ml.assert_called_once_with(test_data)

        # Verify rules were called
        mock_run_rule.assert_called_once_with(test_data)

        assert "Issues detected" in result["diagnosis"]
        assert result["severity"] == "HIGH"

    @patch.object(DiagnosticsEngine, '_run_rule_diagnosis')
    @patch.object(DiagnosticsEngine, '_run_ml_diagnosis')
    def test_both_ml_and_rules_fail_uses_fallback(self, mock_run_ml, mock_run_rule, engine):
        """Test that when both ML and rules fail, fallback is used"""
        # Mock both to fail
        mock_run_ml.return_value = None
        mock_run_rule.return_value = []

        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        result = engine.diagnose(test_data)

        # Verify both were called
        mock_run_ml.assert_called_once_with(test_data)
        mock_run_rule.assert_called_once_with(test_data)

        assert "All monitored systems appear normal" in result["diagnosis"]
        assert result["confidence"] == 0.95
        assert result["severity"] == "NORMAL"

    @patch('ai.core.diagnostics_engine.validate_live_data')
    def test_validation_failure_raises_error(self, mock_validate, engine):
        """Test that validation failure raises DiagnosticError"""
        # Mock validation to raise error
        mock_validate.side_effect = Exception("Validation failed")

        test_data = {"invalid": "data"}

        with pytest.raises(DiagnosticError, match="Diagnosis failed"):
            engine.diagnose(test_data)

    def test_result_structure(self, engine):
        """Test that result has all required fields"""
        engine._run_ml_diagnosis = Mock(return_value=None)
        engine._run_rule_diagnosis = Mock(return_value=[])

        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        result = engine.diagnose(test_data)

        required_fields = ["agent", "timestamp", "diagnosis", "confidence", "recommendations", "severity", "mode"]
        for field in required_fields:
            assert field in result

        assert result["agent"] == "Charlemaine"
        assert result["mode"] == "LOCAL OFFLINE AI"
        assert isinstance(result["timestamp"], str)
        assert isinstance(result["recommendations"], list)

    def test_confidence_calculation_with_issues(self, engine):
        """Test confidence calculation when issues are found"""
        engine._run_ml_diagnosis = Mock(return_value=None)

        mock_issues = [Mock()]
        mock_issues[0].message = "Test issue"
        mock_issues[0].severity = "MEDIUM"
        engine._run_rule_diagnosis = Mock(return_value=mock_issues)

        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        result = engine.diagnose(test_data)

        assert result["diagnosis"] == "Issues detected."
        assert result["confidence"] == 0.75  # Default when no ML confidence
        assert result["severity"] == "MEDIUM"