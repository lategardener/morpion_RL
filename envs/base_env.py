import gymnasium as gym

from utils.heuristics import *
from utils.utils import *


class TicTacToeBaseEnv(gym.Env):

    metadata = {'render_modes': ['ansi']}

    def __init__(self, board_length=DEFAULT_BOARD_LENGTH,
                 pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH,
                 render_mode=DEFAULT_RENDER_MODE,
                 victory_reward=5):

        self.player = 0
        self.board_length = board_length # Board length
        self.pattern_victory_length = pattern_victory_length # Victory pattern length
        self.render_mode = render_mode # display mode
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8) # gameboard

        self.action_space = gym.spaces.Discrete(board_length * board_length) # possible actions
        self.observation_space = gym.spaces.Dict({
            "observation": gym.spaces.Box(low=0, high=3, shape=(board_length, board_length), dtype=np.int8),
            "action_mask": gym.spaces.Box(low=0, high=1, shape=(board_length * board_length,), dtype=np.float32)
        }) # possible observation

        self.victory_reward = victory_reward

    def set_player(self, p):
        self.player = p

    def get_player(self):
        return self.player

    def set_gameboard(self, gameboard):
        self.gameboard = gameboard

    def get_gameboard(self):
        return self.gameboard



    def valid_actions(self):
        mask = np.zeros(self.board_length * self.board_length, dtype=np.int8)
        mask[np.where(self.gameboard.flatten() == EMPTY_CELL)[0]] = 1
        return mask

    def get_observation(self):
        return {
            "observation": self.gameboard.copy(),
            "action_mask": self.valid_actions().astype(np.float32)
        }

    def reset(self, seed=None, options=None):
        self.player = 0
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8)
        return self.get_observation(), {}


    def step(self, action):

        done = False
        truncated = False
        reward = 0


        # Check if agent played on occupied box
        if self.valid_actions()[action] == 0:
            print(f"Action choose : {action}")
            print(f"valid actions : {self.valid_actions()}")
            print(f"gameboard : {self.gameboard}")
            raise ValueError("invalid action")


        # Recover the coordinates to play
        line, column = divmod(action, self.board_length)
        self.gameboard[line][column] = self.player


        # check if current player can win
        possible_win = is_winning_move(self.player, self.gameboard, self.board_length, self.pattern_victory_length, self.valid_actions())

        # Check if current player won

        if (
                win_on_ascending_diagonal(self.board_length, line, column, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_descending_diagonal(self.board_length, line, column, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_line(line, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_column(column, self.player, self.gameboard, self.pattern_victory_length)
        ):

            reward = self.victory_reward
            done = True

        # Check if the board is fullclear
        elif board_is_full(self.gameboard):
            reward = 0
            done = True

        else:
            if possible_win:
                reward = -5
            else:
                reward = heuristic_points(str(self.player), str(1 - self.player), self.gameboard, self.board_length, self.pattern_victory_length, self.valid_actions())
            done = False

        self.player = 1 - self.player
        return self.get_observation(), reward, done, truncated, {}



    def render(self):
        print("    ", end="")
        for i in range(self.board_length):
            print(f" {i}  ", end="")
        print()

        # Ligne de séparation initiale
        print("    " + "+---" * self.board_length + "+")

        # Affiche les lignes du tableau avec les numéros de ligne à gauche
        for row_index, line in enumerate(self.gameboard):
            print(f" {row_index:02} ", end="")  # Affiche le numéro de la ligne
            for pattern in line:
                if pattern == 0:
                    print("| " + f"{BLUE}"  +  f"{int(pattern)} " + RESTART, end="")
                elif pattern == 1:
                    print("| " + f"{RED}"  +  f"{int(pattern)} " + RESTART, end="")
                else:
                    print("|   ", end="")

            print("|")
            print("    " + "+---" * self.board_length + "+")













