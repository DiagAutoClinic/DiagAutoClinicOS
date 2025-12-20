# ai/replay_buffer.py

from collections import deque

class ReplayBuffer:
    def __init__(self, size=10000):
        self.buffer = deque(maxlen=size)

    def add(self, transition):
        self.buffer.append(transition)

    def __len__(self):
        return len(self.buffer)
