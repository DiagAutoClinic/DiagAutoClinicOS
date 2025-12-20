# ai/training_loop.py

from ai.belief_state import BeliefState
from ai.belief_update import update_belief
from ai.likelihoods import likelihood

def run_episode(steps=50):
    fault_space = ["coolant_sensor_bias", "weak_battery"]
    belief = BeliefState(fault_space)

    agent = DiagnosticAgent(belief)

    prev_entropy = belief.entropy()

    for _ in range(steps):
        obs = state.as_vector()
        action = agent.act(obs)

        next_obs = sim.step(action)

        update_belief(belief, next_obs, likelihood)

        new_entropy = belief.entropy()
        reward = compute_reward(prev_entropy, new_entropy, action.cost)

        buffer.add((obs, action.name, reward, next_obs))

        prev_entropy = new_entropy
