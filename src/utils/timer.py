import time
from functools import wraps
from src.utils.logger import get_logger

logger = get_logger(__name__)


def timer(step_name: str):
    """
    Decorator function that calculates time taken for a function to execute
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"===== Starting {step_name} =====")
            start = time.time()

            result = func(*args, **kwargs)

            end = time.time()
            duration = round(end - start, 3)

            logger.info(
                f"===== Completed {step_name} in {duration} seconds" f"=====\n"
            )
            return result

        return wrapper

    return decorator
