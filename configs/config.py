import os
import torch.nn as nn
from utils.models_utils import exp_decay


# Game parameters
DEFAULT_PATTERN_VICTORY_LENGTH = 5
DEFAULT_BOARD_LENGTH = 9
EMPTY_CELL = 3
VICTORY_REWARD = 1
DEFAULT_FIRST_PLAY_RATE = 0.5
DEFAULT_REVIEW_RATIO = 0.0
DEFAULT_RENDER_MODE = 'ansi'


# Training parameters
# Dossiers
MODELS_DIR = "models"
TAMPON_DIR = "tampon"
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(TAMPON_DIR, exist_ok=True)

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
