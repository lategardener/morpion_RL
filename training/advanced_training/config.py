import os
import torch.nn as nn
from utils.models_utils import exp_decay
from configs.config import  DEFAULT_BOARD_LENGTH, DEFAULT_PATTERN_VICTORY_LENGTH

# Training parameters
# Dossiers
MODELS_DIR = "../models/models_" + f"{DEFAULT_BOARD_LENGTH}_{DEFAULT_PATTERN_VICTORY_LENGTH}"
os.makedirs(MODELS_DIR, exist_ok=True)

# Chemins de fichiers
STATS_PATH = os.path.join(MODELS_DIR, "opponent_stats.json")

# Hyperparamètres
GAMMA = 0.99
GAE_LAMBDA = 0.95
START_ENT_COEF = 0.02
CHECKPOINT_INTERVAL = 4000
IMPROVEMENT_THRESHOLD = 0.04
START_MODEL_INDEX = 1
MAX_MODELS = 1
TOTAL_STEPS = 20_000
LR_SCHEDULE = exp_decay(3e-4, 1e-5)

# Architecture de la politique
POLICY_KWARGS = dict(
    activation_fn=nn.ReLU,
    net_arch=[dict(pi=[512, 512], vf=[512, 512])]
)

# Base models name
BASE_MODELS_NAME = "model_" + f"{DEFAULT_BOARD_LENGTH}_{DEFAULT_PATTERN_VICTORY_LENGTH}"