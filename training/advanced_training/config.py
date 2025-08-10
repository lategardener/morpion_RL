import os
from pathlib import Path

import torch.nn as nn
from utils.models_utils import exp_decay

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
START_MODEL_INDEX = 5  # Initial model index for loading
MAX_MODELS = 7  # Max number of models to keep
TOTAL_STEPS = 100_000  # Total training steps

# Learning rate schedule (exponential decay)
LR_SCHEDULE = exp_decay(3e-4, 1e-5)

# ==============================
# Policy architecture
# ==============================
POLICY_KWARGS = dict(
    activation_fn=nn.ReLU,
    net_arch=[dict(pi=[256, 256], vf=[256, 256])]
)

# ==============================
# Base model naming
# ==============================
BASE_MODELS_NAME = f"model_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"
