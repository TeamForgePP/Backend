import logging
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

RESET = "\x1b[0m"
COLORS = {
    "DEBUG": "\x1b[37m",
    "INFO": "\x1b[34m",
    "WARNING": "\x1b[33m",
    "ERROR": "\x1b[31m",
    "CRITICAL": "\x1b[41m",
}


class UTCFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        color = COLORS.get(record.levelname.replace(RESET, ""), "")
        record.levelname = f"{color}{record.levelname}{RESET}"
        return super().format(record)


FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d %(funcName)s | %(message)s"


def setup_logging(config_path: str = "config.toml") -> None:
    # Загружаем конфиг
    cfg = {}
    path = Path(config_path)
    if path.exists():
        with open(path, "rb") as f:
            cfg = tomllib.load(f)

    log_cfg = cfg.get("logging", {})
    level = log_cfg.get("level", "INFO").upper()
    to_file = log_cfg.get("to_file", False)
    log_file = log_cfg.get("file", "logs/app.log")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(UTCFormatter(FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    if to_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(UTCFormatter(FORMAT))
        root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
