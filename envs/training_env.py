import json
import random
import os
import numpy as np

from agents import RandomAgent, SmartRandomAgent, PPOAgent
from envs.base_env import *
from training.advanced_training.config import (
    TRAINING_DEFAULT_BOARD_LENGTH,
    TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH
)


class TicTacToeTrainingEnv(TicTacToeBaseEnv):
    """
    Extended TicTacToe environment for training agents against various opponents.
    Supports weighted opponent selection, replaying past losing games, and evaluation mode.
    """

    def __init__(self,
                 board_length=DEFAULT_BOARD_LENGTH,
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
        self.opponent_models = self.preload_opponents(self.opponent_pool)  # Preload all opponents
        self.opponent_model = None
        self.opponent_blows = []
        self.opponent_load_blows = None
        self.agent_blows = []

        # Training and evaluation settings
        self.evaluation = evaluation
        self.first_play_rate = first_play_rate
        self.lost_games_path = lost_games_path
        self.review_ratio = review_ratio

        # Opponent probability weighting based on statistics
        self.opponent_statistics_file = opponent_statistics_file
        self.opponent_statistics = self.load_opponent_statistics(self.opponent_statistics_file)
        self.opponent_probabilities = self.calculate_opponent_probabilities()

    # ---------------------------
    # Opponent statistics
    # ---------------------------

    def load_opponent_statistics(self, filepath):
        """Load opponent statistics from a JSON file."""
        if filepath is None or not os.path.exists(filepath):
            return {}
        with open(filepath, "r") as f:
            return json.load(f)

    def calculate_opponent_probabilities(self):
        """
        Calculate opponent selection probabilities using an 80/20 split:
        - 80% of the probability is distributed equally among all opponents
        - 20% is distributed proportionally according to the opponent's defeat rate
        Ensures all opponents have a non-zero chance of being selected.
        """
        probs = {}
        n = len(self.opponent_models)

        # 1. Equal share portion (80%)
        equal_share = 0.8 / n

        # 2. Compute total defeat rate for proportional share (20%)
        total_defeat = sum(self.opponent_statistics.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]
                           for opponent in self.opponent_models)

        # 3. Calculate probabilities
        for opponent in self.opponent_models:
            defeat_rate = self.opponent_statistics.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]
            proportional_share = 0.2 * (defeat_rate / total_defeat) if total_defeat > 0 else 0
            probs[opponent] = equal_share + proportional_share

        # 4. Normalize to ensure total probability sums to 1
        total = sum(probs.values())
        for k in probs:
            probs[k] /= total

        return probs


    def choose_opponent(self):
        """Randomly select an opponent using weighted probabilities."""
        opponents = list(self.opponent_probabilities.keys())
        weights = list(self.opponent_probabilities.values())
        return random.choices(opponents, weights=weights, k=1)[0]

    def preload_opponents(self, opponent_pool):
        """Preload opponent agents/models to avoid repeated disk access."""
        models = {}
        for opponent in opponent_pool:
            if opponent == "random":
                models["random"] = RandomAgent()
            elif opponent == "smart_random":
                models["smart_random"] = SmartRandomAgent()
            elif opponent.endswith(".zip") and os.path.exists(opponent):
                models[opponent] = PPOAgent(model_path=opponent, evaluation=True)
        return models

    # ---------------------------
    # Environment control
    # ---------------------------

    def reset(self, seed=None, options=None):
        """
        Start a new episode:
        - Select an opponent
        - Optionally load a past losing game (review mode)
        - Or start a normal game if no lost games exist or random chance
        """
        # Call base reset to initialize the board
        obs, info = super().reset(seed, options)

        # Select opponent for this episode
        chosen_opponent = self.choose_opponent()
        self.opponent_model = self.opponent_models[chosen_opponent]
        self.opponent_statistics = self.load_opponent_statistics(self.opponent_statistics_file)
        self.opponent_probabilities = self.calculate_opponent_probabilities()

        # Initialize tracking variables
        self.number_turn = 0
        self.retrieve_lost_games = []
        self.opponent_blows = []
        self.agent_blows = []

        # -----------------------------
        # Load past losing games
        # -----------------------------
        if self.review_ratio > 0 and self.lost_games_path is not None:
            try:
                with open(self.lost_games_path, "r") as file:
                    data = json.load(file)
                    for _, value in data.items():
                        self.retrieve_lost_games.append([
                            value["player"],
                            value["opponent_moves"]
                        ])
            except FileNotFoundError:
                pass
                # print(f"{RED}❌ No lost games file found. {RESET}")

        # -----------------------------
        # Decide between normal or review game
        # -----------------------------
        if random.random() >= self.review_ratio or not self.retrieve_lost_games:
            # Normal game start
            self.draw = random.random()
            self.turn = 0 if self.draw <= self.first_play_rate else 1
            self.first_to_play = (self.turn == 0)

            # If opponent plays first
            if not self.first_to_play:
                opponent_action = self.get_opponent_action()
                if self.evaluation:
                    self.opponent_blows.append(opponent_action)
                if opponent_action is not None:
                    obs, _, _, _, _ = super().step(opponent_action)

            return obs, info

        # -----------------------------
        # Start from a past losing position
        # -----------------------------
        lost_game_chosen = random.choice(self.retrieve_lost_games)
        self.player = lost_game_chosen[0]

        # Create a copy of opponent moves for the current game
        self.opponent_load_blows = lost_game_chosen[1].copy()

        # Keep the original list for file deletion if needed
        self.opponent_load_blows_original = lost_game_chosen[1]

        # Apply first move if agent is player 1
        if self.player == 1 and self.opponent_load_blows:
            line, column = divmod(self.opponent_load_blows.pop(0), self.board_length)
            self.gameboard[line][column] = 0

        self.first_to_play = (self.player == 0)
        return self.get_observation(), {}



    def get_opponent_action(self):
        """Return the opponent's move based on its model type."""
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
        Process the agent's action and then the opponent's action.
        Rewards are assigned based on game outcome and special events (e.g., blocking an imminent opponent win).
        If the agent deviates from a pre-recorded losing game, that specific game is removed from the JSON file
        using the original moves list.
        """
        valid_moves = np.where(self.valid_actions() == 1)[0]

        # Check if opponent has a winning move before agent plays
        opponent_win_before_moving = is_winning_move(
            1 - self.player, self.gameboard,
            self.board_length, self.pattern_victory_length,
            valid_moves
        )

        self.number_turn += 1

        # ---------------------
        # Agent's turn
        # ---------------------
        obs_agent, reward_agent, done_agent, truncated_agent, info_agent = super().step(action)
        if self.evaluation:
            self.agent_blows.append(action)

        if done_agent or truncated_agent:
            return obs_agent, self.victory_reward, done_agent, truncated_agent, info_agent

        # Reward for blocking an imminent opponent win
        if opponent_win_before_moving is not None:
            valid_moves_after_play = np.where(self.valid_actions() == 1)[0]
            opponent_win_after_moving = is_winning_move(
                self.player, self.gameboard,
                self.board_length, self.pattern_victory_length,
                valid_moves_after_play
            )
            if opponent_win_after_moving is None:
                reward_agent += REWARD_BLOCK_OPP_WIN

        # ---------------------
        # Opponent's turn
        # ---------------------
        if self.opponent_load_blows:
            opponent_action = self.opponent_load_blows.pop(0)
            valid_moves = np.where(self.valid_actions() == 1)[0]
            if opponent_action not in valid_moves:
                # Agent deviated from pre-recorded game; choose a new valid action
                opponent_action = self.get_opponent_action()
                # Disable further replay for this episode
                self.opponent_load_blows = None

        else:
            opponent_action = self.get_opponent_action()

        if self.evaluation:
            self.opponent_blows.append(opponent_action)

        obs_opponent, reward_opponent, done_opponent, truncated_opponent, _ = super().step(opponent_action)

        # Check for opponent win or draw
        if done_opponent:
            final_reward = -self.victory_reward if reward_opponent == self.victory_reward else 0
            return obs_opponent, final_reward, done_opponent, truncated_opponent, info_agent

        return obs_opponent, reward_agent, done_opponent, truncated_opponent, info_agent


