# ai/utils/validation.py

from typing import Dict, Any
from ..core.exceptions import InvalidInputError

def validate_live_data(data: Dict[str, Any]) -> None:
    """Validate the structure and required fields of live vehicle data."""
    if not isinstance(data, dict):
        raise InvalidInputError("Live data must be a dictionary")

    required_keys = {"live_parameters", "dtc_codes", "vehicle_context"}
    missing = required_keys - data.keys()
    if missing:
        raise InvalidInputError(f"Missing required keys: {missing}")

    # Validate live_parameters structure
    live_params = data.get("live_parameters", {})
    if not isinstance(live_params, dict):
        raise InvalidInputError("live_parameters must be a dictionary")

    # Check for essential parameters
    essential_params = {"engine_rpm", "coolant_temp", "battery_voltage"}
    param_keys = set(live_params.keys())
    if not essential_params.issubset(param_keys):
        missing_params = essential_params - param_keys
        raise InvalidInputError(f"Missing essential parameters: {missing_params}")

    # Validate parameter values are dictionaries with 'value' key
    for param_name, param_data in live_params.items():
        if not isinstance(param_data, dict) or "value" not in param_data:
            raise InvalidInputError(f"Parameter '{param_name}' must be a dict with 'value' key")

    # Validate dtc_codes is a list
    dtc_codes = data.get("dtc_codes", [])
    if not isinstance(dtc_codes, list):
        raise InvalidInputError("dtc_codes must be a list")

    # Validate vehicle_context is a dict
    vehicle_context = data.get("vehicle_context", {})
    if not isinstance(vehicle_context, dict):
        raise InvalidInputError("vehicle_context must be a dictionary")