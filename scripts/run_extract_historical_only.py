import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.extraction.extract_historical_prices import (  # noqa: E402
    extract_historical_ohlc,
)
from src.utils.config import (  # noqa: E402
    COINS,
    DEFAULT_CURRENCY,
    DEFAULT_DAYS,
)
from src.utils.logger import get_logger  # noqa: E402
from src.utils.timer import timer  # noqa: E402

logger = get_logger(__name__)


@timer("Historical Extraction Only")
def run_historical_only():
    logger.info("Running HISTORICAL OHLC extraction ONLY...")

    data = extract_historical_ohlc(COINS, DEFAULT_CURRENCY, DEFAULT_DAYS)

    logger.info(f"Extraction complete. Total rows: {len(data)}")


if __name__ == "__main__":
    run_historical_only()
