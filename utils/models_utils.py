from typing import Callable
import os

def get_models(path):
    """
    Return the list of model file paths sorted by their model number,
    even if filenames contain multiple underscores.
    """
    model_files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f.startswith("model_") and f.endswith(".zip")
    ]

    def extract_number(file_path):
        """
        Extract the model number from the filename by taking
        the last underscore-separated part before '.zip'.
        If extraction fails, return -1 as fallback.
        """
        name = os.path.basename(file_path)
        try:
            return int(name.replace(".zip", "").split("_")[-1])
        except:
            return -1

    return sorted(model_files, key=extract_number)


def should_save_model(current_stats, best_stats, threshold=0.03, max_defeat_increase=0.01):
    """
    Decide whether to save the current model based only on defeat rate comparison.

    Rules:
    - No opponent should have defeat_rate increased by more than max_defeat_increase.
    - Save only if the number of improvements (defeat rate decreases beyond threshold)
      outweigh regressions (defeat rate increases beyond threshold).
    """
    improvements = 0
    regressions = 0

    for opponent in current_stats:
        current_defeat = current_stats[opponent]["defeat_rate"]
        best_defeat = best_stats.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]

        # Blocking condition: too large increase in defeat rate
        if current_defeat >= best_defeat + max_defeat_increase:
            return False

        # Count tolerable improvements and regressions on defeat rate
        if current_defeat <= best_defeat:
            improvements += 1
        elif current_defeat > best_defeat + 0.008:
            regressions += 1

    # Save if improvements exceed regressions
    return improvements > regressions



def get_last_model_number(models_dir):
    """
    Returns the highest model number found in all '.zip' filenames within the directory.

    It assumes the model number is the last underscore-separated segment before '.zip'.

    Example filename: model_3_3_7.zip -> returns 7

    Args:
        models_dir (str): path to the directory containing model files

    Returns:
        int: highest model number found, or 0 if no models exist
    """
    model_files = [
        f for f in os.listdir(models_dir)
        if f.endswith(".zip")
    ]

    max_num = 0  # Default if no models found

    for f in model_files:
        # Remove '.zip' and split by underscore
        parts = f[:-4].split("_")
        try:
            # Take last part as model number
            num = int(parts[-1])
            if num > max_num:
                max_num = num
        except ValueError:
            # Filename doesn’t match expected pattern, skip
            pass

    return max_num



def exp_decay(initial_lr: float, final_lr: float = 1e-5) -> Callable[[float], float]:
    """
    Return an exponential decay function for learning rate scheduling.

    The returned function takes a progress float between 0 and 1 and returns
    the decayed learning rate, smoothly moving from initial_lr to final_lr.
    """
    def func(progress: float) -> float:
        return final_lr + (initial_lr - final_lr) * (0.1 ** (10 * progress))
    return func
