import os
from typing import Annotated

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel

from agents import *
from envs.base_env import *

app = FastAPI()

env: TicTacToeBaseEnv | None  = None
agent: PPOAgent | RandomAgent | SmartRandomAgent | None = None

class EnvConfigs(BaseModel):
    board_length : int
    pattern_victory_length : int
    victory_reward : int


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/observation")
async def observation():
    global env
    if env is None:
        return None
    obs = env.get_observation()
    return {
        "observation": obs["observation"].tolist(),
        "action_mask": obs["action_mask"].tolist(),
        "current_player" : obs["current_player"].item()
    }

@app.post("/initEnv")
async def init_env(configs: EnvConfigs):
    global env
    if env is not None:
        return{
            "message": "Env already initialized",
        }
    env = TicTacToeBaseEnv(board_length=configs.board_length,
                           pattern_victory_length=configs.pattern_victory_length,
                           victory_reward=configs.victory_reward
                           )
    return {
        "message": "Success",
        "board_length": env.board_length,
        "pattern_victory_length": env.pattern_victory_length,
        "victory_reward": env.victory_reward,
        "player": env.player,
        "gameboard": env.gameboard.tolist()
    }

@app.get("/agent/{board_length}/{win_pattern_length}/{version}/")
async def get_agent(board_length: Annotated[int, Path(title="Path int", description="Board lines and columns number", ge=3)],
                    win_pattern_length: Annotated[int, Path(title="Path int", description="Number of align pawns to win", ge=3)],
                    version: Annotated[int,Path(title="Path int", description="Agent version", ge=1)]):

    agent = f"best_agents/agent_v{version}_{board_length}x{board_length}_{win_pattern_length}.zip"
    if os.path.exists(agent):
        return {"agent": PPOAgent(agent)}
    return None



