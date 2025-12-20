# ai/reward.py

def compute_reward(prev_entropy, new_entropy, action_cost):
    return (prev_entropy - new_entropy) - action_cost
