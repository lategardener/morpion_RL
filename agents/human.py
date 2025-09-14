import shutil
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text


class Human:
    """
    Human player that can work in two modes:
    - 'console': ask the user for input interactively via terminal
    - 'api': receive the move as an external parameter (e.g., API request)
    """

    def __init__(self, mode="console"):
        """
        Initialize the Human agent.

        Parameters:
        - mode (str): "console" for CLI interaction, "api" for external input
        """
        self.mode = mode

    def play(self, valid_moves, console=None, user_input=None):
        """
        Select a move depending on the mode.

        Parameters:
        - valid_moves (list[int]): list of valid moves available.
        - console: Rich console instance (only used in console mode).
        - user_input (int): predefined move (only used in API mode).

        Returns:
        - int: a valid move chosen by the human player.

        Raises:
        - ValueError: if API mode receives an invalid move.
        """
        if self.mode == "api":
            # API mode: validate external input
            if user_input is None or user_input not in valid_moves:
                raise ValueError("Invalid move provided by API client")
            return user_input

        elif self.mode == "console":
            # Console mode: ask the player to input a move manually
            console.print(
                Align.center(
                    Panel(
                        f"Available moves: {valid_moves}",
                        style="bold cyan",
                        expand=False,
                    )
                )
            )
            while True:
                try:
                    columns = shutil.get_terminal_size().columns
                    prompt_text = "Enter a valid cell index: "

                    padding = (columns - len(prompt_text)) // 2
                    prompt = " " * padding + prompt_text

                    move = int(input(prompt))
                    if move in valid_moves:
                        return move

                    console.print(
                        Align.center(
                            Panel(
                                "❌ Invalid cell. Please try again.",
                                style="bold red",
                                expand=False,
                            )
                        )
                    )
                except ValueError:
                    console.print(
                        Align.center(
                            Panel(
                                "❌ Invalid input. Please enter a number.",
                                style="bold red",
                                expand=False,
                            )
                        )
                    )
                except KeyboardInterrupt:
                    return sys.exit
