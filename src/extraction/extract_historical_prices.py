import json
import requests
import time
import random
from src.utils.logger import get_logger
from src.utils.timer import timer
from src.utils.config import RAW_DIR

logger = get_logger(__name__)

HISTORICAL_API = (
    "https://api.coingecko.com/api/v3/coins/{coin}/ohlc?"
    "vs_currency={currency}&days={days}"
)

BACKUP_FILE = RAW_DIR / "backup_historical_prices.json"


@timer("Extract Historical OHLC Crypto Data")
def extract_historical_ohlc(
    coins: list[dict], currencies: list[str], days: int
):
    """
    Extract historical OHLC data and save backup JSON only once.
    If no data is extracted and a backup exists, load backup instead.
    """

    logger.info(
        f"Extracting historical OHLC for {len(coins)} coins, "
        f"{len(currencies)} currencies, over {days} days"
    )

    all_records = []

    try:
        for coin in coins:
            coin_id = coin["id"]
            coin_name = coin["name"]

            for currency in currencies:
                logger.info(f"Fetching OHLC for {coin_id} in {currency}")

                time.sleep(random.uniform(1.5, 3.0))  # Prevents rate limiting

                url = HISTORICAL_API.format(
                    coin=coin_id, currency=currency, days=days
                )

                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    logger.error(
                        f"Request failed for {coin_id}/{currency}: {e}"
                    )
                    continue

                try:
                    ohlc_data = response.json()
                except ValueError:
                    logger.error(f"Invalid JSON for {coin_id} in {currency}")
                    continue

                for row in ohlc_data:
                    if len(row) != 5:
                        logger.warning(f"Bad OHLC row for {coin_id}: {row}")
                        continue

                    ts_ms, open_, high_, low_, close_ = row

                    all_records.append(
                        {
                            "coin_id": coin_id,
                            "coin_name": coin_name,
                            "currency": currency,
                            "timestamp_ms": ts_ms,
                            "open": open_,
                            "high": high_,
                            "low": low_,
                            "close": close_,
                        }
                    )

        # Uses backup data if no data is extracted
        if not all_records:
            if BACKUP_FILE.exists():
                logger.warning("No OHLC data extracted — loading backup")
                with open(BACKUP_FILE) as f:
                    return json.load(f)
            logger.error("No OHLC data extracted and no backup available")
            return []

        # Saves backup if one doesn't exist
        if not BACKUP_FILE.exists():
            with open(BACKUP_FILE, "w") as f:
                json.dump(all_records, f, indent=2)
            logger.info(f"Backup saved to {BACKUP_FILE}")

        logger.info(f"Extracted {len(all_records)} total OHLC rows.")
        return all_records

    except Exception as e:
        logger.error(f"Unexpected error during OHLC extraction: {e}")

        if BACKUP_FILE.exists():
            logger.warning("Loading backup after unexpected exception")
            with open(BACKUP_FILE) as f:
                return json.load(f)

        return []
