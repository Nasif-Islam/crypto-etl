import logging
from pathlib import Path
from src.utils.config import LOG_DIR


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger instance for any module
    Logs are written to both console and log file

    Args:
        name (str): the module name using the logger

    Returns:
        logging.Logger: configured logger instance
    """

    # Checks that the log file exists
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevents duplicate log messages
    if logger.hasHandlers():
        return logger

    file_handler = logging.FileHandler(LOG_DIR / "etl.log")
    file_format = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(file_format)

    console_handler = logging.StreamHandler()
    console_format = logging.Formatter("%(levelname)s | %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
