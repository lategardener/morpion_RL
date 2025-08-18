from typing import Callable
import os

def get_models(path):
    """
    Return the list of model file paths sorted by their model number.

    Handles filenames with multiple underscores. Assumes model files
    start with 'model_' and end with '.zip'.
    """
    model_files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f.startswith("model_") and f.endswith(".zip")
    ]

    def extract_number(file_path):
        """
        Extract the model number from a filename.

        - Takes the last underscore-separated segment before '.zip'.
        - Returns -1 if extraction fails.
        """
        name = os.path.basename(file_path)
        try:
            return int(name.replace(".zip", "").split("_")[-1])
        except:
            return -1

    return sorted(model_files, key=extract_number)


def should_save_model(current_stats, best_stats, threshold=0.03, max_defeat_increase=0.01):
    """
    Decide whether to save the current model based on defeat rate comparisons.

    Rules:
    - Reject saving if any opponent's defeat_rate increases more than max_defeat_increase.
    - Count improvements and regressions across all opponents.
    - Save only if the number of improvements outweighs regressions.
    """
    improvements = 0
    regressions = 0

    for opponent in current_stats:
        current_defeat = current_stats[opponent]["defeat_rate"]
        best_defeat = best_stats.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]

        # Block saving if defeat rate increased too much
        if current_defeat >= best_defeat + max_defeat_increase:
            return False

        # Count minor improvements and regressions
        if current_defeat <= best_defeat:
            improvements += 1
        elif current_defeat > best_defeat + 0.008:
            regressions += 1

    return improvements > regressions


def get_last_model_number(models_dir):
    """
    Returns the highest model number in a directory of model files.

    Assumes model filenames are of the form 'model_X_Y_..._N.zip', where N is the number.
    Returns 0 if no model files exist.
    """
    model_files = [f for f in os.listdir(models_dir) if f.endswith(".zip")]

    max_num = 0

    for f in model_files:
        parts = f[:-4].split("_")
        try:
            num = int(parts[-1])
            if num > max_num:
                max_num = num
        except ValueError:
            # Skip files that don’t match expected pattern
            pass

    return max_num


def exp_decay(initial_lr: float, final_lr: float = 1e-5) -> Callable[[float], float]:
    """
    Returns an exponential decay function for learning rate scheduling.

    - The returned function accepts a progress float (0 to 1)
      and returns a smoothly decayed learning rate from initial_lr to final_lr.
    """
    def func(progress: float) -> float:
        return final_lr + (initial_lr - final_lr) * (0.1 ** (10 * progress))
    return func
