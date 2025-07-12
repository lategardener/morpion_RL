import os
from pathlib import Path

import torch.nn as nn
from utils.models_utils import exp_decay

# Training parameters
TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH = 3
TRAINING_DEFAULT_BOARD_LENGTH = 3
TRAINING_DEFAULT_FIRST_PLAY_RATE = 0.5
TRAINING_DEFAULT_REVIEW_RATIO = 0.0

# Dossiers

# Pour pointer depuis le fichier courant vers la racine

# Chemin absolu vers ce fichier (config.py)
current_file_path = os.path.abspath(__file__)

# Dossier contenant config.py
current_dir = os.path.dirname(current_file_path)

# Remonter 2 niveaux vers la racine du projet tic_tac_toe_rl
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Construire le chemin vers models/
MODELS_DIR = os.path.join(
    project_root,
    'models',
    f'models_{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}'
)

print(MODELS_DIR)  # Pour vérifier

# Construction du chemin vers le dossier modèle
WANDB_MODEL_DIR = f"{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"

os.makedirs(MODELS_DIR, exist_ok=True)

# Chemins de fichiers
STATS_PATH = os.path.join(MODELS_DIR, "opponent_stats.json")

# Hyperparamètres
GAMMA = 0.99
GAE_LAMBDA = 0.95
START_ENT_COEF = 0.02
CHECKPOINT_INTERVAL = 10000
IMPROVEMENT_THRESHOLD = 0.04
START_MODEL_INDEX = 4
MAX_MODELS = 4
TOTAL_STEPS = 10_000
LR_SCHEDULE = exp_decay(3e-4, 1e-5)

# Architecture de la politique
POLICY_KWARGS = dict(
    activation_fn=nn.ReLU,
    net_arch=[dict(pi=[512, 512], vf=[512, 512])]
)

# Base models name
BASE_MODELS_NAME = "model_" + f"{TRAINING_DEFAULT_BOARD_LENGTH}_{TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH}"