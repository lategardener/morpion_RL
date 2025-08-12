import json
from collections import deque
from envs import TicTacToeTrainingEnv
from test.action_mask_ import mask_fn
from training.advanced_training.config import *


def evaluate_model_by_opponent(model, opponent_pool, n_episodes=200):
    """Evaluate the model against each opponent and save lost games with opponent moves."""

    unique_opponents = list(set(opponent_pool))
    results = {}
    MAX_SAVED_DEFEATS = 20
    defeated_games = deque(maxlen=MAX_SAVED_DEFEATS)

    for opponent in unique_opponents:
        # Create two envs to test playing first and second
        env1 = TicTacToeTrainingEnv(
            opponent_pool=[opponent],
            board_length=TRAINING_DEFAULT_BOARD_LENGTH,
            pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
            evaluation=True,
            first_play_rate=0.0,
            lost_games_path=DEFEAT_PATH,
            review_ratio=0.0,
            opponent_statistics_file=STATS_PATH,
        )

        env2 = TicTacToeTrainingEnv(
            opponent_pool=[opponent],
            board_length=TRAINING_DEFAULT_BOARD_LENGTH,
            pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
            evaluation=True,
            first_play_rate=1.0,
            lost_games_path=DEFEAT_PATH,
            review_ratio=0.0,
            opponent_statistics_file=STATS_PATH,
        )

        wins_play_first = losses_play_first = draws_play_first = 0
        wins_play_second = losses_play_second = draws_play_second = 0

        n_episodes_for_current_opponent = n_episodes
        if opponent not in ["random", "smart_random"]:
            n_episodes_for_current_opponent = 2  # fewer episodes for deterministic opponents

        for i in range(n_episodes_for_current_opponent):
            env = env1 if i < n_episodes_for_current_opponent // 2 else env2

            obs, _ = env.reset()
            done = False

            while not done:
                action, _ = model.predict(obs, deterministic=True, action_masks=mask_fn(env))
                obs, reward, done, _, _ = env.step(action)

            # Défaite
            if reward == -env.victory_reward:
                defeated_games.append({
                    f"game_lost_{len(defeated_games)+1}": {
                        "player": env.player,
                        "opponent": opponent,
                        "opponent_moves": [int(move) for move in env.opponent_blows],
                        "agent_move": [int(move) for move in env.agent_blows]
                    }
                })

                if env.first_to_play:
                    losses_play_first += 1
                else:
                    losses_play_second += 1

            elif reward > 0:
                if env.first_to_play:
                    wins_play_first += 1
                else:
                    wins_play_second += 1
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

    # Sauvegarde des défaites
    os.makedirs(os.path.dirname(DEFEAT_PATH), exist_ok=True)
    if defeated_games:
        with open(DEFEAT_PATH, "w") as f:
            json.dump({k: v for d in defeated_games for k, v in d.items()}, f, indent=4)

    return results
