import os

from fastapi import Path
from agents import PPOAgent
from typing import Annotated

from fastapi_app.models.agent_model import GameModeConfigs


def init_game_mode(app, game_mode: GameModeConfigs) :
    if app.state.game_mode is not None:
        return{
            "message": "Game mode already initialized",
        }
    app.state.game_mode = game_mode.mode
    return {
        "message": "Game mode initialized => Game mode : {}".format(game_mode.mode),
    }

def get_agent(board_length: Annotated[int, Path(title="Path int", description="Board lines and columns number", ge=3)],
              win_pattern_length: Annotated[int, Path(title="Path int", description="Number of align pawns to win", ge=3)],
              version: Annotated[int,Path(title="Path int", description="Agent version", ge=1)]):

    agent = f"best_agents/agent_v{version}_{board_length}x{board_length}_{win_pattern_length}.zip"
    if os.path.exists(agent):
        return {"agent": PPOAgent(agent)}
    return None