import json
from collections import deque
from envs import TicTacToeTrainingEnv
from utils.action_mask_ import mask_fn
from training.config import *


def evaluate_agent_by_opponent(agent, opponent_pool, n_episodes=1000):
    """
    Evaluate a given agent against a pool of opponents.

    Lost games are stored in a JSON file, keeping a maximum of 20 games.
    Each run deletes previous defeats and only stores the new ones.

    Args:
        agent: The RL agent to evaluate.
        opponent_pool: List of opponents (strings or PPO agent paths).
        n_episodes: Number of episodes per opponent (default: 1000).

    Returns:
        Dictionary with results per opponent including wins, losses, draws, and defeat/victory rates.
    """

    # Keep track of defeated games (max 20)
    MAX_SAVED_DEFEATS = 5
    registered = 0
    defeated_games = deque(maxlen=MAX_SAVED_DEFEATS)

    results = {}

    for opponent in opponent_pool:
        # Create two environments: agent plays first and agent plays second
        env_first = TicTacToeTrainingEnv(
            opponent_pool=[opponent],
            board_length=TRAINING_DEFAULT_BOARD_LENGTH,
            pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
            evaluation=True,
            first_play_rate=0.0,
            lost_games_path=DEFEAT_PATH,
            review_ratio=0.0,
            opponent_statistics_file=BEST_STATS_PATH,
        )

        env_second = TicTacToeTrainingEnv(
            opponent_pool=[opponent],
            board_length=TRAINING_DEFAULT_BOARD_LENGTH,
            pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
            evaluation=True,
            first_play_rate=1.0,
            lost_games_path=DEFEAT_PATH,
            review_ratio=0.0,
            opponent_statistics_file=BEST_STATS_PATH,
        )

        # Initialize counters
        wins_first = losses_first = draws_first = 0
        wins_second = losses_second = draws_second = 0

        # Fewer episodes for deterministic opponents
        episodes_for_current = n_episodes
        if opponent not in ["random", "smart_random"]:
            episodes_for_current = 2

        # Run episodes
        for i in range(episodes_for_current):
            env = env_first if i < episodes_for_current // 2 else env_second
            obs, _ = env.reset()
            done = False

            # Play one episode
            while not done:
                action, _ = agent.predict(obs, deterministic=True, action_masks=mask_fn(env))
                obs, reward, done, _, _ = env.step(action)

            # Record a lost game
            if reward == -env.victory_reward:
                registered += 1
                if registered < 5:
                    defeated_games.append({
                        f"game_lost_{len(defeated_games)+1}": {
                            "player": env.player,
                            "opponent": opponent,
                            "opponent_moves": [int(move) for move in env.opponent_blows],
                            "agent_moves": [int(move) for move in env.agent_blows]
                        }
                    })

                if env.first_to_play:
                    losses_first += 1
                else:
                    losses_second += 1

            # Record wins and draws
            elif reward > 0:
                if env.first_to_play:
                    wins_first += 1
                else:
                    wins_second += 1
            else:
                if env.first_to_play:
                    draws_first += 1
                else:
                    draws_second += 1

        # Save results per opponent
        results[opponent] = {
            "wins_play_first": wins_first,
            "wins_play_second": wins_second,
            "losses_play_first": losses_first,
            "losses_play_second": losses_second,
            "draws_play_first": draws_first,
            "draws_play_second": draws_second,
            "defeat_rate": (losses_first + losses_second) / episodes_for_current,
            "victory_rate": (wins_first + wins_second) / episodes_for_current
        }

        stats = results[opponent]
        print(f"Opponent: {opponent}")
        print(f"Defeat rate: {stats['defeat_rate']:.2%}")
        print(f"Losses (play first): {stats['losses_play_first']}")
        print(f"Losses (play second): {stats['losses_play_second']}")

    # -------------------------------
    # Save up to 20 new defeated games
    # -------------------------------
    import os
    os.makedirs(os.path.dirname(DEFEAT_PATH), exist_ok=True)

    with open(DEFEAT_PATH, "w") as f:
        json.dump({k: v for d in defeated_games for k, v in d.items()}, f, indent=4)

    return results
