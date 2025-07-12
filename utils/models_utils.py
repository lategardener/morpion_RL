from typing import Callable
import os

def get_models(path):
    """Retourne la liste des modèles triés par numéro, même avec plusieurs underscores."""
    print(f"---{path}---")
    model_files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f.startswith("model_") and f.endswith(".zip")
    ]

    def extract_number(file_path):
        name = os.path.basename(file_path)
        try:
            # prend le dernier élément avant ".zip"
            return int(name.replace(".zip", "").split("_")[-1])
        except:
            return -1  # fallback si jamais erreur

    return sorted(model_files, key=extract_number)



def should_save_model(current_stats, best_stats, threshold=0.03, max_defeat_increase=0.05):
    """
    Détermine si le modèle doit être sauvegardé.

    Règles :
    - Aucun adversaire ne doit avoir un defeat_rate augmenté de plus que max_defeat_increase
    - Aucun adversaire ne doit avoir un victory_rate diminué de plus que max_defeat_increase
    - Sinon, on sauvegarde si les améliorations >= régressions
    """
    improvements = regressions = 0

    for k in current_stats:
        current_defeat = current_stats[k]["defeat_rate"]
        best_defeat = best_stats.get(k, {"defeat_rate": 1.0})["defeat_rate"]
        current_victory = current_stats[k]["victory_rate"]
        best_victory = best_stats.get(k, {"victory_rate": 0.0})["victory_rate"]

        # Bloquant : explosion du taux de défaite (ex : de 0.7 à 0.76 ou +)
        if current_defeat >= best_defeat + max_defeat_increase:
            return False

        # Bloquant : chute trop forte du taux de victoire (ex : de 0.7 à 0.64 ou -)
        if current_victory <= best_victory - max_defeat_increase:
            return False

        # Comptage améliorations/régressions tolérables
        if current_defeat < best_defeat - threshold:
            improvements += 1
        elif current_defeat > best_defeat + threshold:
            regressions += 1

        if current_victory > best_victory + threshold:
            improvements += 1
        elif current_victory < best_victory - threshold:
            regressions += 1

    return improvements > regressions


def exp_decay(initial_lr: float, final_lr: float = 1e-5) -> Callable[[float], float]:
    """Retourne une fonction de scheduling exponentiel pour le learning rate."""
    def func(progress: float) -> float:
        return final_lr + (initial_lr - final_lr) * (0.1 ** (10 * progress))
    return func