# === Game Board Configuration ===

# Size of the square board
DEFAULT_BOARD_LENGTH = 3
# Number of consecutive marks required to win
DEFAULT_PATTERN_VICTORY_LENGTH = 3
# Value representing an empty cell on the board
EMPTY_CELL = 3


# === Game Flow Parameters ===

# Probability that the first player starts the game
DEFAULT_FIRST_PLAY_RATE = 0.5
# Ratio for review or re-evaluation
DEFAULT_REVIEW_RATIO = 0.0
# Default rendering mode
DEFAULT_RENDER_MODE = 'ansi'


# === Reward / Penalty Values for Reinforcement Learning ===

# Reward for winning the game
REWARD_VICTORY = 1.0
# Penalty for missing a winning move opportunity
REWARD_MISSED_WIN = -0.4
# Penalty for allowing the opponent to immediately win
REWARD_ALLOW_OPP_WIN = -0.6
# Bonus for creating a winning threat to be realized next turn
REWARD_CREATE_THREAT = 0.3
# Bonus for blocking a unique winning move by the opponent
REWARD_BLOCK_OPP_WIN = 0.2
