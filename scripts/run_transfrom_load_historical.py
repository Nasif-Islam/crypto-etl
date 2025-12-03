import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.utils.config import RAW_DIR  # noqa: E402
from src.transform.transform_historical_prices import (  # noqa: E402
    transform_historical_prices,
)
from src.load.load_historical_prices import (  # noqa: E402
    load_historical_prices,
)
from src.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

BACKUP_PATH = RAW_DIR / "backup_historical_prices.json"


def run_transform_and_load():
    logger.info("=== Starting Historical Transform + Load ===")

    # Load backup JSON
    if not BACKUP_PATH.exists():
        raise FileNotFoundError(
            f"Backup historical file not found: {BACKUP_PATH}"
        )

    logger.info(f"Loading backup data from: {BACKUP_PATH}")

    with open(BACKUP_PATH, "r") as f:
        raw_records = json.load(f)

    logger.info(f"Loaded {len(raw_records)} raw OHLC rows from backup")

    # Transform
    transformed_data = transform_historical_prices(raw_records)

    logger.info("Transformation complete")
    logger.info(
        f"Cleaned rows: {len(transformed_data['clean'])}, "
        f"Stats rows: {len(transformed_data['stats'])}"
    )

    # Load
    output_paths = load_historical_prices(transformed_data)

    logger.info("=== Historical Transform + Load Completed ===")
    logger.info(f"Saved OHLC CSV → {output_paths['clean_path']}")
    logger.info(f"Saved Stats CSV → {output_paths['stats_path']}")


if __name__ == "__main__":
    run_transform_and_load()
