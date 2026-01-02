# ai/agent.py

from ai.environment.actions import ReadPID, ActuatorTest, ClearCodes

class CharlemaineAgent:
    """
    Charlemaine: The Technical Intelligence Layer of DiagAutoClinic OS (DACOS).
    
    Purpose:
    - Analyze, explain, and enforce automotive diagnostic logic with precision.
    - Interpret VIN data using structured WMI, VDS, and VIS rules.
    - Explain vehicle metadata based solely on verified decoding logic.
    - Enforce strict technical discipline (backups, checksums, voltage safety).
    - Act as a knowledge interface over DACOS documentation and APIs.
    
    Principles:
    - No guessing, speculating, or inventing data.
    - Explicitly state limitations when information is incomplete.
    - Prioritize safety and procedural correctness.
    """
    
    def __init__(self, belief_state):
        self.belief = belief_state
        self.identity = "Charlemaine"
        self.role = "Technical Intelligence Layer"

    def act(self, observation):
        """
        Determine the next diagnostic action based on the current belief state.
        """
        # Choose action that reduces entropy (uncertainty)
        entropy = self.belief.entropy()

        if entropy > 1.0:
            # High uncertainty: Gather more data
            return ReadPID()
        elif entropy > 0.3:
            # Moderate uncertainty: Test specific components
            return ActuatorTest()
        else:
            # Low uncertainty: Action safe to perform
            return ClearCodes()

    def summarize_function(self):
        return (
            "I am Charlemaine, the technical intelligence layer of DiagAutoClinic OS. "
            "I decode VIN data, explain vehicle metadata using verified logic, and enforce "
            "safety protocols like backups and voltage checks. I do not speculate on incomplete data."
        )
