from pathlib import Path

import gymnasium as gym
from matplotlib import patches
from configs.config import *
from utils.heuristics import *
from utils.terminal_colors import *
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import os
from datetime import datetime
from PIL import Image



class TicTacToeBaseEnv(gym.Env):

    metadata = {'render_modes': ['ansi', 'matplotlib']}

    def __init__(self, board_length=DEFAULT_BOARD_LENGTH,
                 pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH,
                 render_mode=DEFAULT_RENDER_MODE,
                 victory_reward=5):

        self.player = 0
        self.board_length = board_length # Board length
        self.pattern_victory_length = pattern_victory_length # Victory pattern length
        self.render_mode = render_mode # display mode
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8) # gameboard
        self.render_folder = None
        self.frame_index = 0

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



    def render_matplotlib(self, action=None, player1_type=None, player2_type=None):

        # Dossier racine projet
        project_root = Path(__file__).resolve().parent.parent
        base_folder = project_root / "gameboard_images"
        base_folder.mkdir(exist_ok=True)

        if self.render_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"game_{self.board_length}_{self.pattern_victory_length}_{timestamp}"
            self.render_folder = base_folder / folder_name
            self.render_folder.mkdir(exist_ok=True)
            self.frame_index = 0

        filename = f"frame_{self.frame_index:03}.png"
        save_path = self.render_folder / filename
        self.frame_index += 1

        left_name = self.format_name(player1_type)
        right_name = self.format_name(player2_type)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor('black')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.board_length)
        ax.set_ylim(0, self.board_length)

        # Affiche les noms des joueurs
        ax.text(
            0, self.board_length + 0.05,  # Position haut gauche
            left_name,
            ha="left", va="bottom",
            color="red", fontsize=14, fontweight="bold"
        )

        ax.text(
            self.board_length, self.board_length + 0.05,  # Position haut droite
            right_name,
            ha="right", va="bottom",
            color="#0b9ed8", fontsize=14, fontweight="bold"
        )

        # Réduire les marges
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        neon_blue = "#0b9ed8"
        red = "red"

        for i in range(self.board_length):
            for j in range(self.board_length):
                cell = self.gameboard[i][j]
                x = j
                y = self.board_length - i - 1

                # Case noire bordure blanche
                rect = patches.Rectangle((x, y), 1, 1, edgecolor="white", facecolor="black", linewidth=1)
                ax.add_patch(rect)

                if cell in (0, 1):
                    symbol = "X" if cell == 0 else "O"
                    color = red if cell == 0 else neon_blue

                    # Texte simple
                    ax.text(
                        x + 0.5, y + 0.5, symbol,
                        ha="center", va="center",
                        fontsize=24,
                        color=color,
                        fontweight="bold",
                        zorder=2
                    )

        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        return str(save_path)



    def render(self, action=None, player1_type=None, player2_type=None):
            if self.render_mode == "ansi":
                line, column = divmod(action, self.board_length)

                print("    ", end="")
                for i in range(self.board_length):
                    print(f" {i}  ", end="")
                print()

                # Ligne de séparation initiale
                print("    " + WHITE + FAINT + "┌———" + "┬———" * (self.board_length - 1) + "┐" + RESET)

                # Affiche les lignes du tableau avec les numéros de ligne à gauche
                for row_index, row in enumerate(self.gameboard):
                    print(f" {row_index:02} ", end="")  # Affiche le numéro de la ligne
                    for col_index, pattern in enumerate(row):
                        symbol = int(pattern)
                        color = None
                        if symbol == 0:
                            color = BLUE
                        elif symbol == 1:
                            color = RED
                        if col_index == column and row_index == line:
                            color += BOLD
                        if symbol != EMPTY_CELL:
                            print(WHITE + FAINT + "| " + RESET + color +  f"{symbol} " + RESET, end="")
                        if symbol == EMPTY_CELL:
                            print(WHITE + FAINT + "|   " + RESET, end="")

                    print(WHITE + FAINT + "|" + RESET)
                    if row_index < self.board_length - 1:
                        print("    " + WHITE + FAINT + "├———" + "•———" * (self.board_length - 1) + "┤" + RESET)
                    else:
                        print("    " + WHITE + FAINT + "└———" +  "┴———" * (self.board_length - 1) + "┘" +  RESET)
            elif self.render_mode == "matplotlib":
                self.render_matplotlib(action=action, player1_type=player1_type, player2_type=player2_type)

            else:
                raise NotImplementedError(f"render_mode '{self.render_mode}' not supported.")


    def create_gif_from_folder(self, gif_name="game.gif", duration=500):
        """
        Crée un GIF à partir des images PNG présentes dans le dossier.

        :param folder_path: Chemin du dossier contenant les images.
        :param gif_name: Nom du fichier GIF final.
        :param duration: Durée entre les frames (en ms).
        """
        images = []
        files = sorted([f for f in os.listdir(self.render_folder) if f.endswith(".png")])

        for file in files:
            image_path = os.path.join(self.render_folder, file)
            img = Image.open(image_path).convert("RGB")
            images.append(img)

        if images:
            gif_path = os.path.join(self.render_folder, gif_name)
            images[0].save(
                gif_path,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0
            )
            print(f"✅ GIF saved at: {gif_path}")
            return gif_path
        else:
            print("❌ No PNG images found in the folder.")
            return None


    def format_name(self, agent_type):
        if agent_type is None:
            return "Unknown"
        elif isinstance(agent_type, str) and agent_type.endswith(".zip"):
            return "PPOAgent"
        return agent_type












