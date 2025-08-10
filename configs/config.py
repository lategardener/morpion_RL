# Game parameters
DEFAULT_PATTERN_VICTORY_LENGTH = 5
DEFAULT_BOARD_LENGTH = 9
EMPTY_CELL = 3
DEFAULT_FIRST_PLAY_RATE = 0.5
DEFAULT_REVIEW_RATIO = 0.0
DEFAULT_RENDER_MODE = 'ansi'

# reward for a win
REWARD_VICTORY = 1.0

# penalty for missing a winning move
REWARD_MISSED_WIN = -0.4

# penalty for allowing the opponent to win immediately
REWARD_ALLOW_OPP_WIN = -0.6

# bonus for creating a winning threat on the next turn
REWARD_CREATE_THREAT = 0.3

# bonus for blocking a unique opponent winning move
REWARD_BLOCK_OPP_WIN = 0.2

