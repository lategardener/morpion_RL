import os

import torch.nn as nn
from utils.models_utils import exp_decay
import torch as th
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

# ==============================
# Training parameters
# ==============================
TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH = 3
TRAINING_DEFAULT_BOARD_LENGTH = 3
TRAINING_DEFAULT_FIRST_PLAY_RATE = 0.5
TRAINING_DEFAULT_REVIEW_RATIO = 0.0

# ==============================
# Directories and paths
# ==============================

# Absolute path to this file (config.py)
current_file_path = os.path.abspath(__file__)

# Directory containing config.py
current_dir = os.path.dirname(current_file_path)

# Move up two levels to the root of the tic_tac_toe_rl project
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Build path to models directory
MODELS_DIR = os.path.join(
    project_root,
    'models',
    f'models_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}'
)


# Folder name for wandb model saving (if used)
WANDB_MODEL_DIR = f"{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# Path to statistics file
STATS_PATH = os.path.join(MODELS_DIR, "opponent_stats.json")
DEFEAT_PATH = os.path.join(MODELS_DIR, "defeated_games.json")

# ==============================
# Hyperparameters
# ==============================
GAMMA = 0.99  # Discount factor
GAE_LAMBDA = 0.95  # GAE lambda for advantage estimation
START_ENT_COEF = 0.02  # Initial entropy coefficient
CHECKPOINT_INTERVAL = 10000  # Number of steps between checkpoints
IMPROVEMENT_THRESHOLD = 0.03  # Threshold to consider an improvement
TOTAL_STEPS = 100_000  # Total training steps

# Learning rate schedule (exponential decay)
LR_SCHEDULE = exp_decay(3e-4, 1e-5)


# ==============================
# Base model naming
# ==============================
BASE_MODELS_NAME = f"model_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"

# ==============================
# Policy architecture
# ==============================
class CustomFeatureExtractorWithPlayer(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=256):
        super().__init__(observation_space, features_dim)

        # Lightweight CNN to process the board (1 channel grayscale)
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),  # 8 filters instead of 32
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute the flattened CNN output size using a sample input
        with th.no_grad():
            sample_board = th.as_tensor(observation_space['observation'].sample()[None, None]).float()
            n_flatten = self.cnn(sample_board).shape[1]

        # Linear layer after CNN, smaller size
        self.linear_cnn = nn.Sequential(
            nn.Linear(n_flatten, 64),  # reduced from 128 to 64
            nn.ReLU(),
        )

        # MLP for the current_player scalar input
        self.player_net = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(),
        )

        # Combine CNN features and player info
        self.final_net = nn.Sequential(
            nn.Linear(64 + 16, features_dim),  # adjusted to the combined input size
            nn.ReLU(),
        )

    def forward(self, observations):
        board = observations['observation'].unsqueeze(1).float()    # (batch, 1, H, W)
        current_player = observations['current_player'].float().view(-1, 1)  # (batch, 1)

        cnn_out = self.linear_cnn(self.cnn(board))
        player_out = self.player_net(current_player)

        combined = th.cat([cnn_out, player_out], dim=1)
        return self.final_net(combined)

# Define policy kwargs to use this custom feature extractor
policy_kwargs = dict(
    features_extractor_class=CustomFeatureExtractorWithPlayer,
    features_extractor_kwargs=dict(features_dim=256)
)
