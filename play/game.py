import argparse
import os
import sys
import re

import numpy as np
from time import sleep

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from envs import TicTacToeBaseEnv
from agents.ppo_agent import PPOAgent
from agents.random_agent import RandomAgent
from agents.smart_random_agent import SmartRandomAgent
from configs.config import *

console = Console()


def load_agent(agent_type, version=None, board_length=None, victory_pattern_length=None):
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

        if victory_pattern_length is None:
            console.print(
                Panel.fit("❌ Missing victory pattern length.", style="bold red")
            )
            sys.exit(1)

        agent_path = f"best_agents/agent_v{version}_{board_length}x{board_length}_{victory_pattern_length}.zip"
        if not os.path.exists(agent_path):
            console.print(
                Panel.fit(
                    f"❌ agent not found: [yellow]{agent_path}[/yellow]",
                    title="agent Error",
                    style="bold red",
                )
            )
            sys.exit(1)
        return PPOAgent(agent_path)
    else:
        console.print(
            Panel.fit(f"❌ Unknown agent type: {agent_type}", style="bold red")
        )
        sys.exit(1)


def get_action(env, agent, board_length, victory_patteen_length):
    """Choose the action based on agent type."""
    valid_moves = np.where(env.valid_actions() == 1)[0]

    if agent == "human":
        valid_moves_list = [int(i) for i in valid_moves]
        console.print(f"Available moves: {valid_moves}", style="bold cyan")

        while True:
            try:
                move = int(input(f"Enter a valid cell index from the list above: "))
                if move in valid_moves_list:
                    return move
                console.print("❌ Invalid cell. Please choose from the available cells.", style="bold red")
            except ValueError:
                console.print("❌ Invalid input. Please enter a number.", style="bold red")
            except KeyboardInterrupt:
                pass
            return sys.exit

    elif isinstance(agent, RandomAgent):
        return agent.play(valid_moves=valid_moves)

    elif isinstance(agent, SmartRandomAgent):
        return agent.play(
            player=env.player,
            gameboard=env.gameboard,
            valid_moves=valid_moves,
            board_length=board_length,
            pattern_victory_length=victory_patteen_length,
        )

    elif isinstance(agent, PPOAgent):
        obs = env.get_observation()
        return agent.play(obs)

    else:
        console.print("❌ Unsupported agent type.", style="bold red")
        sys.exit(1)


def play_game(player1, player2, board_length, victory_pattern_length, render_delay=2):
    """Main loop to play a TicTacToe game."""
    env = TicTacToeBaseEnv(
        board_length=board_length,
        pattern_victory_length=victory_pattern_length,
        render_mode="ansi",
    )
    obs, _ = env.reset()
    done = False
    players = {0: player1, 1: player2}
    player_types = {
        0: "Human" if player1 == "human" else type(player1).__name__,
        1: "Human" if player2 == "human" else type(player2).__name__
    }

    console.print(
        Panel(
            f"Game start!\nBoard: {board_length}x{board_length}\nVictory condition: {victory_pattern_length} in a row\nPlayers:\nPlayer 1 : {player_types[0]}\nPlayer 2 : {player_types[1]}",
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

        action = int(get_action(env, agent, board_length, victory_pattern_length))

        if not isinstance(action, int):
            console.print(f"\nGame interrupted by user. Exiting the game...", style="bold red")
            return

        obs, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        env.render(action=action)
        sleep(render_delay)

    if reward > 0:
        winner_type = player_types[1 - env.player]
        console.print(Panel(f"{winner_type} wins the game!", style="bold green", expand=False))
    elif reward < 0:
        winner_type = player_types[env.player]
        console.print(Panel(f"{winner_type} wins the game!", style="bold green", expand=False))
    else:
        console.print(Panel("It's a draw!", style="bold yellow", expand=False))


def list_agents():
    """Display available agents in best_agents/ as a table."""
    agents_dir = "best_agents"
    if not os.path.exists(agents_dir):
        console.print(f"[red]⚠️ Directory '{agents_dir}' not found.[/red]")
        return

    agents = [f for f in os.listdir(agents_dir) if f.endswith(".zip")]
    if not agents:
        console.print("[yellow]No agents found in 'best_agents'.[/yellow]")
        return

    table = Table(title="Available PPO agents", show_lines=True)
    table.add_column("agent", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Version", style="magenta")

    pattern = r"agent_v(\d+)_(\d+)x\2_(\d+)\.zip"

    for agent in sorted(agents):
        match = re.match(pattern, agent)
        if match:
            version, board, victory = match.groups()
            description = f"Trained on {board}x{board} board with victory pattern of {victory}"
            table.add_row(agent, description, f"v{version}")
        else:
            table.add_row(agent, "[red]Invalid naming convention[/red]", "-")

    console.print(table)


def parse_args():
    parser = argparse.ArgumentParser(
        description="TicTacToe Game Runner",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Example:
  python play/game.py -p 3 -w 3 -f human -s random
  python play/game.py -p 3 -w 3 -f agent -vf 1 -s smart_random"""
    )

    parser.add_argument("-p", "--plateau", type=int, help="Board size (n x n)")
    parser.add_argument("-w", "--win", type=int, help="Victory pattern length")

    parser.add_argument("-f", "--first", type=str,
                        choices=["agent", "random", "smart_random", "human"],
                        help="First player type")
    parser.add_argument("-s", "--second", type=str,
                        choices=["agent", "random", "smart_random", "human"],
                        help="Second player type")

    parser.add_argument("-vf", "--version_first", type=int, help="Version for first player if agent")
    parser.add_argument("-vs", "--version_second", type=int, help="Version for second player if agent")

    parser.add_argument("-m", "--agents", action="store_true", help="List available PPO agents")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.agents:
        list_agents()
        sys.exit(0)

    if not all([args.plateau, args.win, args.first, args.second]):
        console.print("[yellow]⚠️ Missing arguments. Use -h for help.[/yellow]")
        sys.exit(1)

    board_length = args.plateau
    win_length = args.win

    # Load players
    p1 = load_agent(args.first, args.version_first, board_length, win_length)
    p2 = load_agent(args.second, args.version_second, board_length, win_length)

    play_game(p1, p2, board_length, win_length)
