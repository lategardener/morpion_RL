import json
import random

from agents import RandomAgent, SmartRandomAgent, PPOAgent
from envs.base_env import *
from training.config import (
    TRAINING_DEFAULT_BOARD_LENGTH,
    TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH
)


class TicTacToeTrainingEnv(TicTacToeBaseEnv):
    """
    Extended TicTacToe environment for training RL agents.
    - Supports multiple opponent types (Random, SmartRandom, PPO-based agents)
    - Allows weighted opponent selection based on defeat statistics
    - Supports review mode (replaying past losing games)
    - Provides evaluation mode for logging agent and opponent actions
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
        """
        Initialize the training environment.

        Parameters:
        - board_length (int): size of the board (NxN)
        - pattern_victory_length (int): number of consecutive marks to win
        - render_mode (str): "ansi" or "matplotlib" rendering
        - victory_reward (float): reward for winning the game
        - opponent_pool (list[str]): list of opponent types or agent paths
        - evaluation (bool): if True, logs agent and opponent moves
        - first_play_rate (float): probability that the agent plays first
        - lost_games_path (str): JSON file path containing past lost games
        - review_ratio (float): probability of replaying a lost game
        - opponent_statistics_file (str): JSON file path with opponent statistics
        """
        super().__init__(board_length, pattern_victory_length, render_mode, victory_reward)

        # Opponent configuration
        self.opponent_pool = opponent_pool if opponent_pool else ["random"]
        self.opponent_agents = self.preload_opponents(self.opponent_pool)  # Preload opponent instances
        self.opponent_agent = None  # Current opponent for the episode
        self.opponent_blows = []    # Track opponent moves for evaluation
        self.opponent_load_blows = None  # Moves loaded from past losing games
        self.agent_blows = []       # Track agent moves for evaluation

        # Training settings
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
        """
        Load opponent statistics from JSON file.
        Returns empty dict if file does not exist.
        """
        if filepath is None or not os.path.exists(filepath):
            return {}
        with open(filepath, "r") as f:
            return json.load(f)

    def calculate_opponent_probabilities(self):
        """
        Calculate opponent selection probabilities.
        - 80% equally distributed among all opponents
        - 20% distributed proportionally to opponent's defeat rate
        Returns a normalized dictionary of probabilities.
        """
        probs = {}
        n = len(self.opponent_agents)

        # Equal portion (80%)
        equal_share = 0.8 / n

        # Total defeat rate for proportional portion (20%)
        total_defeat = sum(self.opponent_statistics.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]
                           for opponent in self.opponent_agents)

        # Compute total probabilities
        for opponent in self.opponent_agents:
            defeat_rate = self.opponent_statistics.get(opponent, {"defeat_rate": 1.0})["defeat_rate"]
            proportional_share = 0.2 * (defeat_rate / total_defeat) if total_defeat > 0 else 0
            probs[opponent] = equal_share + proportional_share

        # Normalize probabilities
        total = sum(probs.values())
        for k in probs:
            probs[k] /= total

        return probs

    def choose_opponent(self):
        """
        Randomly select an opponent using weighted probabilities.
        Returns the opponent key (string).
        """
        opponents = list(self.opponent_probabilities.keys())
        weights = list(self.opponent_probabilities.values())
        return random.choices(opponents, weights=weights, k=1)[0]

    def preload_opponents(self, opponent_pool):
        """
        Preload opponent agents to avoid repeated disk access.
        - RandomAgent and SmartRandomAgent are instantiated directly
        - PPOAgent loaded from .zip agent file
        Returns a dict of opponent instances.
        """
        agents = {}
        for opponent in opponent_pool:
            if opponent == "random":
                agents["random"] = RandomAgent()
            elif opponent == "smart_random":
                agents["smart_random"] = SmartRandomAgent()
            elif opponent.endswith(".zip") and os.path.exists(opponent):
                agents[opponent] = PPOAgent(agent_path=opponent, evaluation=True)
        return agents

    # ---------------------------
    # Environment control
    # ---------------------------
    def reset(self, seed=None, options=None):
        """
        Reset the environment for a new episode.
        - Select opponent
        - Optionally load a past losing game (review mode)
        - Or start normal game
        Returns initial observation and info.
        """
        obs, info = super().reset(seed, options)

        # Choose opponent
        chosen_opponent = self.choose_opponent()
        self.opponent_agent = self.opponent_agents[chosen_opponent]
        self.opponent_statistics = self.load_opponent_statistics(self.opponent_statistics_file)
        self.opponent_probabilities = self.calculate_opponent_probabilities()

        # Tracking variables
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

        # -----------------------------
        # Decide between normal or review game
        # -----------------------------
        if random.random() >= self.review_ratio or not self.retrieve_lost_games:
            # Normal game start
            self.draw = random.random()
            self.turn = 0 if self.draw <= self.first_play_rate else 1
            self.first_to_play = (self.turn == 0)

            # Opponent plays first if needed
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
        self.opponent_load_blows = lost_game_chosen[1].copy()
        self.opponent_load_blows_original = lost_game_chosen[1]

        # Apply first move if agent is player 1
        if self.player == 1 and self.opponent_load_blows:
            line, column = divmod(self.opponent_load_blows.pop(0), self.board_length)
            self.gameboard[line][column] = 0

        self.first_to_play = (self.player == 0)
        return self.get_observation(), {}

    def get_opponent_action(self):
        """
        Return opponent's move based on its type:
        - PPOAgent uses its play() method with observation
        - RandomAgent or SmartRandomAgent uses board info and valid moves
        Raises ValueError if opponent agent invalid.
        """
        valid_moves = np.where(self.valid_actions() == 1)[0]

        if hasattr(self.opponent_agent, "play"):
            if hasattr(self.opponent_agent, "agent"):  # PPOAgent
                obs = self.get_observation()
                return self.opponent_agent.play(obs)
            else:  # Random or SmartRandom
                return self.opponent_agent.play(
                    board_length=TRAINING_DEFAULT_BOARD_LENGTH,
                    pattern_victory_length=TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH,
                    player=self.player,
                    gameboard=self.gameboard,
                    valid_moves=valid_moves
                )

        raise ValueError("❌ Invalid opponent agent!")

    def step(self, action):
        """
        Process agent action and opponent action sequentially.
        - Reward agent for blocking opponent wins
        - Remove past game from replay if agent deviates
        Returns: observation, reward, done, truncated, info
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
            return obs_agent, reward_agent, done_agent, truncated_agent, info_agent

        # Reward for blocking imminent opponent win
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
                # Agent deviated from past game, generate new move
                opponent_action = self.get_opponent_action()
                self.opponent_load_blows = None  # disable further replay

        else:
            opponent_action = self.get_opponent_action()

        if self.evaluation:
            self.opponent_blows.append(opponent_action)

        obs_opponent, reward_opponent, done_opponent, truncated_opponent, _ = super().step(opponent_action)

        # Adjust reward if opponent wins or draw
        if done_opponent:
            final_reward = -self.victory_reward if reward_opponent == self.victory_reward else 0
            return obs_opponent, final_reward, done_opponent, truncated_opponent, info_agent

        return obs_opponent, reward_agent, done_opponent, truncated_opponent, info_agent
