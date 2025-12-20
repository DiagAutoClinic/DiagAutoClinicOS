import pytest
from ai.utils.validation import validate_live_data
from ai.core.exceptions import InvalidInputError


class TestValidateLiveData:
    def test_valid_data(self):
        """Test that valid data passes validation"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": ["P0118"],
            "vehicle_context": {
                "make": "Toyota",
                "model": "Camry"
            }
        }
        # Should not raise
        validate_live_data(data)

    def test_missing_live_parameters(self):
        """Test that missing live_parameters raises error"""
        data = {
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing required keys"):
            validate_live_data(data)

    def test_missing_dtc_codes(self):
        """Test that missing dtc_codes raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing required keys"):
            validate_live_data(data)

    def test_missing_vehicle_context(self):
        """Test that missing vehicle_context raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": []
        }
        with pytest.raises(InvalidInputError, match="Missing required keys"):
            validate_live_data(data)

    def test_wrong_data_type_dict(self):
        """Test that non-dict data raises error"""
        with pytest.raises(InvalidInputError, match="Live data must be a dictionary"):
            validate_live_data("not a dict")

    def test_live_parameters_not_dict(self):
        """Test that live_parameters not being dict raises error"""
        data = {
            "live_parameters": "not a dict",
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="live_parameters must be a dictionary"):
            validate_live_data(data)

    def test_dtc_codes_not_list(self):
        """Test that dtc_codes not being list raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": "not a list",
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="dtc_codes must be a list"):
            validate_live_data(data)

    def test_vehicle_context_not_dict(self):
        """Test that vehicle_context not being dict raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": "not a dict"
        }
        with pytest.raises(InvalidInputError, match="vehicle_context must be a dictionary"):
            validate_live_data(data)

    def test_missing_engine_rpm(self):
        """Test that missing engine_rpm raises error"""
        data = {
            "live_parameters": {
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing essential parameters"):
            validate_live_data(data)

    def test_missing_coolant_temp(self):
        """Test that missing coolant_temp raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing essential parameters"):
            validate_live_data(data)

    def test_missing_battery_voltage(self):
        """Test that missing battery_voltage raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing essential parameters"):
            validate_live_data(data)

    def test_parameter_not_dict(self):
        """Test that parameter not being dict raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": "not a dict",
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="must be a dict with 'value' key"):
            validate_live_data(data)

    def test_parameter_missing_value(self):
        """Test that parameter missing 'value' key raises error"""
        data = {
            "live_parameters": {
                "engine_rpm": {"not_value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="must be a dict with 'value' key"):
            validate_live_data(data)

    def test_partial_missing_parameters(self):
        """Test with some parameters present but not all essential ones"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "throttle_position": {"value": 50}  # Not essential
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing essential parameters"):
            validate_live_data(data)

    def test_extra_parameters_allowed(self):
        """Test that extra parameters beyond essential ones are allowed"""
        data = {
            "live_parameters": {
                "engine_rpm": {"value": 2000},
                "coolant_temp": {"value": 90},
                "battery_voltage": {"value": 13.5},
                "throttle_position": {"value": 50},
                "fuel_level": {"value": 75}
            },
            "dtc_codes": [],
            "vehicle_context": {}
        }
        # Should not raise
        validate_live_data(data)

    def test_empty_live_parameters(self):
        """Test that empty live_parameters raises error for missing essentials"""
        data = {
            "live_parameters": {},
            "dtc_codes": [],
            "vehicle_context": {}
        }
        with pytest.raises(InvalidInputError, match="Missing essential parameters"):
            validate_live_data(data)