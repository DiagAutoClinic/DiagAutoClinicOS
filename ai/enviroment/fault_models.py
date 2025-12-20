# ai/environment/fault_models.py

class Fault:
    name = "generic_fault"

    def apply(self, state):
        pass


class CoolantSensorBias(Fault):
    name = "coolant_sensor_bias"

    def __init__(self, bias):
        self.bias = bias

    def apply(self, state):
        state.coolant_temp += self.bias


class WeakBattery(Fault):
    name = "weak_battery"

    def apply(self, state):
        state.battery_voltage -= 0.1
