from fastapi import APIRouter, Request

from fastapi_app.models.agent_model import GameModeConfigs
from fastapi_app.models.env_model import EnvConfigs, ActionPlayed
from fastapi_app.services.agent_service import init_game_mode, get_available_opponents
from fastapi_app.services.env_service import init_env, observation

router = APIRouter()

@router.post("/initEnv")
def init_env_route(configs: EnvConfigs, request: Request):
    return init_env(request.app, configs)

@router.post("/initGameMode")
def init_game_mode_route(request: Request, configs: GameModeConfigs):
    return init_game_mode(request.app, configs)

@router.post("/actionPlayed")
def action_played(request: Request, action: ActionPlayed):
    return action_played(request.app, action)

@router.get("/observation")
def get_observation_route(request: Request):
    return observation(request.app)

@router.get("/opponents")
def get_available_opponents_route(request: Request):
    return get_available_opponents(request.app)