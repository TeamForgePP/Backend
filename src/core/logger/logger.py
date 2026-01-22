import logging
import sys
import tomllib
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RESET = "\x1b[0m"
COLORS: Mapping[str, str] = {
    "DEBUG": "\x1b[37m",
    "INFO": "\x1b[34m",
    "WARNING": "\x1b[33m",
    "ERROR": "\x1b[31m",
    "CRITICAL": "\x1b[41m",
}


class UTCFormatter(logging.Formatter):
    def __init__(self, *, use_color: bool = True) -> None:
        super().__init__()
        self.use_color = use_color

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record)
        level = record.levelname

        level_padded = f"{level:<7}"
        if self.use_color:
            color = COLORS.get(level)
            if color:
                level_padded = f"{color}{level_padded}{RESET}"

        name = record.name
        message = record.getMessage()

        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return f"{ts} | {level_padded} | {name} | {message}"


def setup_logging(config_path: str = "config.toml") -> None:
    cfg: dict[str, Any] = {}
    path = Path(config_path)
    if path.exists():
        with path.open("rb") as f:
            cfg = tomllib.load(f)

    logging_cfg = cfg.get("logging", {})
    if not isinstance(logging_cfg, dict):
        logging_cfg = {}

    level_name = str(logging_cfg.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(UTCFormatter(use_color=True))
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
        lg.setLevel(level)

    logging.captureWarnings(True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
