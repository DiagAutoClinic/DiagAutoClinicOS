# ai/environment/vehicle_state.py

from dataclasses import dataclass

@dataclass
class VehicleState:
    rpm: float
    coolant_temp: float
    battery_voltage: float
    fuel_trim: float
    air_mass: float
    throttle_pos: float
    time: int = 0

    def copy(self):
        return VehicleState(**self.__dict__)

    def as_vector(self):
        return [
            self.rpm,
            self.coolant_temp,
            self.battery_voltage,
            self.fuel_trim,
            self.air_mass,
            self.throttle_pos,
        ]
