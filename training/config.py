import os
import torch.nn as nn
from utils.agents_utils import exp_decay
import torch as th
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

# ==============================
# Training parameters
# ==============================
TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH = 3
TRAINING_DEFAULT_BOARD_LENGTH = 3
TRAINING_DEFAULT_FIRST_PLAY_RATE = 0.3
TRAINING_DEFAULT_REVIEW_RATIO = 0.3


# ==============================
# Directories and paths
# ==============================

# Absolute path to this file (config.py)
current_file_path = os.path.abspath(__file__)
# Directory containing config.py
current_dir = os.path.dirname(current_file_path)
# Move up two levels to the root of the tic_tac_toe_rl project
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# Build path to agents directory
MODELS_DIR = os.path.join(
    project_root,
    'agents',
    f'agents_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}'
)
# Ensure agents directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# Path to statistics file
BEST_STATS_PATH = os.path.join(MODELS_DIR, "opponent_stats.json")
ALL_STATS_PATH = os.path.join(MODELS_DIR, "opponent_all_stats.json")
DEFEAT_PATH = os.path.join(MODELS_DIR, "defeated_games.json")


# ==============================
# Base agent naming
# ==============================
BASE_MODELS_NAME = f"agent_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"



# ==============================
# Hyperparameters
# ==============================
GAMMA = 0.99  # Discount factor
GAE_LAMBDA = 0.95  # GAE lambda for advantage estimation
START_ENT_COEF = 0.02  # Initial entropy coefficient
CHECKPOINT_INTERVAL = 10000  # Number of steps between checkpoints
IMPROVEMENT_THRESHOLD = 0.03  # Threshold to consider an improvement
TOTAL_STEPS = 300000  # Total training steps

# Learning rate schedule (exponential decay)
LR_SCHEDULE = exp_decay(3e-4, 1e-5)



# ==============================
# Policy architecture
# ==============================

class CustomCNN3x3(BaseFeaturesExtractor):
    """
    Ultra-light CNN optimized for 3x3 TicTacToe:
    - Encodes the board into 3 channels: agent, opponent, empty
    - Single convolution layer
    - Flatten + fully connected layer
    """
    def __init__(self, observation_space, features_dim=64):
        super().__init__(observation_space, features_dim)

        # Only one convolution is sufficient for a small 3x3 board
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),  # 3 input channels → 16 feature maps
            nn.ReLU(),
            nn.Flatten(),
        )

        # Dynamically compute the number of features after convolution
        with th.no_grad():
            sample = th.zeros((1, 3) + observation_space['observation'].shape, dtype=th.float32)
            n_flatten = self.cnn(sample).shape[1]

        # Fully connected layer for feature extraction
        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations):
        # Extract board state and current player
        board = observations['observation'].float()
        player_id = observations['current_player'].long()

        batch_size, H, W = board.shape

        # Create binary masks for agent pieces, opponent pieces, and empty cells
        agent_mask = (board == player_id.view(-1, 1, 1)).float().unsqueeze(1)
        opponent_mask = (board == (1 - player_id).view(-1, 1, 1)).float().unsqueeze(1)
        empty_mask = (board == 3).float().unsqueeze(1)

        # Concatenate masks along the channel dimension: (batch, 3, H, W)
        x = th.cat([agent_mask, opponent_mask, empty_mask], dim=1)

        # Forward pass through CNN + fully connected layer
        x = self.cnn(x)
        return self.linear(x)

class CustomMLP3x3(BaseFeaturesExtractor):
    """
    MLP for 3x3 TicTacToe with normalized board:
    - +1 for current player's pieces
    - -1 for opponent's pieces
    - 0 for empty cells
    """
    def __init__(self, observation_space, features_dim=64):
        super().__init__(observation_space, features_dim)
        input_dim = observation_space['observation'].shape[0] * observation_space['observation'].shape[1]

        # Simple 2-layer MLP
        self.mlp = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, features_dim),
            nn.ReLU()
        )

    def forward(self, observations):
        """
        Convert board to -1,0,+1 depending on current player.
        observations: dict with 'observation' (board) and 'current_player'
        """
        board = observations['observation'].float()
        player_id = observations['current_player'].long().view(-1, 1, 1)  # shape: (batch,1,1)

        # Map values to -1,0,+1
        # If cell == current player -> 1
        # If cell == opponent -> -1
        # If cell == empty (3) -> 0
        normalized_board = th.where(board == player_id, th.ones_like(board), th.where(board == (1 - player_id), -th.ones_like(board), th.zeros_like(board)))

        return self.mlp(normalized_board)

# Stable-Baselines3 policy kwargs
policy_kwargs = dict(
    features_extractor_class=CustomMLP3x3,
    features_extractor_kwargs=dict(features_dim=64)
)
