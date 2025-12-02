import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.extraction.extract_current_prices import (  # noqa: E402
    extract_current_prices,
)
from src.transform.transform_current_prices import (  # noqa: E402
    transform_current_prices,
)
from src.load.load_current_prices import load_current_prices  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402
from src.utils.config import COINS, CURRENCIES  # noqa: E402
from src.utils.timer import timer  # noqa: E402


logger = get_logger(__name__)


@timer("Full ETL Pipeline")
def run_pipeline():
    logger.info("")

    try:
        raw = extract_current_prices(COINS, CURRENCIES)
        df = transform_current_prices(raw, COINS, CURRENCIES)
        load_current_prices(df)

    except Exception:
        logger.error("Pipeline failed", exc_info=True)
        raise

    logger.info("ETL pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()
