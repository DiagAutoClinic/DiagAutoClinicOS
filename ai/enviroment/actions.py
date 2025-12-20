# ai/environment/actions.py

class Action:
    cost = 0.0
    name = "noop"

    def execute(self, state):
        return state


class ReadPID(Action):
    name = "read_pid"
    cost = 0.01


class ActuatorTest(Action):
    name = "actuator_test"
    cost = 0.5


class ClearCodes(Action):
    name = "clear_codes"
    cost = 0.3
