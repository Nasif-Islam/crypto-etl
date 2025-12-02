import pandas as pd  # noqa: F401
import os  # noqa: F401
from src.utils.logger import get_logger
from src.utils.config import CLEANED_DIR
from src.utils.timer import timer

logger = get_logger(__name__)


@timer("Load Historical OHLC Data")
def load_historical_ohlc(records: list[dict], filename: str = CLEANED_DIR):
    pass
