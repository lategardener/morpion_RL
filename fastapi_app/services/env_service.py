from envs import TicTacToeBaseEnv
from fastapi_app.models.env_model import EnvConfigs
from fastapi import Request


def observation(app):
    if app.state.env is None:
        return None
    obs = app.state.env.get_observation()
    return {
        "observation": obs["observation"].tolist(),
        "action_mask": obs["action_mask"].tolist(),
        "current_player" : obs["current_player"].item()
    }

def init_env(app, configs: EnvConfigs):

    if app.state.env is not None:
        return{
            "message": "Env already initialized",
        }
    app.state.env = TicTacToeBaseEnv(board_length=configs.board_length,
                           pattern_victory_length=configs.pattern_victory_length,
                           )
    return {
        "message": "Success",
        **configs.model_dump(),
        "gameboard": app.state.env.gameboard.tolist()
    }