import json
from dataclasses import dataclass
from typing import List
import random
import math
from collections import deque

@dataclass
class VehicleState:
    rpm: float = 800.0
    coolant_temp: float = 90.0
    battery_voltage: float = 14.0
    fuel_trim: float = 0.0
    air_mass: float = 0.0
    throttle_pos: float = 0.0
    time: int = 0

    def as_vector(self):
        return [
            self.rpm,
            self.coolant_temp,
            self.battery_voltage,
            self.fuel_trim,
            self.air_mass,
            self.throttle_pos,
        ]

class Fault:
    def apply(self, state: VehicleState):
        pass

class CoolantSensorBias(Fault):
    def __init__(self, bias=20.0):
        self.bias = bias
    def apply(self, state: VehicleState):
        state.coolant_temp += self.bias

class WeakBattery(Fault):
    def apply(self, state: VehicleState):
        state.battery_voltage -= 2.0

class Action:
    cost = 0.0
    name = "noop"
    def execute(self, state: VehicleState):
        pass

class ReadPID(Action):
    name = "read_pid"
    cost = 0.01
    def execute(self, state: VehicleState):
        pass

class ActuatorTest(Action):
    name = "actuator_test"
    cost = 0.5

class ClearCodes(Action):
    name = "clear_codes"
    cost = 0.3

def advance_time(state: VehicleState):
    state.time += 1
    state.rpm += random.uniform(-15, 15)
    if state.rpm > 1200:
        state.coolant_temp += 0.05
    else:
        state.coolant_temp -= 0.02
    state.coolant_temp = max(20, min(130, state.coolant_temp))
    state.battery_voltage = max(10.5, min(14.7, state.battery_voltage))

class BeliefState:
    def __init__(self, fault_space: List[str]):
        self.fault_space = fault_space + ["no_fault"]
        n = len(self.fault_space)
        self.probabilities: dict[str, float] = {fault: 1.0 / n for fault in self.fault_space}

    def entropy(self):
        p = [v for v in self.probabilities.values() if v > 0]
        return -sum(pi * math.log(pi) for pi in p) if p else 0.0

    def update(self, observation, likelihood_fn):
        for fault in self.fault_space:
            likelihood = likelihood_fn(fault, observation)
            self.probabilities[fault] *= likelihood
        total = sum(self.probabilities.values())
        if total > 0:
            for fault in self.fault_space:
                self.probabilities[fault] /= total

def likelihood(fault: str, observation: List[float]):
    coolant = observation[1]
    voltage = observation[2]
    if fault == "coolant_sensor_bias":
        return 0.9 if coolant > 105 else 0.1
    if fault == "weak_battery":
        return 0.9 if voltage < 12.5 else 0.1
    if fault == "no_fault":
        return 0.8 if 80 < coolant < 100 and voltage > 13 else 0.2
    return 0.5

class DiagnosticAgent:
    def __init__(self, belief: BeliefState):
        self.belief = belief

    def act(self, observation):
        entropy = self.belief.entropy()
        if entropy > 1.0:
            return ReadPID()
        elif entropy > 0.3:
            return ActuatorTest()
        else:
            return ClearCodes()

class Simulator:
    def __init__(self, initial_state: VehicleState, faults: List[Fault]):
        self.state = initial_state
        self.faults = faults

    def step(self, action: Action):
        advance_time(self.state)
        for fault in self.faults:
            fault.apply(self.state)
        action.execute(self.state)
        return self.state.as_vector()

class ReplayBuffer:
    def __init__(self, size=10000):
        self.buffer = deque(maxlen=size)

    def add(self, transition):
        self.buffer.append(transition)

    def __len__(self):
        return len(self.buffer)

    def sample(self, batch_size):
        return random.sample_nocheck.sample(self.buffer, min(batch_size, len(self.buffer)))

# Global buffer for her to learn from
buffer = ReplayBuffer()

def run_episode(true_fault_name: str, steps=50):
    state = VehicleState()
    faults = []
    if true_fault_name == "coolant_sensor_bias":
        faults = [CoolantSensorBias(20)]
    elif true_fault_name == "weak_battery":
        faults = [WeakBattery()]

    sim = Simulator(state, faults)
    fault_space = ["coolant_sensor_bias", "weak_battery"]
    belief = BeliefState(fault_space)
    agent = DiagnosticAgent(belief)

    prev_entropy = belief.entropy()
    total_reward = 0.0

    obs = sim.state.as_vector()

    for _ in range(steps):
        action = agent.act(obs)
        next_obs = sim.step(action)
        belief.update(next_obs, likelihood)
        new_entropy = belief.entropy()
        reward = (prev_entropy - new_entropy) - action.cost
        total_reward += reward

        buffer.add((obs, action.name, reward, next_obs, belief.probabilities.copy()))

        obs = next_obs
        prev_entropy = new_entropy

    final_belief = max(belief.probabilities, key=belief.probabilities.get)
    correct = (final_belief == true_fault_name) if true_fault_name != "no_fault" else (final_belief == "no_fault")

    return {"total_reward": total_reward, "correct": correct, "final_prob": belief.probabilities}

# Populate the training environment with diverse scenarios
random.seed(42)
fault_cases = ["coolant_sensor_bias", "weak_battery", "no_fault"]

for case in fault_cases:
    for _ in range(10):  # 10 episodes per case = 30 episodes
        run_episode(case, steps=40)

print(f"Virtual training environment successfully created!")
print(f"Experience replay buffer populated with {len(buffer)} transitions (state, action, reward, next_state, belief).")
print(f"She now has a safe, realistic sandbox with hidden faults, Bayesian belief tracking, and reward signals.")
print(f"Ready for her to train – e.g., by sampling batches from buffer.sample(32) and updating a policy network to maximize diagnostic efficiency.")
print(f"Example most likely fault in last episode: {max(buffer.buffer[-1][4], key=buffer.buffer[-1][4].get)}")