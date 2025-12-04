import logging
from pathlib import Path
import os
from dotenv import load_dotenv
from src.utils.config import LOG_DIR


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a logger instance
    - Automatically loads .env.dev or .env.test depending on ENV value
    - Logging level & log file output is set via in .env
    - Logs are written to both console and log file
    - Handlers are added only once per logger name
    """

    # Determine which .env file to load (default = dev)
    env_name = os.getenv("ENV", "dev")

    env_file = ".env.test" if env_name.lower() == "test" else ".env.dev"

    # Load the selected env file
    load_dotenv(env_file)

    # Ensure logs folder exists
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    # Configure log level from .env
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Configure output log file, depending on environment
    log_file_name = os.getenv("LOG_FILE", "etl.log")
    log_path = LOG_DIR / log_file_name

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_format = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter("%(levelname)s | %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
