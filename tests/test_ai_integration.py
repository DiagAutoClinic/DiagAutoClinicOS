import pytest
import os
import logging
from unittest.mock import patch
from ai.core.config import AIConfig
from ai.core.initializer import SystemInitializer
import charlemaine  # Import to test initialization


class TestSystemIntegration:
    def test_config_initialization(self):
        """Test that AIConfig initializes with default values"""
        config = AIConfig()
        assert config.model_path.endswith("diagnostic_ai_model.keras")
        assert config.can_db_path == "can_bus_databases.sqlite"
        assert config.enable_ml is True
        assert config.enable_ai_engine is True

    def test_config_environment_variables(self):
        """Test that config respects environment variables"""
        with patch.dict(os.environ, {
            "AI_MODEL_PATH": "/custom/models",
            "CAN_DB_PATH": "/custom/db.sqlite",
            "ENABLE_ML": "0"
        }):
            config = AIConfig()
            assert config.model_path == "/custom/models/diagnostic_ai_model.keras"
            assert config.can_db_path == "/custom/db.sqlite"
            assert config.enable_ml is False

    @patch('ai.ml.loader.MLLoader.load')
    @patch('ai.can.database.CANDatabase.connect')
    def test_system_initializer(self, mock_can_connect, mock_ml_load):
        """Test that SystemInitializer creates components without error"""
        config = AIConfig()
        initializer = SystemInitializer(config)

        ml, can, rules = initializer.initialize()

        # Check that components are created
        assert ml is not None
        assert can is not None
        assert rules is not None

        # Check that initialization methods were called
        mock_ml_load.assert_called_once()
        mock_can_connect.assert_called_once()

    def test_charlemaine_initialization(self):
        """Test that Charlemaine initializes without error"""
        # This tests the global charlemaine instance
        assert charlemaine.charlemaine is not None
        assert charlemaine.charlemaine.name == "Charlemaine"
        assert charlemaine.charlemaine.version == "1.0"
        assert charlemaine.charlemaine.mode == "LOCAL OFFLINE AI"

    def test_full_diagnose_call(self):
        """Test that a full diagnose call completes successfully"""
        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {
                "make": "Toyota",
                "model": "Camry"
            }
        }

        result = charlemaine.charlemaine.diagnose(test_data)

        # Check result structure
        assert "diagnosis" in result
        assert "confidence" in result
        assert "recommendations" in result
        assert "severity" in result
        assert "timestamp" in result
        assert result["agent"] == "Charlemaine"
        assert result["mode"] == "LOCAL OFFLINE AI"

        # Should be normal since no issues
        assert "normal" in result["diagnosis"].lower()
        assert result["severity"] == "NORMAL"

    @patch('ai.ml.loader.MLLoader.is_available')
    def test_ml_disabled_config(self, mock_ml_available):
        """Test that disabling ML via config works"""
        mock_ml_available.return_value = False

        # Create new instance with ML disabled
        config = AIConfig(enable_ml=False)
        initializer = SystemInitializer(config)
        ml, can, rules = initializer.initialize()

        # ML should not be available
        assert not ml.is_available()

        # But system should still work
        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        # Create engine with disabled ML
        from ai.core.diagnostics_engine import DiagnosticsEngine
        engine = DiagnosticsEngine(config, ml, can, rules)
        result = engine.diagnose(test_data)

        # Should still work via rules/fallback
        assert result["diagnosis"] is not None
        assert result["confidence"] > 0

    def test_logging_produced(self, caplog):
        """Test that logging calls are made during diagnosis"""
        test_data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }

        with caplog.at_level(logging.INFO):
            charlemaine.charlemaine.diagnose(test_data)

            assert "Starting diagnostic analysis" in caplog.text