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
    def __init__(self, *, use_color: bool = True) -> None:
        super().__init__()
        self.use_color = use_color

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        # время
        ts = self.formatTime(record)

        # уровень
        level = record.levelname
        level_padded = f"{level:<7}"  # фикс ширина

        if self.use_color:
            color = COLORS.get(level, "")
            if color:
                level_padded = f"{color}{level_padded}{RESET}"

        name_padded = f"{record.name:<20}"
        line_padded = f"{record.lineno:<5}"
        func_padded = f"{record.funcName:<20}"

        message = record.getMessage()

        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"

        if record.stack_info:
            message = f"{message}\n{record.stack_info}"

        return f"{ts} | {level_padded} | {name_padded}:{line_padded} {func_padded} | {message}"


def setup_logging(config_path: str = "config.toml") -> None:
    cfg: dict = {}
    path = Path(config_path)
    if path.exists():
        with open(path, "rb") as f:
            cfg = tomllib.load(f)

    log_cfg = cfg.get("logging", {})
    level = str(log_cfg.get("level", "INFO")).upper()
    to_file = bool(log_cfg.get("to_file", False))
    log_file = str(log_cfg.get("file", "logs/app.log"))

    stream_formatter = UTCFormatter(use_color=True)
    file_formatter = UTCFormatter(use_color=False)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(stream_formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(stream_handler)

    # файл
    if to_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

    logging.captureWarnings(True)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        lg = logging.getLogger(logger_name)
        lg.handlers.clear()
        lg.propagate = True
        lg.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
