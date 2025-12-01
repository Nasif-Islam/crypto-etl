from src.extraction.extract_current_prices import extract_crypto_prices
from src.utils.save_json import save_raw_json
from src.utils.config import COINS, CURRENCIES
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("=== Starting Backup JSON Update ===")

    try:
        raw_data = extract_crypto_prices(COINS, CURRENCIES)
        logger.info("Successfully extracted current crypto prices.")
    except Exception as e:
        logger.error(f"Failed to extract data from API: {e}")
        return

    try:
        path = save_raw_json(raw_data, "backup_current_prices.json")
        logger.info(f"Backup successfully saved to: {path}")
    except Exception as e:
        logger.error(f"Failed to save backup JSON: {e}")
        return

    logger.info("=== Backup JSON Update Complete ===")


if __name__ == "__main__":
    main()
