import sys
from loguru import logger
from core.config import Config

def setup_logger(cfg: Config) -> None:
    log_dir = cfg.project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stderr,
        level=cfg.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.add(
        cfg.project_root / "logs" / "log_{time:DD-MM-YYYY}_{time:HH-mm}.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )