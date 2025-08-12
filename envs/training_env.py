import json
import random
import os
import numpy as np

from agents import RandomAgent, SmartRandomAgent, PPOAgent
from envs.base_env import *
from training.advanced_training.config import TRAINING_DEFAULT_BOARD_LENGTH, TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH


class TicTacToeTrainingEnv(TicTacToeBaseEnv):
    """
    Extended TicTacToe environment for training agents against various opponents.
    Supports opponent probability weighting, loading past defeats for replay,
    and evaluation mode.
    """

    def __init__(self, board_length=DEFAULT_BOARD_LENGTH,
                 pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH,
                 render_mode=DEFAULT_RENDER_MODE,
                 victory_reward=REWARD_VICTORY,
                 opponent_pool=None,
                 evaluation=False,
                 first_play_rate=DEFAULT_FIRST_PLAY_RATE,
                 lost_games_path=None,
                 review_ratio=DEFAULT_REVIEW_RATIO,
                 opponent_statistics_file=None):

        super().__init__(board_length, pattern_victory_length, render_mode, victory_reward)

        # Opponent configuration
        self.opponent_pool = opponent_pool if opponent_pool else ["random"]
        self.opponent_models = self.preload_opponents(self.opponent_pool)  # Preload all opponents to avoid reloading from disk
        self.opponent_model = None
        self.opponent_blows = []
        self.agent_blows = []

        # Training and evaluation settings
        self.evaluation = evaluation
        self.first_play_rate = first_play_rate
        self.lost_games_path = lost_games_path
        self.review_ratio = review_ratio

        # Opponent selection based on statistics
        self.opponent_statistics = self.load_opponent_statistics(opponent_statistics_file)
        self.opponent_probabilities = self.calculate_opponent_probabilities()

    def load_opponent_statistics(self, filepath):
        """Load opponent statistics from JSON file."""
        if filepath is None or not os.path.exists(filepath):
            return {}
        with open(filepath, "r") as f:
            return json.load(f)

    def calculate_opponent_probabilities(self):
        """
        Calculate a weighted probability distribution for opponent selection,
        based on their defeat rate.
        """
        probs = {}
        epsilon = 0.05  # Ensures all opponents have a non-zero probability

        for opponent in self.opponent_models:
            stats = self.opponent_statistics.get(opponent, {"defeat_rate": 1.0, "victory_rate": 0.0})
            defeat_rate = stats.get("defeat_rate", 1.0)
            probs[opponent] = defeat_rate + epsilon

        # Normalize probabilities
        total = sum(probs.values())
        for k in probs:
            probs[k] /= total

        return probs

    def choose_opponent(self):
        """
        Randomly select an opponent based on calculated probabilities.
        Occasionally prints probabilities for debugging.
        """
        opponents = list(self.opponent_probabilities.keys())
        weights = list(self.opponent_probabilities.values())
        return random.choices(opponents, weights=weights, k=1)[0]

    def preload_opponents(self, opponent_pool):
        """
        Preload opponent models into memory to avoid disk access during training.
        """
        models = {}
        for opponent in opponent_pool:
            if opponent == "random":
                models["random"] = RandomAgent()
            elif opponent == "smart_random":
                models["smart_random"] = SmartRandomAgent()
            elif opponent.endswith(".zip") and os.path.exists(opponent):
                models[opponent] = PPOAgent(model_path=opponent, evaluation=True)
        return models

    def reset(self, seed=None, options=None):
        """
        Selects an opponent at the start of each episode.
        Optionally loads a random losing position from previous games
        (based on review_ratio) for training from disadvantageous states.
        """
        obs, info = super().reset(seed, options)

        chosen_opponent = self.choose_opponent()
        self.opponent_model = self.opponent_models[chosen_opponent]
        self.number_turn = 0
        self.retrieve_lost_games = []
        self.opponent_blows = []
        self.agent_blows = []

        # Load past lost games for review mode
        if self.review_ratio > 0:
            try:
                if self.lost_games_path is not None:
                    with open(self.lost_games_path, "r") as file:
                        data = json.load(file)
                        for _, value in data.items():
                            self.retrieve_lost_games.append([value["player"], value["opponent_moves"]])
            except FileNotFoundError:
                print(f"{RED}❌ No lost games file found. {RESET}")

        # Regular game start
        if random.random() >= self.review_ratio:
            self.draw = random.random()
            if self.draw <= self.first_play_rate:
                self.turn = 0
            else:
                self.turn = 1

            self.first_to_play = True
            if self.turn != self.player:
                self.first_to_play = False
                opponent_action = self.get_opponent_action()
                if self.evaluation:
                    self.opponent_blows.append(opponent_action)
                if opponent_action is not None:
                    obs, _, _, _, _ = super().step(opponent_action)

        # Start from a past losing position
        else:
            lost_game_chosen = random.choice(self.retrieve_lost_games)
            self.player = lost_game_chosen[0]
            self.turn = self.player
            if self.player == 1:
                # Map action (integer) to 2D board coordinates (row, col)
                line, column = divmod(lost_game_chosen[1].pop(0), self.board_length)
                self.gameboard[line][column] = self.player
            self.first_to_play = (self.player == 0)
            return self.get_observation(), {}

        return obs, info

    def get_opponent_action(self):
        """
        Get the opponent's move based on the loaded model.
        """
        valid_moves = np.where(self.valid_actions() == 1)[0]

        if hasattr(self.opponent_model, "play"):
            if hasattr(self.opponent_model, "model"):  # PPOAgent
                obs = self.get_observation()
                return self.opponent_model.play(obs)
            else:  # Random or SmartRandom
                return self.opponent_model.play(
                    board_length=TRAINING_DEFAULT_BOARD_LENGTH,
                    pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
                    player=self.player,
                    gameboard=self.gameboard,
                    valid_moves=valid_moves
                )

        raise ValueError("❌ Invalid opponent model!")

    def step(self, action):
        """
        Executes the agent's move, then the opponent's move.
        Rewards and penalties are assigned based on game outcome.
        """
        valid_moves = np.where(self.valid_actions() == 1)[0]
        opponent_win_before_moving = is_winning_move(
            1 - self.player, self.gameboard,
            self.board_length, self.pattern_victory_length,
            valid_moves
        )

        self.number_turn += 1

        # Agent's turn
        obs_agent, reward_agent, done_agent, truncated_agent, info_agent = super().step(action)
        if self.evaluation:
            self.agent_blows.append(action)

        if done_agent or truncated_agent:
            return obs_agent, self.victory_reward, done_agent, truncated_agent, info_agent

        # Reward for blocking opponent's imminent win
        if opponent_win_before_moving is not None:
            valid_moves_after_play = np.where(self.valid_actions() == 1)[0]
            opponent_win_after_moving = is_winning_move(
                self.player, self.gameboard,
                self.board_length, self.pattern_victory_length,
                valid_moves_after_play
            )
            if opponent_win_after_moving is None:
                reward_agent += REWARD_BLOCK_OPP_WIN

        # Opponent's turn
        opponent_action = self.get_opponent_action()
        if self.evaluation:
            self.opponent_blows.append(opponent_action)
        obs_opponent, reward_opponent, done_opponent, truncated_opponent, _ = super().step(opponent_action)

        # If opponent wins or it's a draw
        if done_opponent:
            final_reward = -self.victory_reward if reward_opponent == self.victory_reward else 0
            return obs_opponent, final_reward, done_opponent, truncated_opponent, info_agent

        return obs_opponent, reward_agent, done_opponent, truncated_opponent, info_agent
