from fastapi import APIRouter, Request

from fastapi_app.models.env_model import EnvConfigs
from fastapi_app.services.env_service import init_env, observation

router = APIRouter()

@router.post("/initEnv")
def init_env_route(configs: EnvConfigs, request: Request):
    return init_env(request.app, configs)

@router.get("/observation")
def get_observation_route(request: Request):
    return observation(request.app)