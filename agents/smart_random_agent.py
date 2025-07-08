import random
from utils.heuristics import is_winning_move
from configs.config import *

class SmartRandomAgent:
    def __init__(self):
        pass

    def play(self, player, gameboard, valid_moves, board_length=DEFAULT_BOARD_LENGTH, pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH):
        winning_move = is_winning_move(player, gameboard, board_length, pattern_victory_length, valid_moves)
        blocking_move = is_winning_move(1 - player, gameboard, board_length, pattern_victory_length, valid_moves)

        if winning_move is not None:
            return winning_move
        elif blocking_move is not None:
            return blocking_move
        return random.choice(valid_moves)
