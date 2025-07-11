import json
from collections import deque
from envs import TicTacToeTrainingEnv
from utils.json_utils import convert_to_serializable
from test.action_mask_ import mask_fn
from training.advanced_training.config import *


def evaluate_model_by_opponent(model, opponent_pool, n_episodes=200, stats_path=None):
    """Évalue le modèle contre chaque adversaire et retourne les statistiques."""

    global reward
    unique_opponents = list(set(opponent_pool))
    results = {}
    all_boards = []
    MAX_SAVED_DEFEATS = 10
    defeated_games = deque(maxlen=MAX_SAVED_DEFEATS)

    for opponent in unique_opponents:
        env1 = TicTacToeTrainingEnv(
            opponent_pool=[opponent],
            board_length=TRAINING_DEFAULT_BOARD_LENGTH,
            pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
            evaluation=True,
            first_play_rate=0.0,
            lost_games_path="defeated_games.json",
            review_ratio=0.0,
            opponent_statistics_file=stats_path,
        )

        env2 = TicTacToeTrainingEnv(
            opponent_pool=[opponent],
            board_length=TRAINING_DEFAULT_BOARD_LENGTH,
            pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
            evaluation=True,
            first_play_rate=1.0,
            lost_games_path="defeated_games.json",
            review_ratio=0.0,
            opponent_statistics_file=stats_path,
        )

        wins_play_first = losses_play_first = draws_play_first = 0
        wins_play_second = losses_play_second = draws_play_second = 0

        n_episodes_for_current_opponent = n_episodes
        if opponent not in ["random", "smart_random"]:
            n_episodes_for_current_opponent = 2

        for i in range(n_episodes_for_current_opponent):
            if i < n_episodes_for_current_opponent//2:
                env=env1
            else:
                env=env2

            obs, _ = env.reset()
            done = False
            episode_data = {"player": env.player, "board": []}

            while not done:
                action, _ = model.predict(obs, deterministic=True, action_masks=mask_fn(env))
                obs, reward, done, _, _ = env.step(action)
                if not done:
                    episode_data["board"] = convert_to_serializable(obs["observation"])

            if reward > 0:
                if env.first_to_play:
                    wins_play_first += 1
                else:
                    wins_play_second += 1
            elif reward == -env.victory_reward or reward == -1:
                if episode_data["board"] not in all_boards:
                    all_boards.append(episode_data["board"])
                    defeated_games.append({
                        f"game_lose_against_{opponent}_{len(defeated_games)+1}": episode_data
                    })
                if env.first_to_play:
                    losses_play_first += 1
                else:
                    losses_play_second += 1
            else:
                if env.first_to_play:
                    draws_play_first += 1
                else:
                    draws_play_second += 1

        results[opponent] = {
            "wins_play_first": wins_play_first,
            "wins_play_second": wins_play_second,
            "losses_play_first": losses_play_first,
            "losses_play_second": losses_play_second,
            "draws_play_first": draws_play_first,
            "draws_play_second": draws_play_second,
            "defeat_rate": (losses_play_first + losses_play_second) / n_episodes_for_current_opponent,
            "victory_rate": (wins_play_first + wins_play_second) / n_episodes_for_current_opponent
        }

    if defeated_games:
        with open("defeated_games.json", "w") as f:
            json.dump({k: v for d in defeated_games for k, v in d.items()}, f, indent=4)

    return results