import os

import numpy as np
from fastapi import Path
from agents import PPOAgent, RandomAgent, SmartRandomAgent
from typing import Annotated
import re

from fastapi_app.models.agent_model import GameModeConfigs, AgentConfigs


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

    opponents = [
        {"name": "Random"},
        {"name" : "Smart Random"}
    ]

    pattern = rf"agent_v(\d+)_{board_size}x{board_size}_{pattern_vl}\.zip"
    for agent_path in sorted(os.listdir(agents_dir)):
        match = re.match(pattern, agent_path)
        if match:
            version = match.groups()[0]
            opponents.append({"name" : f"AI agent version {version}", "version": f"{version}"})

    return opponents

def save_agent(app, agent_config:AgentConfigs):
    agent = agent_config.agent
    env = app.state.env
    if agent["name"] == "Random":
        app.state.agent = RandomAgent()
    elif agent["name"] == "Smart Random":
        app.state.agent = SmartRandomAgent()
    else:
        agent_path = f"best_agents/agent_v{agent['version']}_{env.board_length}x{env.board_length}_{env.victory_pattern_length}.zip"
        app.state.agent = PPOAgent(agent_path)


def get_agent_move(app):
    agent = app.state.agent
    env = app.state.env
    valid_moves = np.where(env.valid_actions() == 1)[0]

    if isinstance(agent, RandomAgent):
        return int(agent.play(valid_moves=valid_moves))

    elif isinstance(agent, SmartRandomAgent):
        return int(agent.play(
            player=env.player,
            gameboard=env.gameboard,
            valid_moves=valid_moves,
            board_length=env.board_length,
            pattern_victory_length=env.pattern_victory_length,
        ))

    elif isinstance(agent, PPOAgent):
        obs = env.get_observation()
        return int(agent.play(obs))
    else:
        raise AssertionError("Agent not implemented")