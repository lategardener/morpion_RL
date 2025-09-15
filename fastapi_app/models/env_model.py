from pydantic import BaseModel, Field


class EnvConfigs(BaseModel):
    board_length : int = Field(default=3, ge=3)
    pattern_victory_length : int = Field(default=3, ge=3)

class ActionPlayed(BaseModel):
    action : int