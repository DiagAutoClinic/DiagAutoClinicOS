"""
Live Data Mock Generator for AutoDiag Pro
Provides realistic mock live data streaming for vehicle diagnostics
"""

import random
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class LiveDataParameter:
    """Represents a live data parameter with its properties"""
    name: str
    unit: str
    min_value: float
    max_value: float
    current_value: float
    variation_rate: float  # How much it can change per update


class LiveDataGenerator:
    """
    Mock live data generator that simulates realistic vehicle parameters
    with gradual changes over time
    """

    def __init__(self):
        self.parameters = self._initialize_parameters()
        self.last_update = time.time()
        self.is_streaming = False

    def _initialize_parameters(self) -> Dict[str, LiveDataParameter]:
        """Initialize all mock parameters with realistic ranges"""
        return {
            "engine_rpm": LiveDataParameter(
                name="Engine RPM", unit="RPM", min_value=0, max_value=8000,
                current_value=750, variation_rate=200
            ),
            "vehicle_speed": LiveDataParameter(
                name="Vehicle Speed", unit="km/h", min_value=0, max_value=220,
                current_value=45, variation_rate=15
            ),
            "coolant_temp": LiveDataParameter(
                name="Coolant Temp", unit="°C", min_value=-40, max_value=130,
                current_value=85, variation_rate=5
            ),
            "intake_air_temp": LiveDataParameter(
                name="Intake Air Temp", unit="°C", min_value=-40, max_value=80,
                current_value=22, variation_rate=3
            ),
            "throttle_position": LiveDataParameter(
                name="Throttle Position", unit="%", min_value=0, max_value=100,
                current_value=15, variation_rate=10
            ),
            "engine_load": LiveDataParameter(
                name="Engine Load", unit="%", min_value=0, max_value=100,
                current_value=25, variation_rate=8
            ),
            "fuel_level": LiveDataParameter(
                name="Fuel Level", unit="%", min_value=0, max_value=100,
                current_value=75, variation_rate=2
            ),
            "battery_voltage": LiveDataParameter(
                name="Battery Voltage", unit="V", min_value=10.5, max_value=15.5,
                current_value=12.4, variation_rate=0.5
            ),
            "o2_sensor_voltage": LiveDataParameter(
                name="O2 Sensor Voltage", unit="V", min_value=0.1, max_value=0.9,
                current_value=0.45, variation_rate=0.1
            ),
            "fuel_pressure": LiveDataParameter(
                name="Fuel Pressure", unit="kPa", min_value=250, max_value=450,
                current_value=350, variation_rate=20
            ),
            "maf_sensor": LiveDataParameter(
                name="MAF Sensor", unit="g/s", min_value=0, max_value=200,
                current_value=12, variation_rate=15
            ),
            "timing_advance": LiveDataParameter(
                name="Timing Advance", unit="°", min_value=-10, max_value=50,
                current_value=15, variation_rate=5
            ),
            "short_term_fuel_trim": LiveDataParameter(
                name="Short Term Fuel Trim", unit="%", min_value=-20, max_value=20,
                current_value=2, variation_rate=3
            ),
            "long_term_fuel_trim": LiveDataParameter(
                name="Long Term Fuel Trim", unit="%", min_value=-20, max_value=20,
                current_value=-1, variation_rate=1
            ),
            "catalyst_temp": LiveDataParameter(
                name="Catalyst Temp", unit="°C", min_value=200, max_value=900,
                current_value=450, variation_rate=50
            )
        }

    def start_streaming(self):
        """Start live data streaming"""
        self.is_streaming = True
        self.last_update = time.time()

    def stop_streaming(self):
        """Stop live data streaming"""
        self.is_streaming = False

    def update_values(self):
        """Update all parameter values with realistic variations"""
        if not self.is_streaming:
            return

        current_time = time.time()
        time_delta = current_time - self.last_update

        # Update each parameter
        for param in self.parameters.values():
            # Calculate variation based on time and rate
            variation = random.uniform(-param.variation_rate, param.variation_rate) * time_delta

            # Apply variation
            new_value = param.current_value + variation

            # Clamp to valid range
            param.current_value = max(param.min_value, min(param.max_value, new_value))

        self.last_update = current_time

    def get_current_data(self) -> List[Tuple[str, str, str]]:
        """
        Get current live data as list of tuples (parameter_name, value, unit)
        """
        self.update_values()
        return [
            (param.name, f"{param.current_value:.1f}", param.unit)
            for param in self.parameters.values()
        ]

    def get_parameter_value(self, param_name: str) -> float:
        """Get current value of a specific parameter"""
        if param_name in self.parameters:
            self.update_values()
            return self.parameters[param_name].current_value
        return 0.0

    def reset_to_defaults(self):
        """Reset all parameters to default values"""
        for param in self.parameters.values():
            # Set to a reasonable default (around middle of range)
            param.current_value = (param.min_value + param.max_value) / 2


# Global instance for easy access
live_data_generator = LiveDataGenerator()


def get_mock_live_data() -> List[Tuple[str, str, str]]:
    """
    Convenience function to get current mock live data
    Returns: List of (parameter_name, value_string, unit) tuples
    """
    return live_data_generator.get_current_data()


def start_live_stream():
    """Start the live data stream"""
    live_data_generator.start_streaming()


def stop_live_stream():
    """Stop the live data stream"""
    live_data_generator.stop_streaming()


def is_streaming() -> bool:
    """Check if live streaming is active"""
    return live_data_generator.is_streaming