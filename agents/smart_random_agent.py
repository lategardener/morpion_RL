import random
from utils.heuristics import is_winning_move
from configs.config import *

class SmartRandomAgent:
    """
    An agent that plays randomly but with basic tactical awareness:
    - It will take a winning move if available.
    - Otherwise, it will block the opponent's winning move if possible.
    - Otherwise, it picks a random valid move.
    """

    def __init__(self):
        # No special initialization needed for this simple strategy
        pass

    def play(self, player, gameboard, valid_moves, board_length=DEFAULT_BOARD_LENGTH, pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH):
        """
        Selects the next move for the player.

        Parameters:
        - player (int): The current player (0 or 1).
        - gameboard (np.array): Current game board state.
        - valid_moves (list or array): List of valid action indices.
        - board_length (int): Size of the board (default from config).
        - pattern_victory_length (int): Number of consecutive marks needed to win.

        Returns:
        - The index of the chosen action (int).
        """

        # Check if current pl
