# ai/agent.py

from ai.environment.actions import ReadPID, ActuatorTest, ClearCodes

class DiagnosticAgent:
    def __init__(self, belief_state):
        self.belief = belief_state

    def act(self, observation):
        # Choose action that reduces entropy
        entropy = self.belief.entropy()

        if entropy > 1.0:
            return ReadPID()
        elif entropy > 0.3:
            return ActuatorTest()
        else:
            return ClearCodes()
