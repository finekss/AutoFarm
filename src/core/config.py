from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from omegaconf import OmegaConf

class GameConfig(BaseModel):
    window_title: str = "GameWindow"
    resolution: tuple[int, int] = (640, 480)
    borderless: bool = True


class BotConfig(BaseModel):
    fps_limit: int = 30
    action_delay_min: float = 0.1
    action_delay_max: float = 0.3
    error_retry_count: int = 3


class Config(BaseModel):
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    game: GameConfig = Field(default_factory=GameConfig)
    bot: BotConfig = Field(default_factory=BotConfig)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @field_validator('project_root', mode='before')
    @classmethod
    def resolve_root(cls, v):
        return Path(v).resolve()

    @classmethod
    def load(cls, config_path: Path) -> 'Config':
        cfg = OmegaConf.load(config_path)
        return cls.model_validate(OmegaConf.to_container(cfg, resolve=True))