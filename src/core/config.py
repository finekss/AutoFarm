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

class PerceptionConfig(BaseModel):
    capture_region: tuple[int, int, int, int] = (0, 0, 640, 480)
    target_fps: int = 30
    yolo_model_path: str = "models/yolo/game_v1.onnx"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.5
    device: str = "cuda"

class Config(BaseModel):
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    game: GameConfig = Field(default_factory=GameConfig)
    bot: BotConfig = Field(default_factory=BotConfig)
    perception: PerceptionConfig = Field(default_factory=PerceptionConfig)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @field_validator('project_root', mode='before')
    @classmethod
    def resolve_root(cls, v):
        return Path(v).resolve()

    @classmethod
    def load(cls, config_path: Path) -> 'Config':
        cfg = OmegaConf.load(config_path)
        return cls.model_validate(OmegaConf.to_container(cfg, resolve=True))