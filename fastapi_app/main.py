from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents import PPOAgent, RandomAgent, SmartRandomAgent
from envs import TicTacToeBaseEnv
from .routers import game
app = FastAPI()

origins = [
    "http://localhost:5173",  # ton front
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.env: TicTacToeBaseEnv | None  = None
app.state.agent: PPOAgent | RandomAgent | SmartRandomAgent | None = None

app.include_router(game.router, prefix="/game")
