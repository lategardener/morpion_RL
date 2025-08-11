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

print(MODELS_DIR)  # For verification

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
IMPROVEMENT_THRESHOLD = 0.04  # Threshold to consider an improvement
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
class CustomFeatureExtractorWithMask(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=256):
        super().__init__(observation_space, features_dim)

        action_mask_shape = observation_space['action_mask'].shape  # (board_length*board_length,)

        # CNN to process the board (grayscale, so 1 channel)
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute flattened CNN output size with dummy input
        with th.no_grad():
            sample_board = th.as_tensor(observation_space['observation'].sample()[None, None]).float()
            n_flatten = self.cnn(sample_board).shape[1]

        self.linear_cnn = nn.Sequential(
            nn.Linear(n_flatten, 128),
            nn.ReLU(),
        )

        # Small MLP for the action mask
        self.mask_net = nn.Sequential(
            nn.Linear(action_mask_shape[0], 64),
            nn.ReLU(),
        )

        # Small MLP for scalar features (num_moves_played, agent_can_win_next, opponent_can_win_next)
        self.scalar_net = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
        )

        # Combine all features
        self.final_net = nn.Sequential(
            nn.Linear(128 + 64 + 64, features_dim),  # CNN + mask + scalar features
            nn.ReLU(),
        )

    def forward(self, observations):
        # Process board: add channel dimension and convert to float
        board = observations['observation'].unsqueeze(1).float()

        # Process action mask
        mask = observations['action_mask'].float()

        # Stack scalar features into tensor (batch, 3)
        scalar_features = th.stack([
            observations['num_moves_played'].float(),
            observations['agent_can_win_next'].float(),
            observations['opponent_can_win_next'].float()
        ], dim=1)

        # Forward passes
        cnn_out = self.linear_cnn(self.cnn(board))
        mask_out = self.mask_net(mask)
        scalar_out = self.scalar_net(scalar_features)

        # Concatenate all
        combined = th.cat([cnn_out, mask_out, scalar_out], dim=1)

        return self.final_net(combined)


policy_kwargs = dict(
    features_extractor_class=CustomFeatureExtractorWithMask,
    features_extractor_kwargs=dict(features_dim=256)
)

