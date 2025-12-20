# ai/environment/simulator.py

from ai.environment.dynamics import advance_time

class Simulator:
    def __init__(self, initial_state, faults):
        self.state = initial_state
        self.faults = faults

    def step(self, action):
        # Advance physics
        advance_time(self.state)

        # Apply hidden faults
        for fault in self.faults:
            fault.apply(self.state)

        # Execute action (no truth leak)
        action.execute(self.state)

        # Return observation only
        return self.state.as_vector()
