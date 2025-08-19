import argparse
import os
import sys
import numpy as np
from time import sleep

from rich.console import Console
from rich.panel import Panel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from envs import TicTacToeBaseEnv
from agents.ppo_agent import PPOAgent
from agents.random_agent import RandomAgent
from agents.smart_random_agent import SmartRandomAgent
from configs.config import *

console = Console()


def load_agent(agent_type, version=None, board_length=None):
    """
    Load the appropriate agent:
    - "random", "smart_random", "human"
    - "agent": requires version and board_length
    """
    if agent_type == "random":
        return RandomAgent()
    elif agent_type == "smart_random":
        return SmartRandomAgent()
    elif agent_type == "human":
        return "human"
    elif agent_type == "agent":
        if version is None or board_length is None:
            console.print(
                Panel.fit("❌ Missing version or board size for agent.", style="bold red")
            )
            sys.exit(1)

        model_path = f"best_models/model_v{version}_{board_length}x{board_length}.zip"
        if not os.path.exists(model_path):
            console.print(
                Panel.fit(
                    f"❌ Model not found: [yellow]{model_path}[/yellow]",
                    title="Model Error",
                    style="bold red",
                )
            )
            sys.exit(1)
        return PPOAgent(model_path)
    else:
        console.print(
            Panel.fit(f"❌ Unknown agent type: {agent_type}", style="bold red")
        )
        sys.exit(1)


def get_action(env, agent, board_length, pattern_victory_length):
    """Choose the action based on agent type."""
    valid_moves = np.where(env.valid_actions() == 1)[0]

    if agent == "human":
        while True:
            try:
                move = int(input(f"🔢 Enter a valid cell {list(valid_moves)}: "))
                if move in valid_moves:
                    return move
                console.print("❌ Invalid cell.", style="bold red")
            except ValueError:
                console.print("❌ Invalid input.", style="bold red")

    elif isinstance(agent, RandomAgent):
        return agent.play(valid_moves=valid_moves)

    elif isinstance(agent, SmartRandomAgent):
        return agent.play(
            player=env.player,
            gameboard=env.gameboard,
            valid_moves=valid_moves,
            board_length=board_length,
            pattern_victory_length=pattern_victory_length,
        )

    elif isinstance(agent, PPOAgent):
        obs = env.get_observation()
        return agent.play(obs)

    else:
        console.print("❌ Unsupported agent type.", style="bold red")
        sys.exit(1)



def play_game(player1, player2, board_length, pattern_victory_length, render_delay=2):
    """Main loop to play a TicTacToe game."""
    env = TicTacToeBaseEnv(
        board_length=board_length,
        pattern_victory_length=pattern_victory_length,
        render_mode="ansi",  # replace with render_rich if implemented
    )
    obs, _ = env.reset()
    done = False
    players = {0: player1, 1: player2}
    player_types = {
        0: "Human" if player1 == "human" else type(player1).__name__,
        1: "Human" if player2 == "human" else type(player2).__name__
    }

    # Initial display
    console.print(
        Panel(
            f"Game start!\nBoard: {board_length}x{board_length}\nVictory condition: {pattern_victory_length} in a row\nPlayers:\nPlayer 1 : {player_types[0]}\nPlayer 2 : {player_types[1]}",
            title="🎮 TicTacToe",
            style="bold cyan",
            expand=False,
        )
    )

    while not done:
        current_player = env.player
        agent = players[current_player]
        console.print(
            Panel(
                f"{player_types[current_player]} is making a move...",
                style="bold magenta",
                expand=False
            )
        )

        action = get_action(env, agent, board_length, pattern_victory_length)
        obs, reward, done, _, _ = env.step(action)

        env.render(action=action)
        sleep(render_delay)

    # Display result
    if reward > 0:
        winner_type = player_types[1 - env.player]
        console.print(
            Panel(
                f"{winner_type} wins the game!",
                style="bold green",
                expand=False
            )
        )
    elif reward < 0:
        winner_type = player_types[env.player]
        console.print(
            Panel(
                f"{winner_type} wins the game!",
                style="bold green",
                expand=False
            )
        )
    else:
        console.print(
            Panel(
                "It's a draw!",
                style="bold yellow",
                expand=False
            )
        )

def parse_args():
    parser = argparse.ArgumentParser(description="TicTacToe Game Runner")

    parser.add_argument("-p", "--plateau", type=int, required=True, help="Board size (n x n)")
    parser.add_argument("-w", "--win", type=int, required=True, help="Victory pattern length")

    parser.add_argument("-f", "--first", type=str, required=True,
                        choices=["agent", "random", "smart_random", "human"],
                        help="First player type")
    parser.add_argument("-s", "--second", type=str, required=True,
                        choices=["agent", "random", "smart_random", "human"],
                        help="Second player type")

    parser.add_argument("-vf", "--version_first", type=int, help="Version for first player if agent")
    parser.add_argument("-vs", "--version_second", type=int, help="Version for second player if agent")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    board_length = args.plateau
    win_length = args.win

    # Load players
    p1 = load_agent(args.first, args.version_first, board_length)
    p2 = load_agent(args.second, args.version_second, board_length)

    play_game(p1, p2, board_length, win_length)
