from fastapi import FastAPI

from agents import PPOAgent, RandomAgent, SmartRandomAgent
from envs import TicTacToeBaseEnv
from .routers import game

app = FastAPI()

app.state.env: TicTacToeBaseEnv | None  = None
app.state.agent: PPOAgent | RandomAgent | SmartRandomAgent | None = None

app.include_router(game.router, prefix="/game")
