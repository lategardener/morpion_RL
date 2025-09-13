import os

from fastapi import Path

from agents import PPOAgent
from typing import Annotated



def get_agent(board_length: Annotated[int, Path(title="Path int", description="Board lines and columns number", ge=3)],
              win_pattern_length: Annotated[int, Path(title="Path int", description="Number of align pawns to win", ge=3)],
              version: Annotated[int,Path(title="Path int", description="Agent version", ge=1)]):

    agent = f"best_agents/agent_v{version}_{board_length}x{board_length}_{win_pattern_length}.zip"
    if os.path.exists(agent):
        return {"agent": PPOAgent(agent)}
    return None