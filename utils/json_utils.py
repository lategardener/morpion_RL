import numpy as np
import os
import json
from configs.config import *

def convert_to_serializable(obj):
    """Convertit les objets numpy en types Python natifs pour la sérialisation JSON."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    return obj

def load_opponent_stats(opponents, stats_path=STATS_PATH):
    """Charge les statistiques des adversaires depuis le fichier JSON."""
    if os.path.exists(stats_path):
        with open(stats_path, "r") as f:
            saved_stats = json.load(f)
    else:
        saved_stats = {}

    for opp in opponents:
        if opp not in saved_stats:
            saved_stats[opp] = {"defeat_rate": 1.0, "victory_rate": 0.0}
    return saved_stats

def save_opponent_stats(best_stats, stats_path):
    """Sauvegarde les statistiques des adversaires dans un fichier JSON."""
    with open(stats_path, "w") as f:
        json.dump(best_stats, f, indent=4)