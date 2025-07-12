import json
import random

from agents import RandomAgent, SmartRandomAgent, PPOAgent
from envs.base_env import *
from training.advanced_training.config import TRAINING_DEFAULT_BOARD_LENGTH, TRAINING_DEFAULT_PATTERN_VICTORY_LENGTH


class TicTacToeTrainingEnv(TicTacToeBaseEnv):
    def __init__(self, board_length=DEFAULT_BOARD_LENGTH,
                 pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH,
                 render_mode=DEFAULT_RENDER_MODE,
                 victory_reward=VICTORY_REWARD,
                 opponent_pool=None,
                 evaluation=False,
                 first_play_rate=DEFAULT_FIRST_PLAY_RATE,
                 lost_games_path=None,
                 review_ratio=DEFAULT_REVIEW_RATIO,
                 opponent_statistics_file=None):

        super().__init__(board_length, pattern_victory_length, render_mode, victory_reward)
        self.opponent_pool = opponent_pool if opponent_pool else ["random"]
        self.opponent_models = self.preload_opponents(self.opponent_pool)  # Précharger tous les adversaires
        self.opponent_model = None
        self.evaluation = evaluation
        self.first_play_rate = first_play_rate
        self.lost_games_path = lost_games_path
        self.review_ratio = review_ratio
        self.opponent_statistics = self.load_opponent_statistics(opponent_statistics_file)
        self.opponent_probabilities = self.calculate_opponent_probabilities()



    def load_opponent_statistics(self, filepath):
        if filepath is None or not os.path.exists(filepath):
            print("⚠️ No statistics file provided or file not found.")
            return {}
        with open(filepath, "r") as f:
            return json.load(f)

    def calculate_opponent_probabilities(self):
        """Calcule une distribution de probabilité basée sur le taux de défaite"""
        probs = {}
        epsilon = 0.05  # Pour que même les adversaires à defeat_rate=0 soient joués

        for opponent in self.opponent_models:
            stats = self.opponent_statistics.get(opponent, {"defeat_rate": 1.0, "victory_rate": 0.0})
            defeat_rate = stats.get("defeat_rate", 1.0)
            # Éviter une proba nulle
            probs[opponent] = defeat_rate + epsilon

        # Normalisation
        total = sum(probs.values())
        for k in probs:
            probs[k] /= total

        return probs


    def choose_opponent(self):
        """Tirage pondéré selon la probabilité calculée"""
        opponents = list(self.opponent_probabilities.keys())
        weights = list(self.opponent_probabilities.values())
        return random.choices(opponents, weights=weights, k=1)[0]

    def preload_opponents(self, opponent_pool):
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

        """Sélectionne un adversaire au début de chaque partie sans recharger le modèle depuis le disque."""
        obs, info = super().reset(seed, options)

        chosen_opponent = random.choice(list(self.opponent_models.keys()))
        self.opponent_model = self.opponent_models[chosen_opponent]
        self.number_turn = 0
        self.retrieve_lost_games = []

        if self.review_ratio > 0:
            try:
                self.lost_games_path is not None
                with open(self.lost_games_path, "r") as file:
                    data = json.load(file)
                    for key, value in data.items():
                        self.retrieve_lost_games.append([value["player"], value["board"]])

            except FileNotFoundError:
                print(f"{RED}❌ Aucun fichier de parties perdues trouvé. {RESET}")

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
                if opponent_action is not None:
                    obs, _, _, _, _ = super().step(opponent_action)

        else:
            # print(f"{RED} ---------------> {"here"} <----------------{RESTART}")
            lost_game_chosen = random.choice(self.retrieve_lost_games)
            self.player = lost_game_chosen[0]
            self.turn = self.player
            self.set_gameboard(np.array(lost_game_chosen[1], dtype=np.int8))
            if self.player == 0:
                self.first_to_play = True
            else:
                self.first_to_play = False

            return self.get_observation(), {}

        return obs, info


    def get_opponent_action(self):
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

        raise ValueError("❌ Modèle d'adversaire invalide !")


    def step(self, action):

        valid_moves = np.where(self.valid_actions() == 1)[0]
        opponent_win_before_moving = is_winning_move(1 - self.player, self.gameboard, self.board_length, self.pattern_victory_length, valid_moves)

        self.number_turn += 1


        """Tour du joueur"""
        obs_agent, reward_agent, done_agent, truncated_agent, info_agent = super().step(action)

        if done_agent or truncated_agent:
            return obs_agent, self.victory_reward, done_agent, truncated_agent, info_agent

        if opponent_win_before_moving is not None:
            valid_moves_after_play = np.where(self.valid_actions() == 1)[0]
            opponent_win_after_moving = is_winning_move(self.player, self.gameboard, self.board_length, self.pattern_victory_length, valid_moves_after_play)
            if opponent_win_after_moving is None:
                reward_agent += 0.05

        """Tour de l'adversaire"""
        opponent_action = self.get_opponent_action()
        obs_opponent, reward_opponent, done_opponent, truncated_opponent, _ = super().step(opponent_action)

        # Si l'adversaire gagne ou si c'est un match nul
        if done_opponent:
            final_reward = -self.victory_reward if reward_opponent == self.victory_reward else 0  # Pénalité si l'agent perd, 0 si match nul
            return obs_opponent, final_reward, done_opponent, truncated_opponent, info_agent


        return obs_opponent, reward_agent, done_opponent, truncated_opponent, info_agent
