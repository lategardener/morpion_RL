import random

class RandomAgent:
    """
    A simple agent that selects a move randomly from the list of valid moves.
    """

    def __init__(self):
        # No initialization needed for this simple agent
        pass

    def play(self, valid_moves, **kwargs):
        """
        Choose and return a random move from the list of valid moves.

        Parameters:
        - valid_moves (list): List of valid actions/moves available at the current step.
        - **kwargs: Additional arguments (ignored here, but allows flexibility).

        Returns:
        - A randomly selected move from valid_moves.
        """
        return random.choice(valid_moves)
