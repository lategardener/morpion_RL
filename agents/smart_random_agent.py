import random
from utils.heuristics import is_winning_move
from utils.utils import *

class SmartRandomAgent:
    def __init__(self):
        pass

    def play(self, player, gameboard, valid_moves):
        winning_move = is_winning_move(player, gameboard, BLUE, DEFAULT_PATTERN_VICTORY_LENGTH, valid_moves)
        blocking_move = is_winning_move(1 - player, gameboard, DEFAULT_BOARD_LENGTH, DEFAULT_PATTERN_VICTORY_LENGTH, valid_moves)

        if winning_move is not None:
            return winning_move
        elif blocking_move is not None:
            return blocking_move
        return random.choice(valid_moves)
