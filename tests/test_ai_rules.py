import pytest
from ai.rules.engine_rules import (
    EngineOverheatRule,
    CoolantTemperatureRule,
    BatteryVoltageRule,
    MisfireDetectionRule,
    DTCDetectionRule
)


class TestEngineOverheatRule:
    def test_overheat_triggered(self):
        """Test that rule triggers when coolant temp > 105"""
        rule = EngineOverheatRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 112}
            }
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1
        assert "overheating" in result.issues[0].message.lower()
        assert result.issues[0].severity == "CRITICAL"

    def test_overheat_boundary_no_trigger(self):
        """Test that rule does not trigger at boundary (105)"""
        rule = EngineOverheatRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 105}
            }
        }
        result = rule.evaluate(data)
        assert result is None

    def test_overheat_slightly_over_boundary(self):
        """Test that rule triggers slightly over boundary (106)"""
        rule = EngineOverheatRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 106}
            }
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1

    def test_overheat_missing_data(self):
        """Test graceful handling of missing coolant temp data"""
        rule = EngineOverheatRule()
        data = {
            "live_parameters": {}
        }
        result = rule.evaluate(data)
        assert result is None

    def test_overheat_invalid_data_type(self):
        """Test handling of non-numeric coolant temp"""
        rule = EngineOverheatRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": "hot"}
            }
        }
        result = rule.evaluate(data)
        assert result is None  # Should not crash


class TestCoolantTemperatureRule:
    def test_low_temp_triggered(self):
        """Test that rule triggers when coolant temp < 70"""
        rule = CoolantTemperatureRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 65}
            }
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1
        assert "thermostat" in result.issues[0].message.lower()

    def test_low_temp_boundary_no_trigger(self):
        """Test that rule does not trigger at boundary (70)"""
        rule = CoolantTemperatureRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 70}
            }
        }
        result = rule.evaluate(data)
        assert result is None

    def test_normal_temp_no_trigger(self):
        """Test that rule does not trigger for normal temps"""
        rule = CoolantTemperatureRule()
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 85}
            }
        }
        result = rule.evaluate(data)
        assert result is None


class TestBatteryVoltageRule:
    def test_low_voltage_triggered(self):
        """Test that rule triggers when voltage < 12.0"""
        rule = BatteryVoltageRule()
        data = {
            "live_parameters": {
                "battery_voltage": {"value": 11.5}
            }
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1
        assert "charging system" in result.issues[0].message.lower()
        assert result.issues[0].severity == "HIGH"

    def test_low_voltage_boundary_no_trigger(self):
        """Test that rule does not trigger at boundary (12.0)"""
        rule = BatteryVoltageRule()
        data = {
            "live_parameters": {
                "battery_voltage": {"value": 12.0}
            }
        }
        result = rule.evaluate(data)
        assert result is None

    def test_normal_voltage_no_trigger(self):
        """Test that rule does not trigger for normal voltage"""
        rule = BatteryVoltageRule()
        data = {
            "live_parameters": {
                "battery_voltage": {"value": 13.8}
            }
        }
        result = rule.evaluate(data)
        assert result is None


class TestMisfireDetectionRule:
    def test_misfire_triggered(self):
        """Test that rule triggers when P030x DTC is present"""
        rule = MisfireDetectionRule()
        data = {
            "dtc_codes": ["P0301", "P0118"]
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1
        assert "misfire" in result.issues[0].message.lower()

    def test_misfire_multiple_p030(self):
        """Test that rule triggers for any P030x code"""
        rule = MisfireDetectionRule()
        data = {
            "dtc_codes": ["P0300", "P0302", "P0304"]
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1

    def test_misfire_no_trigger(self):
        """Test that rule does not trigger without P030x codes"""
        rule = MisfireDetectionRule()
        data = {
            "dtc_codes": ["P0118", "P0123"]
        }
        result = rule.evaluate(data)
        assert result is None

    def test_misfire_empty_dtc(self):
        """Test that rule does not trigger with empty DTC list"""
        rule = MisfireDetectionRule()
        data = {
            "dtc_codes": []
        }
        result = rule.evaluate(data)
        assert result is None

    def test_misfire_missing_dtc(self):
        """Test that rule handles missing DTC codes gracefully"""
        rule = MisfireDetectionRule()
        data = {}
        result = rule.evaluate(data)
        assert result is None


class TestDTCDetectionRule:
    def test_dtc_present_triggered(self):
        """Test that rule triggers when DTC codes are present"""
        rule = DTCDetectionRule()
        data = {
            "dtc_codes": ["P0118", "P0301"]
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1
        assert "P0118" in result.issues[0].message
        assert "P0301" in result.issues[0].message

    def test_dtc_single_code(self):
        """Test that rule triggers with single DTC code"""
        rule = DTCDetectionRule()
        data = {
            "dtc_codes": ["P0123"]
        }
        result = rule.evaluate(data)
        assert result is not None
        assert len(result.issues) == 1

    def test_dtc_empty_no_trigger(self):
        """Test that rule does not trigger with empty DTC list"""
        rule = DTCDetectionRule()
        data = {
            "dtc_codes": []
        }
        result = rule.evaluate(data)
        assert result is None

    def test_dtc_missing_no_trigger(self):
        """Test that rule does not trigger with missing DTC codes"""
        rule = DTCDetectionRule()
        data = {}
        result = rule.evaluate(data)
        assert result is None


class TestRuleContradictorySignals:
    """Test rules with contradictory or edge case signals"""

    def test_overheat_and_low_temp_contradiction(self):
        """Test that rules handle physically impossible states"""
        overheat_rule = EngineOverheatRule()
        low_temp_rule = CoolantTemperatureRule()

        # Impossible: both overheating and low temp
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 120}  # This would trigger overheat
            }
        }

        overheat_result = overheat_rule.evaluate(data)
        assert overheat_result is not None

        # Low temp rule should not trigger for high temp
        low_temp_result = low_temp_rule.evaluate(data)
        assert low_temp_result is None

    def test_voltage_and_temp_independence(self):
        """Test that voltage and temp rules are independent"""
        voltage_rule = BatteryVoltageRule()
        temp_rule = EngineOverheatRule()

        data = {
            "live_parameters": {
                "battery_voltage": {"value": 11.0},  # Low voltage
                "coolant_temp": {"value": 110}      # High temp
            }
        }

        voltage_result = voltage_rule.evaluate(data)
        temp_result = temp_rule.evaluate(data)

        assert voltage_result is not None
        assert temp_result is not None
        assert len(voltage_result.issues) == 1
        assert len(temp_result.issues) == 1