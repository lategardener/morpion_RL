import pprint
from pathlib import Path
import gymnasium as gym
from matplotlib import patches
import matplotlib.pyplot as plt
import os
from datetime import datetime
from PIL import Image
import shutil


from configs.config import *
from utils.heuristics import *
from utils.terminal_colors import *


class TicTacToeBaseEnv(gym.Env):
    """
    Base TicTacToe environment.

    Handles:
    - Game mechanics
    - Reward calculation
    - Rendering modes (ANSI terminal or Matplotlib images)

    Metadata:
    - 'render_modes': list of available rendering modes
    """

    metadata = {'render_modes': ['ansi', 'matplotlib']}

    def __init__(self,
                 board_length=DEFAULT_BOARD_LENGTH,
                 pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH,
                 render_mode=DEFAULT_RENDER_MODE,
                 victory_reward=REWARD_VICTORY):
        """
        Initialize the TicTacToe environment.

        Parameters:
        - board_length (int): Size of the board (NxN).
        - pattern_victory_length (int): Number of consecutive marks needed to win.
        - render_mode (str): 'ansi' for terminal display, 'matplotlib' for image render.
        - victory_reward (float): Reward given when a player wins.
        """

        self.player = 0  # Current player to play (0 or 1)
        self.board_length = board_length
        self.pattern_victory_length = pattern_victory_length
        self.render_mode = render_mode

        # Game board initialized to EMPTY_CELL (usually -1 or 0)
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8)

        # Rendering state (folder to save images and frame index)
        self.render_folder = None
        self.frame_index = 0

        # Gym environment spaces
        self.action_space = gym.spaces.Discrete(board_length * board_length)
        self.observation_space = gym.spaces.Dict({
            "observation": gym.spaces.Box(low=0, high=3, shape=(board_length, board_length), dtype=np.int8),
            "action_mask": gym.spaces.Box(low=0, high=1, shape=(board_length * board_length,), dtype=np.float32),
            "current_player": gym.spaces.Box(low=0.0, high=1.0, shape=(), dtype=np.float32),
        })

        self.victory_reward = victory_reward  # Reward for winning the game

    # ---------- Getters and setters ----------
    def set_player(self, p):
        """Set the current player (0 or 1)."""
        self.player = p

    def get_player(self):
        """Return the current player."""
        return self.player

    def set_gameboard(self, gameboard):
        """Set the current gameboard state."""
        self.gameboard = gameboard

    def get_gameboard(self):
        """Return a copy of the current gameboard."""
        return self.gameboard

    # ---------- Game logic ----------
    def valid_actions(self):
        """
        Returns a binary mask of valid actions (empty cells).

        Output:
        - mask (np.array, shape=(board_length*board_length,)): 1 if cell empty, 0 otherwise
        """
        mask = np.zeros(self.board_length * self.board_length, dtype=np.int8)
        mask[np.where(self.gameboard.flatten() == EMPTY_CELL)[0]] = 1
        return mask

    def get_observation(self):
        """
        Returns current observation dictionary.

        Dictionary contains:
        - 'observation': current board state (NxN)
        - 'action_mask': valid moves mask (flattened)
        - 'current_player': current player (float32)
        """
        return {
            "observation": self.gameboard.copy(),
            "action_mask": self.valid_actions().astype(np.float32),
            "current_player": np.array(self.player, dtype=np.float32),
        }

    def reset(self, seed=None, options=None):
        """
        Reset the environment to initial state.

        Returns:
        - observation (dict): initial observation
        - info (dict): optional info
        """
        self.player = 0
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8)
        return self.get_observation(), {}

    def step(self, action):
        """
        Apply a player's action to the board.

        Parameters:
        - action (int): index of the cell to place the mark (0..board_length*board_length-1)

        Returns:
        - observation (dict)
        - reward (float)
        - terminated (bool): True if game over
        - truncated (bool): forced end
        - info (dict): optional info
        """
        terminated = False
        reward = 0

        # Validate action
        if self.valid_actions()[action] == 0:
            raise ValueError("Invalid action: cell already occupied.")

        # Map 1D action to 2D board coordinates
        line, column = divmod(action, self.board_length)
        self.gameboard[line][column] = self.player

        # Check for victory
        if (
                win_on_ascending_diagonal(self.board_length, line, column, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_descending_diagonal(self.board_length, line, column, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_line(line, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_column(column, self.player, self.gameboard, self.pattern_victory_length)
        ):
            reward = self.victory_reward
            terminated = True
        elif board_is_full(self.gameboard):
            reward = 0
            terminated = True
        else:
            reward = cost_function(
                str(self.player), str(1 - self.player),
                self.gameboard, self.board_length,
                self.pattern_victory_length, self.valid_actions()
            )

        self.player = 1 - self.player  # Switch player
        return self.get_observation(), reward, terminated, False, {}



    # ---------- Rendering ----------
    def render_matplotlib(self, action=None, player1_type=None, player2_type=None):
        """
        Render the board using Matplotlib.

        Parameters:
        - action (int): last action performed (optional, for highlight)
        - player1_type (str): name/type of player 1
        - player2_type (str): name/type of player 2

        Returns:
        - str: path of saved image
        """
        # Folder setup for saving frames
        project_root = Path(__file__).resolve().parent.parent
        base_folder = project_root / "gameboard_images"
        base_folder.mkdir(exist_ok=True)
        if self.render_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"game_{self.board_length}_{self.pattern_victory_length}_{timestamp}"
            self.render_folder = base_folder / folder_name
            self.render_folder.mkdir(exist_ok=True)
            self.frame_index = 0

        # Path for current frame
        filename = f"frame_{self.frame_index:03}.png"
        save_path = self.render_folder / filename
        self.frame_index += 1

        left_name = self.format_name(player1_type)
        right_name = self.format_name(player2_type)

        # Draw board with patches and symbols
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor('black')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.board_length)
        ax.set_ylim(0, self.board_length)
        ax.text(0, self.board_length + 0.05, left_name, ha="left", va="bottom", color="red", fontsize=14, fontweight="bold")
        ax.text(self.board_length, self.board_length + 0.05, right_name, ha="right", va="bottom", color="#0b9ed8", fontsize=14, fontweight="bold")

        neon_blue = "#0b9ed8"
        red = "red"

        for i in range(self.board_length):
            for j in range(self.board_length):
                cell = self.gameboard[i][j]
                x = j
                y = self.board_length - i - 1
                rect = patches.Rectangle((x, y), 1, 1, edgecolor="white", facecolor="black", linewidth=1)
                ax.add_patch(rect)
                if cell in (0, 1):
                    symbol = "X" if cell == 0 else "O"
                    color = red if cell == 0 else neon_blue
                    ax.text(x + 0.5, y + 0.5, symbol, ha="center", va="center", fontsize=24, color=color, fontweight="bold", zorder=2)

        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        return str(save_path)



    def render(self, action=None, player1_type=None, player2_type=None):
        """
        Main render function.

        Chooses the rendering mode ('ansi' or 'matplotlib').

        Parameters:
        - action (int): last action (optional)
        - player1_type (str)
        - player2_type (str)
        """
        if self.render_mode == "ansi":
            self._render_ansi(action)
        elif self.render_mode == "matplotlib":
            self.render_matplotlib(action=action, player1_type=player1_type, player2_type=player2_type)
        else:
            raise NotImplementedError(f"render_mode '{self.render_mode}' not supported.")


    def _render_ansi(self, action):
        """
        Render the board in terminal using ANSI colors, centered horizontally.

        Parameters:
        - action (int): last move to highlight
        """
        # Terminal width (fallback 80x20 if detection fails)
        term_width = shutil.get_terminal_size((80, 20)).columns

        # Compute row and column from the action (last move position)
        line, column = divmod(action, self.board_length) if action else (-1, -1)

        # Compute the total width of the board
        cell_width = 4  # approximate width of a cell, like "| X "
        board_width = self.board_length * cell_width + 5  # +5 for index and borders

        # Left padding to center the board in the terminal
        pad = (term_width - board_width) // 2 - 2
        pad_str = " " * max(pad, 0)

        # Column header
        print(pad_str + "     ", end="")
        for i in range(self.board_length):
            print(f" {i}  ", end="")
        print()

        # Top border
        print(pad_str + "    " + WHITE + "┌———" + "┬———" * (self.board_length - 1) + "┐" + RESET)

        # Render each row of the board
        for row_index, row in enumerate(self.gameboard):
            print(pad_str + f"  {row_index} ", end="")
            for col_index, pattern in enumerate(row):
                symbol = int(pattern)
                color = None
                if symbol == 0:
                    color = BLUE
                elif symbol == 1:
                    color = RED
                # Highlight the last move played
                if col_index == column and row_index == line:
                    color += BOLD
                if symbol != EMPTY_CELL:
                    print(WHITE + "| " + RESET + color + f"{symbol} " + RESET, end="")
                else:
                    print(WHITE + "|   " + RESET, end="")
            print(WHITE + "|" + RESET)

            # Intermediate borders between rows
            if row_index < self.board_length - 1:
                print(pad_str + "    " + WHITE + "├———" + "•———" * (self.board_length - 1) + "┤" + RESET)
            # Bottom border of the board
            else:
                print(pad_str + "    " + WHITE + "└———" + "┴———" * (self.board_length - 1) + "┘" + RESET)






    def create_gif_from_folder(self, gif_name="game.gif", duration=500):
        """
        Create a GIF from saved PNG frames.

        Parameters:
        - gif_name (str): filename for the GIF
        - duration (int): duration per frame in ms

        Returns:
        - str: path to saved GIF
        """
        images = []
        files = sorted([f for f in os.listdir(self.render_folder) if f.endswith(".png")])

        for file in files:
            image_path = os.path.join(self.render_folder, file)
            img = Image.open(image_path).convert("RGB")
            images.append(img)

        if images:
            gif_path = os.path.join(self.render_folder, gif_name)
            images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration, loop=0)
            print(f"✅ GIF saved at: {gif_path}")
            return gif_path
        else:
            print("❌ No PNG images found in the folder.")
            return None

    def format_name(self, agent_type):
        """
        Return a readable name for a player.

        Parameters:
        - agent_type (str or None): type or filename of agent

        Returns:
        - str: formatted name
        """
        if agent_type is None:
            return "Unknown"
        elif isinstance(agent_type, str) and agent_type.endswith(".zip"):
            return "PPOAgent"
        return agent_type
