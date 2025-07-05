# 🤖 Tic-Tac-Toe Reinforcement Learning Environment

This project provides a customizable Tic-Tac-Toe (N x N) environment built with [Gymnasium](https://gymnasium.farama.org/) and trained using [Maskable PPO](https://github.com/Stable-Baselines-Team/stable-baselines3-contrib).  
It includes several types of opponents (random, smart, PPO, etc.) and advanced features such as:
- Dynamic board size and win conditions
- Reward shaping based on early victories
- Optional heuristic reward system to guide learning
- Game replay from lost matches
- Win/loss-based opponent selection

---

🇫🇷 Ce projet met en œuvre un environnement d'apprentissage par renforcement pour le jeu du Morpion (Tic-Tac-Toe), compatible avec [Gymnasium](https://gymnasium.farama.org/), et entraîné avec [Maskable PPO](https://github.com/Stable-Baselines-Team/stable-baselines3-contrib).

Fonctionnalités :
- Plateau personnalisable (taille et condition de victoire)
- Récompense ajustée selon la rapidité de la victoire
- Système heuristique optionnel pour guider l’apprentissage
- Rejeu de parties perdues pour réentraînement ciblé
- Sélection des adversaires basée sur leurs statistiques
