import random

class RandomAgent:
    def __init__(self):
        pass

    def play(self,valid_moves, **kwargs):
        return random.choice(valid_moves)
