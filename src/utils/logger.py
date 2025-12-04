import logging
from pathlib import Path
import os
from dotenv import load_dotenv
from src.utils.config import LOG_DIR

# Load environment variables once (safe to call multiple times)
load_dotenv()


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger instance.

    - Logging level is controlled via LOG_LEVEL in .env
    - Logs are written to both console and log file
    - Handlers are added only once per logger name
    """

    # Ensure log directory exists
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Resolve log level from environment - defaults to INFO
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger.setLevel(log_level)

    # File Handler
    file_handler = logging.FileHandler(LOG_DIR / "etl.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
