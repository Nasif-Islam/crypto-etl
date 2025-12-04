import json
import requests
import time
import random
from src.utils.logger import get_logger
from src.utils.timer import timer
from src.utils.config import RAW_DIR, DEFAULT_CURRENCY, DEFAULT_DAYS

logger = get_logger(__name__)

HISTORICAL_API = (
    "https://api.coingecko.com/api/v3/coins/{coin}/ohlc?"
    "vs_currency={currency}&days={days}"
)

BACKUP_FILE = RAW_DIR / "backup_historical_prices.json"


@timer("Extract Historical OHLC Crypto Data")
def extract_historical_ohlc(
    coins: list[dict],
    currency: str = DEFAULT_CURRENCY,
    days: int = DEFAULT_DAYS,
) -> list[dict]:
    """
    Extract historical OHLC data for a list of coins (single currency)
    - Rate-limit protected with random sleep
    - Marks coins as failed if *anything* goes wrong
    - Only overwrites backup if ALL coins succeed
    - Falls back to backup if extraction is incomplete
    """

    logger.info(f"Extracting OHLC for {len(coins)} coins in {currency}, days={days}")

    all_records = []
    failed_coins = []

    try:
        for coin in coins:
            coin_id = coin["id"]
            coin_name = coin["name"]

            # Random delay to avoid rate limiting
            time.sleep(random.uniform(8.0, 16.0))

            url = HISTORICAL_API.format(coin=coin_id, currency=currency, days=days)

            logger.info(f"Fetching OHLC for {coin_id}/{currency}")

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {coin_id}: {e}")
                failed_coins.append(coin_id)
                continue

            try:
                ohlc_data = response.json()
            except ValueError:
                logger.error(f"Invalid JSON for {coin_id}/{currency}")
                failed_coins.append(coin_id)
                continue

            if not isinstance(ohlc_data, list):
                logger.error(f"Unexpected OHLC format for {coin_id}: {ohlc_data}")
                failed_coins.append(coin_id)
                continue

            if len(ohlc_data) < 10:
                logger.warning(
                    f"Insufficient OHLC rows for {coin_id} ({len(ohlc_data)} " f"rows)"
                )
                failed_coins.append(coin_id)
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

        if failed_coins:
            logger.error(f"Extraction incomplete — failed coins: {failed_coins}")

            if BACKUP_FILE.exists():
                logger.warning("Loading previous backup instead of partial data")
                with open(BACKUP_FILE) as f:
                    return json.load(f)

            logger.error("No backup exists — returning EMPTY LIST (safe fallback)")
            return []

        with open(BACKUP_FILE, "w") as f:
            json.dump(all_records, f, indent=2)

        logger.info(f"Backup saved to {BACKUP_FILE}")
        logger.info(f"Extracted {len(all_records)} total OHLC rows")
        return all_records

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

        if BACKUP_FILE.exists():
            logger.warning("Loading backup due to unexpected exception")
            with open(BACKUP_FILE) as f:
                return json.load(f)

        return []
