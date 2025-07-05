from envs.base_env import  *
import os
import numpy as np
from sb3_contrib import MaskablePPO
from time import sleep
import random


def get_player_move(env, player=None):

    if player is None:
        """ Demande au joueur humain de choisir une case valide en fonction du vrai plateau de jeu. """
        while True:
            try:
                move = int(input(f"🔢 Entrez un numéro de case {env.valid_actions()}: "))
                if int(env.valid_actions()[move]) == 1:
                    return move
                else:
                    print("❌ Case invalide, choisissez une case libre.")
            except ValueError:
                print("❌ Entrez un nombre valide.")
    else:
        valid_moves = np.where(env.valid_actions() == 1)[0]

        if player == "random":
            return random.choice(valid_moves)

        elif player == "smart_random":
            winning_move = is_winning_move(env.player, env.gameboard, env.board_length, env.pattern_length, valid_moves)
            blocking_move = is_winning_move(1 - env.player, env.gameboard, env.board_length, env.pattern_length, valid_moves)

            if winning_move is not None:
                return winning_move
            elif blocking_move is not None:
                return blocking_move
            return random.choice(valid_moves)

        # 5️⃣ Dernier recours : Coup aléatoire
        return random.choice(valid_moves)






# Charger le modèle entraîné
if os.path.exists("../TIC_TAC_TOE_BEST_MODELS/tIC_TAC_TOE_3X3.zip"):
    print("🔄 Chargement du modèle ...")
    model = MaskablePPO.load("../TIC_TAC_TOE_BEST_MODELS/tIC_TAC_TOE_3X3.zip")


if os.path.exists("../MODELS/ppo_tictactoe_14.zip"):
    print("🔄 Chargement du modèle ...")
    model2 = MaskablePPO.load("../MODELS/ppo_tictactoe_14.zip")



def mask_fn(env):
    return env.valid_actions()

env = TicTacToeBaseEnv(board_length=3, pattern_length=3)
obs, _ = env.reset()
done = False

rewards = 0
current_agent = None

while not done:
    current_agent = env.player

    # Sélectionne le bon modèle
    if current_agent == 1:
        print(f"model {model} is playing")
        action_masks = mask_fn(env)  # Récupère le masque d'actions valides
        action, _ = model.predict(obs, action_masks=action_masks, deterministic=True)  # Applique le masque

    else:
        player = "Marc"
        print(f"{player} is playing")
        action = get_player_move(env, None)
        # print(f"{model2} is playing")
        # action_masks = mask_fn(env)  # Récupère le masque d'actions valides
        # action, _ = model2.predict(obs, action_masks=action_masks, deterministic=False)  # Applique le masque


    obs, rewards, done, _, _ = env.step(action)

    env.render()
    sleep(0.5)
    print(f"obs : {obs}, action: {action}, rewards: {rewards}, done: {done}")

if rewards > 0:
    print(f"{current_agent} won")
elif rewards < 0:
    print(f"{env.player} won")
else:
    print(f"draw")



