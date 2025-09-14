import os

from fastapi import Path
from agents import PPOAgent
from typing import Annotated
import re

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

def get_available_opponents(app):
    board_size = app.state.env.board_length
    pattern_vl = app.state.env.pattern_victory_length
    agents_dir = "best_agents"
    if not os.path.exists(agents_dir):
        raise AssertionError("Agent dir not found")

    opponents = {
        "Random": {},
        "Smart Random": {},
    }

    pattern = rf"agent_v(\d+)_{board_size}x{board_size}_{pattern_vl}\.zip"
    for agent_path in sorted(os.listdir(agents_dir)):
        match = re.match(pattern, agent_path)
        if match:
            version = match.groups()[0]
            opponents[f"AI agent version {version}"] = {"version": f"{version}"}

    return opponents

def get_agent(board_length: Annotated[int, Path(title="Path int", description="Board lines and columns number", ge=3)],
              win_pattern_length: Annotated[int, Path(title="Path int", description="Number of align pawns to win", ge=3)],
              version: Annotated[int,Path(title="Path int", description="Agent version", ge=1)]):

    agent = f"best_agents/agent_v{version}_{board_length}x{board_length}_{win_pattern_length}.zip"
    if os.path.exists(agent):
        return {"agent": PPOAgent(agent)}
    return None