import os
from typing import Annotated

from fastapi import FastAPI, Query, Path

from agents import *
from envs.base_env import *

app = FastAPI()

env: TicTacToeBaseEnv | None  = None
agent: PPOAgent | RandomAgent | SmartRandomAgent | None = None


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/observation")
async def observation():
    global env
    if env is None:
        return None
    return env.get_observation()

@app.get("/agent/{board_length}/{win_pattern_length}/{version}/")
async def get_agent(board_length: Annotated[
                 int,
                 Path(title="Path int",
                       description="Board lines and columns number",
                       ge=3)],
                 win_pattern_length: Annotated[
                     int,
                     Path(title="Path int",
                           description="Number of align pawns to win",
                           ge=3)],
                 version: Annotated[
                     int,
                     Path(title="Path int",
                           description="Agent version",
                           ge=1)]):

    agent = f"best_agents/agent_v{version}_{board_length}x{board_length}_{win_pattern_length}.zip"
    if os.path.exists(agent):
        return {"agent": PPOAgent(agent)}
    return None



