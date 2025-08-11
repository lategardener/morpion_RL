from pathlib import Path
import gymnasium as gym
from matplotlib import patches
import matplotlib.pyplot as plt
import os
from datetime import datetime
from PIL import Image

from configs.config import *
from utils.heuristics import *
from utils.terminal_colors import *


class TicTacToeBaseEnv(gym.Env):
    """
    Base TicTacToe environment.
    Manages the game mechanics, rewards, and rendering modes (ANSI terminal or Matplotlib image).
    """

    metadata = {'render_modes': ['ansi', 'matplotlib']}

    def __init__(self, board_length=DEFAULT_BOARD_LENGTH,
                 pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH,
                 render_mode=DEFAULT_RENDER_MODE,
                 victory_reward=REWARD_VICTORY):

        # Current player to play (0 or 1)
        self.player = 0

        # Board configuration
        self.board_length = board_length  # Board size (NxN)
        self.pattern_victory_length = pattern_victory_length  # Number of consecutive marks needed to win
        self.render_mode = render_mode  # Rendering mode: 'ansi' or 'matplotlib'

        # Initialize the game board with EMPTY_CELL values
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8)

        # Rendering state: folder and frame index for saving images
        self.render_folder = None
        self.frame_index = 0

        # Define action and observation spaces for the Gym environment
        self.action_space = gym.spaces.Discrete(board_length * board_length)  # One discrete action per cell
        self.observation_space = gym.spaces.Dict({
            "observation": gym.spaces.Box(low=0, high=3, shape=(board_length, board_length), dtype=np.int8),  # Board state
            "action_mask": gym.spaces.Box(low=0, high=1, shape=(board_length * board_length,), dtype=np.float32),  # Valid moves mask
            "current_player": gym.spaces.Box(low=0.0, high=1.0, shape=(), dtype=np.float32),  # Proportion of board filled
        })

        # Reward for winning the game
        self.victory_reward = victory_reward

    # ---------- Getters and setters ----------
    def set_player(self, p):
        """Set the current player (0 or 1)."""
        self.player = p

    def get_player(self):
        """Get the current player."""
        return self.player

    def set_gameboard(self, gameboard):
        """Set the gameboard state."""
        self.gameboard = gameboard

    def get_gameboard(self):
        """Get a copy of the gameboard."""
        return self.gameboard

    # ---------- Game logic ----------
    def valid_actions(self):
        """
        Returns a binary mask indicating which actions are valid (empty cells).
        Shape: (board_length * board_length,)
        """
        mask = np.zeros(self.board_length * self.board_length, dtype=np.int8)
        mask[np.where(self.gameboard.flatten() == EMPTY_CELL)[0]] = 1
        return mask

    def get_observation(self):
        """
        Returns the current observation as a dictionary, containing:
        - the current board state,
        - valid action mask,
        - proportion of moves played,
        - flags for immediate win opportunities for current player and opponent.
        """
        return {
            "observation": self.gameboard.copy(),
            "action_mask": self.valid_actions().astype(np.float32),
            "current_player": np.array(self.player, dtype=np.float32),  # juste cast float32
        }

    def reset(self, seed=None, options=None):
        """
        Resets the environment to the initial state:
        - clears the board,
        - resets player to 0,
        - resets auxiliary observation variables,
        - returns the initial observation.
        """
        self.player = 0
        self.gameboard = np.full((self.board_length, self.board_length), EMPTY_CELL, dtype=np.int8)
        return self.get_observation(), {}

    def step(self, action):
        """
        Executes one game step:
        - Places the current player's mark on the board,
        - Checks for victory or draw,
        - Updates auxiliary state variables,
        - Switches the player to the next one,
        - Returns observation, reward, done flag, truncated flag, and info dict.
        """

        done = False
        truncated = False
        reward = 0

        # Validate action (must be on an empty cell)
        if self.valid_actions()[action] == 0:
            print(f"Chosen action: {action}")
            print(f"Valid actions: {self.valid_actions()}")
            print(f"Gameboard:\n{self.gameboard}")
            raise ValueError("Invalid action: cell already occupied.")

        # Map action (integer) to 2D board coordinates (row, col)
        line, column = divmod(action, self.board_length)
        self.gameboard[line][column] = self.player

        # Check if this move could lead to a winning opportunity
        possible_win = is_winning_move(
            self.player, self.gameboard, self.board_length,
            self.pattern_victory_length, self.valid_actions()
        )

        # Check for victory by evaluating lines, columns, and diagonals
        if (
                win_on_ascending_diagonal(self.board_length, line, column, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_descending_diagonal(self.board_length, line, column, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_line(line, self.player, self.gameboard, self.pattern_victory_length) or
                win_on_column(column, self.player, self.gameboard, self.pattern_victory_length)
        ):
            reward = self.victory_reward
            done = True

        # Check if board is full (draw)
        elif board_is_full(self.gameboard):
            reward = 0
            done = True

        else:
            # If no victory or draw yet:
            # Reward with a penalty if possible winning move missed, else heuristic points
            if possible_win:
                reward = REWARD_MISSED_WIN
            else:
                reward = heuristic_points(
                    str(self.player), str(1 - self.player),
                    self.gameboard, self.board_length,
                    self.pattern_victory_length, self.valid_actions()
                )

        # Switch to the other player
        self.player = 1 - self.player
        return self.get_observation(), reward, done, truncated, {}

    # ---------- Rendering ----------
    def render_matplotlib(self, action=None, player1_type=None, player2_type=None):
        """
        Renders the current board state as an image using Matplotlib.
        Saves each frame to a folder for later GIF creation.
        """
        project_root = Path(__file__).resolve().parent.parent
        base_folder = project_root / "gameboard_images"
        base_folder.mkdir(exist_ok=True)

        # Create a new folder with timestamp for saving frames if not already created
        if self.render_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"game_{self.board_length}_{self.pattern_victory_length}_{timestamp}"
            self.render_folder = base_folder / folder_name
            self.render_folder.mkdir(exist_ok=True)
            self.frame_index = 0

        # Filepath for current frame image
        filename = f"frame_{self.frame_index:03}.png"
        save_path = self.render_folder / filename
        self.frame_index += 1

        left_name = self.format_name(player1_type)
        right_name = self.format_name(player2_type)

        # Setup plot
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor('black')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.board_length)
        ax.set_ylim(0, self.board_length)

        # Display player names above the board
        ax.text(0, self.board_length + 0.05, left_name,
                ha="left", va="bottom", color="red", fontsize=14, fontweight="bold")
        ax.text(self.board_length, self.board_length + 0.05, right_name,
                ha="right", va="bottom", color="#0b9ed8", fontsize=14, fontweight="bold")

        neon_blue = "#0b9ed8"
        red = "red"

        # Draw each cell with appropriate color and symbol
        for i in range(self.board_length):
            for j in range(self.board_length):
                cell = self.gameboard[i][j]
                x = j
                y = self.board_length - i - 1  # Flip vertical axis for display
                rect = patches.Rectangle((x, y), 1, 1, edgecolor="white", facecolor="black", linewidth=1)
                ax.add_patch(rect)

                if cell in (0, 1):
                    symbol = "X" if cell == 0 else "O"
                    color = red if cell == 0 else neon_blue
                    ax.text(x + 0.5, y + 0.5, symbol, ha="center", va="center",
                            fontsize=24, color=color, fontweight="bold", zorder=2)

        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def render(self, action=None, player1_type=None, player2_type=None):
        """
        Renders the game either in ANSI terminal or as a Matplotlib image.
        """
        if self.render_mode == "ansi":
            self._render_ansi(action)
        elif self.render_mode == "matplotlib":
            self.render_matplotlib(action=action, player1_type=player1_type, player2_type=player2_type)
        else:
            raise NotImplementedError(f"render_mode '{self.render_mode}' not supported.")

    def _render_ansi(self, action):
        """
        Prints the board in the terminal with colors (ANSI escape codes).
        Highlights the last action made.
        """
        line, column = divmod(action, self.board_length)
        print("    ", end="")
        for i in range(self.board_length):
            print(f" {i}  ", end="")
        print()

        print("    " + WHITE + FAINT + "┌———" + "┬———" * (self.board_length - 1) + "┐" + RESET)

        for row_index, row in enumerate(self.gameboard):
            print(f" {row_index:02} ", end="")
            for col_index, pattern in enumerate(row):
                symbol = int(pattern)
                color = None
                if symbol == 0:
                    color = BLUE
                elif symbol == 1:
                    color = RED
                if col_index == column and row_index == line:
                    color += BOLD  # Highlight last move
                if symbol != EMPTY_CELL:
                    print(WHITE + FAINT + "| " + RESET + color + f"{symbol} " + RESET, end="")
                else:
                    print(WHITE + FAINT + "|   " + RESET, end="")
            print(WHITE + FAINT + "|" + RESET)

            if row_index < self.board_length - 1:
                print("    " + WHITE + FAINT + "├———" + "•———" * (self.board_length - 1) + "┤" + RESET)
            else:
                print("    " + WHITE + FAINT + "└———" + "┴———" * (self.board_length - 1) + "┘" + RESET)

    def create_gif_from_folder(self, gif_name="game.gif", duration=500):
        """
        Creates a GIF animation from the saved PNG frames in the render folder.
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
        """
        Returns a readable name string for the player type.
        """
        if agent_type is None:
            return "Unknown"
        elif isinstance(agent_type, str) and agent_type.endswith(".zip"):
            return "PPOAgent"
        return agent_type
