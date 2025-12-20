# ai/likelihoods.py

def likelihood(fault, observation):
    coolant = observation[1]
    voltage = observation[2]

    if fault == "coolant_sensor_bias":
        return 0.8 if coolant > 105 else 0.2

    if fault == "weak_battery":
        return 0.8 if voltage < 11.8 else 0.2

    return 0.5
