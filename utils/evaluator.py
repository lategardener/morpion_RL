import json
from collections import deque
from envs import TicTacToeTrainingEnv
from utils.json_utils import convert_to_serializable
from test.action_mask_ import mask_fn
from training.advanced_training.config import *


def evaluate_model_by_opponent(model, opponent_pool, n_episodes=200):
    """Evaluate the model against each opponent and return statistics."""

    unique_opponents = list(set(opponent_pool))
    results = {}
    all_boards = []
    MAX_SAVED_DEFEATS = 20  # Increase max saved defeats to 20
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
            if i < n_episodes_for_current_opponent // 2:
                env = env1
            else:
                env = env2

            obs, _ = env.reset()
            done = False

            # Store the history of boards for tracking states during the episode
            board_history = []

            while not done:
                # Append current board state before agent plays
                board_history.append(convert_to_serializable(obs["observation"]))

                action, _ = model.predict(obs, deterministic=True, action_masks=mask_fn(env))
                obs, reward, done, _, _ = env.step(action)

            # On defeat, save the last and the second to last board state before the agent's penultimate move
            if reward == -env.victory_reward or reward == -1:
                # We want the two states before the agent's second to last move
                # The agent plays every other turn, so we look 2 and 4 steps before the end if possible
                # But simpler here: save last two board states if available
                if len(board_history) >= 2:
                    # Save the penultimate and antepenultimate states (if they exist)
                    boards_to_save = []
                    # Take last two board states before final move
                    boards_to_save.append(board_history[-2])
                    if len(board_history) >= 3:
                        boards_to_save.append(board_history[-3])
                    else:
                        # If no antepenultimate state, duplicate penultimate
                        boards_to_save.append(board_history[-2])

                    for board in boards_to_save:
                        if board not in all_boards:
                            all_boards.append(board)
                            defeated_games.append({
                                f"game_lose_against_{opponent}_{len(defeated_games)+1}": {
                                    "player": env.player,
                                    "board": board
                                }
                            })

                elif len(board_history) == 1:
                    # If only one state, save it once
                    board = board_history[0]
                    if board not in all_boards:
                        all_boards.append(board)
                        defeated_games.append({
                            f"{opponent}_{len(defeated_games)+1}": {
                                "player": env.player,
                                "board": board
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

    # Save defeated games to json file if any saved
    os.makedirs(os.path.dirname(DEFEAT_PATH), exist_ok=True)
    if defeated_games:
        with open(DEFEAT_PATH, "w") as f:
            json.dump({k: v for d in defeated_games for k, v in d.items()}, f, indent=4)

    return results
