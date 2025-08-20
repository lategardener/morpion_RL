from typing import Callable
import os

def get_agents(path):
    """
    Return the list of agent file paths sorted by their agent number.

    Handles filenames with multiple underscores. Assumes agent files
    start with 'agent_' and end with '.zip'.
    """
    agent_files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f.startswith("agent_") and f.endswith(".zip")
    ]

    def extract_number(file_path):
        """
        Extract the agent number from a filename.

        - Takes the last underscore-separated segment before '.zip'.
        - Returns -1 if extraction fails.
        """
        name = os.path.basename(file_path)
        try:
            return int(name.replace(".zip", "").split("_")[-1])
        except:
            return -1

    return sorted(agent_files, key=extract_number)


def should_save_agent(current_stats, best_stats, threshold=0.03, max_defeat_increase=0.01):
    """
    Decide whether to save the current agent based on defeat rate comparisons.

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


def get_last_agent_number(agents_dir):
    """
    Returns the highest agent number in a directory of agent files.

    Assumes agent filenames are of the form 'agent_X_Y_..._N.zip', where N is the number.
    Returns 0 if no agent files exist.
    """
    agent_files = [f for f in os.listdir(agents_dir) if f.endswith(".zip")]

    max_num = 0

    for f in agent_files:
        try:
            num = int(f[7])
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
