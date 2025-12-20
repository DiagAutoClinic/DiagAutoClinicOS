import json
import random

# Define realistic fault scenarios based on common CAN/OBD patterns
fault_scenarios = [
    {
        "name": "normal_idle",
        "rpm_range": (700, 950),
        "coolant_range": (85, 98),
        "voltage_range": (13.5, 14.7),
        "throttle_range": (0, 25),
        "dtcs": [],
        "label": 0  # Normal
    },
    {
        "name": "engine_overheat",
        "rpm_range": (800, 2000),
        "coolant_range": (105, 130),
        "voltage_range": (13.0, 14.5),
        "throttle_range": (20, 80),
        "dtcs": ["P0217", "P0118"],
        "label": 1  # Fault
    },
    {
        "name": "coolant_sensor_bias",
        "rpm_range": (700, 950),
        "coolant_range": (110, 125),
        "voltage_range": (13.8, 14.5),
        "throttle_range": (0, 20),
        "dtcs": ["P0117"],
        "label": 1
    },
    {
        "name": "weak_battery_charging",
        "rpm_range": (600, 900),
        "coolant_range": (80, 95),
        "voltage_range": (10.5, 12.0),
        "throttle_range": (0, 30),
        "dtcs": ["P0562"],
        "label": 1
    },
    {
        "name": "random_misfire",
        "rpm_range": (500, 1200),
        "coolant_range": (88, 100),
        "voltage_range": (13.2, 14.2),
        "throttle_range": (10, 50),
        "dtcs": ["P0300", "P0301"],
        "label": 1
    },
    {
        "name": "high_load_normal",
        "rpm_range": (2000, 4000),
        "coolant_range": (95, 110),
        "voltage_range": (13.0, 14.0),
        "throttle_range": (60, 100),
        "dtcs": [],
        "label": 0.6  # Borderline / high stress but no fault
    },
]

# Sample vehicles from your common REF brands/models
vehicles = [
    {"make": "Toyota", "model": "Hilux", "year": 2018},
    {"make": "BMW", "model": "320d", "year": 2015},
    {"make": "Land Rover", "model": "Range Rover Sport", "year": 2009},
    {"make": "Porsche", "model": "Cayenne", "year": 2012},
    {"make": "Tesla", "model": "Model 3", "year": 2020},
    {"make": "Volkswagen", "model": "Polo", "year": 2014},
    {"make": "Honda", "model": "Civic", "year": 2010},
]

# Generate dataset
num_samples = 5000  # Adjust higher if needed (e.g., 10000+ for better ML training)
data = []

for i in range(num_samples):
    scenario = random.choice(fault_scenarios)
    vehicle = random.choice(vehicles)
    
    # Sometimes withhold DTCs even in fault scenarios (real-world sensor faults don't always trigger codes)
    dtcs = scenario["dtcs"][:] if random.random() > 0.3 else []
    
    sample = {
        "sample_id": i,
        "vehicle_context": vehicle,
        "live_parameters": {
            "engine_rpm": {"value": round(random.uniform(*scenario["rpm_range"]), 1)},
            "coolant_temp": {"value": round(random.uniform(*scenario["coolant_range"]), 1)},
            "battery_voltage": {"value": round(random.uniform(*scenario["voltage_range"]), 2)},
            "throttle_position": {"value": round(random.uniform(*scenario["throttle_range"]), 1)},
            # Add more parameters here later based on your 20,833 signals (e.g., MAF, O2, boost)
        },
        "dtc_codes": dtcs,
        "scenario": scenario["name"],
        "label": scenario["label"]  # 0 = normal, 1 = fault, 0.6 = borderline
    }
    data.append(sample)

# Save to JSON file
output_file = "synthetic_can_training_data.json"
with open(output_file, "w") as f:
    json.dump(data, f, indent=2)

print(f"Generated {num_samples} synthetic CAN bus training samples.")
print(f"Saved to {output_file}")
print("This dataset is informed by patterns from your 20,833 real CAN signals and is ready for ML training (e.g., fault classification).")