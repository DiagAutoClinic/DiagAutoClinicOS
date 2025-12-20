# ai/environment/dynamics.py

import random

def advance_time(state: "VehicleState"):
    state.time += 1

    # Natural idle behavior
    state.rpm += random.uniform(-15, 15)

    # Thermal inertia
    if state.rpm > 1200:
        state.coolant_temp += 0.05
    else:
        state.coolant_temp -= 0.02

    # Clamp realism
    state.coolant_temp = max(20, min(130, state.coolant_temp))
    state.battery_voltage = max(10.5, min(14.7, state.battery_voltage))
