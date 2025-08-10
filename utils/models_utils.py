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


def should_save_model(current_stats, best_stats, threshold=0.03, max_defeat_increase=0.05):
    """
    Decide whether to save the current model based on performance stats comparison.

    Rules:
    - No opponent should have defeat_rate increased by more than max_defeat_increase.
    - No opponent should have victory_rate decreased by more than max_defeat_increase.
    - Otherwise, save only if the number of improvements outweigh regressions beyond the threshold.
    """
    improvements = 0
    regressions = 0

    for opponent in current_stats:
        current_defeat = current_stats[opponent]["defeat_rate"]
        best_defeat = best_stats.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]
        current_victory = current_stats[opponent]["victory_rate"]
        best_victory = best_stats.get(opponent, {"victory_rate": 0.0})["victory_rate"]

        # Blocking condition: too large increase in defeat rate (e.g. from 0.7 to 0.76 or more)
        if current_defeat >= best_defeat + max_defeat_increase:
            return False

        # Blocking condition: too large decrease in victory rate (e.g. from 0.7 to 0.64 or less)
        if current_victory <= best_victory - max_defeat_increase:
            return False

        # Count tolerable improvements and regressions
        if current_defeat < best_defeat - threshold:
            improvements += 1
        elif current_defeat > best_defeat + threshold:
            regressions += 1

        if current_victory > best_victory + threshold:
            improvements += 1
        elif current_victory < best_victory - threshold:
            regressions += 1

    # Save if improvements exceed regressions
    return improvements > regressions


def exp_decay(initial_lr: float, final_lr: float = 1e-5) -> Callable[[float], float]:
    """
    Return an exponential decay function for learning rate scheduling.

    The returned function takes a progress float between 0 and 1 and returns
    the decayed learning rate, smoothly moving from initial_lr to final_lr.
    """
    def func(progress: float) -> float:
        return final_lr + (initial_lr - final_lr) * (0.1 ** (10 * progress))
    return func
