import numpy as np
import os
import json
from training.advanced_training.config import *

def convert_to_serializable(obj):
    """
    Convert numpy objects to native Python types for JSON serialization.
    - Converts numpy arrays to lists
    - Converts numpy ints and floats to native int and float
    - Recursively converts dictionaries and lists
    """
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
    """
    Load opponent statistics from a JSON file.
    If the file doesn't exist, initialize an empty dictionary.
    For each opponent, if not present, add default stats:
    - defeat_rate = 1.0
    - victory_rate = 0.0
    """
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
    """
    Save opponent statistics into a JSON file with indentation for readability.
    """
    with open(stats_path, "w") as f:
        json.dump(best_stats, f, indent=4)
