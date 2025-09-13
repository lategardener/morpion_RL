from pydantic import BaseModel


class EnvConfigs(BaseModel):
    board_length : int
    pattern_victory_length : int
    victory_reward : int
