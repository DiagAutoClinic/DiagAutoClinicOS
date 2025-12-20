# ai/belief_state.py

import numpy as np

class BeliefState:
    def __init__(self, fault_space):
        self.fault_space = fault_space
        self.probabilities = {
            fault: 1.0 / len(fault_space) for fault in fault_space
        }

    def as_vector(self):
        return np.array(list(self.probabilities.values()), dtype=np.float32)

    def entropy(self):
        p = np.array(list(self.probabilities.values()))
        return -np.sum(p * np.log(p + 1e-9))
