import numpy as np
from time import sleep
from envs.base_env import TicTacToeBaseEnv
from agents.ppo_agent import PPOAgent
from agents.random_agent import RandomAgent
from agents.smart_random_agent import SmartRandomAgent
from configs.config import *

def load_agent(agent_type):
    """
    Load the appropriate agent based on type string or model path.
    """
    if agent_type == "random":
        return RandomAgent()
    elif agent_type == "smart_random":
        return SmartRandomAgent()
    elif agent_type == "human":
        return "human"
    elif os.path.exists(agent_type):
        return PPOAgent(agent_type)
    else:
        raise ValueError(f"❌ Unknown agent type or invalid model path: {agent_type}")


def get_action(env, agent):
    """
    Determine the action to take based on the type of agent.
    """
    valid_moves = np.where(env.valid_actions() == 1)[0]

    if agent == "human":
        while True:
            try:
                move = int(input(f"🔢 Enter a valid cell {list(valid_moves)}: "))
                if move in valid_moves:
                    return move
                print("❌ Invalid cell.")
            except ValueError:
                print("❌ Invalid input.")

    elif isinstance(agent, RandomAgent):
        return agent.play(valid_moves=valid_moves)

    elif isinstance(agent, SmartRandomAgent):
        return agent.play(player=env.player, gameboard=env.gameboard, valid_moves=valid_moves)

    elif isinstance(agent, PPOAgent):
        obs = env.get_observation()
        return agent.play(obs)

    else:
        raise TypeError("❌ Unsupported agent type.")


def play_game(player1_type, player2_type, board_length=DEFAULT_BOARD_LENGTH, pattern_victory_length=DEFAULT_PATTERN_VICTORY_LENGTH, render_delay=1.5):
    """
    Main loop to play a game between two agents.
    """
    env = TicTacToeBaseEnv(board_length=board_length, pattern_victory_length=pattern_victory_length)
    obs, _ = env.reset()
    done = False

    players = {
        0: load_agent(player1_type),
        1: load_agent(player2_type)
    }

    while not done:
        current_player = env.player
        agent = players[current_player]
        print(f"\n🔁 Player {current_player} ({type(agent).__name__}) is playing...")

        action = get_action(env, agent)
        obs, reward, done, _, _ = env.step(action)

        env.render(action=action)
        sleep(render_delay)

    if reward > 0:
        print(f"🎉 Player {1 - env.player} wins!")
    elif reward < 0:
        print(f"🎉 Player {env.player} wins!")
    else:
        print("🤝 It's a draw.")


# Example usage
if __name__ == "__main__":
    play_game(
        player1_type="smart_random",
        player2_type="../models/models_9_5/model_9_5_1.zip"
    )
