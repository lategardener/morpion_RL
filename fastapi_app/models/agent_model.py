from pydantic import BaseModel, Field


class GameModeConfigs(BaseModel):
    mode : str = Field(default="IA Vs Human")

class AgentConfigs(BaseModel):
    agent : dict

