"""Central logging configuration."""
from __future__ import annotations
import logging
from pathlib import Path
from src.config import Settings

def configure_logging(settings: Settings) -> logging.Logger:
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("supportpearlz")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
