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
CHECKPOINT_INTERVAL = 50000  # Number of steps between checkpoints
IMPROVEMENT_THRESHOLD = 0.03  # Threshold to consider an improvement
TOTAL_STEPS = 200000  # Total training steps

# Learning rate schedule (exponential decay)
LR_SCHEDULE = exp_decay(3e-4, 1e-5)


# ==============================
# Base model naming
# ==============================
BASE_MODELS_NAME = f"model_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"

# ==============================
# Policy architecture
# ==============================
import torch as th
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=256):
        super().__init__(observation_space, features_dim)

        # Convolutional neural network to extract spatial features from the board state
        # Input shape: (batch_size, 1, height, width) since the board is single-channel
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),  # Conv layer with 32 filters
            nn.ReLU(),                                   # Activation function
            nn.Conv2d(32, 64, kernel_size=3, padding=1),# Conv layer with 64 filters
            nn.ReLU(),                                   # Activation function
            nn.Flatten(),                                # Flatten feature maps to vector
        )

        # Calculate the number of features after CNN layers by performing a forward pass
        with th.no_grad():
            sample = th.as_tensor(observation_space['observation'].sample()[None, None]).float()
            n_flatten = self.cnn(sample).shape[1]

        # Fully connected layer to reduce feature dimensionality to desired size
        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations):
        # Extract the board state tensor from observations dict
        # Add channel dimension for CNN input: (batch_size, height, width) -> (batch_size, 1, height, width)
        x = observations['observation'].unsqueeze(1).float()

        # Pass through CNN layers
        x = self.cnn(x)

        # Pass through fully connected layer to obtain final feature representation
        return self.linear(x)

# Define policy keyword arguments to specify the custom feature extractor for PPO
policy_kwargs = dict(
    features_extractor_class=CustomCNN,
    features_extractor_kwargs=dict(features_dim=256)
)
