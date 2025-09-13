from fastapi import FastAPI
from .routers import game

app = FastAPI()
app.include_router(game.router, prefix="/game")
