import requests
import pandas as pd
from src.utils.logger import get_logger
from src.utils.timer import timer

logger = get_logger(__name__)

HISTORICAL_API = (
    "https://api.coingecko.com/api/v3/coins/{coin}/ohlc?"
    "vs_currency={currency}&days={days}"
)


@timer("Extract Historical OHLC Crypto Data")
def extract_historical_ohlc(
    coins: list[dict], currencies: list[str], days: int
):
    """
    Extract historical OHLC data for multiple coins and currencies

    Args:
        coins (list[dict]): List of coin dicts from config file
        currencies (list[str]): List of fiat currencies,
        e.g. ["gbp", "usd", "eur"]
        days (int): Number of days of OHLC data to fetch (default = 365)

    Returns:
        list[dict]: Flattened OHLC rows for all coin/currency combinations
    """

    logger.info(
        f"Extracting historical OHLC for {len(coins)} coins, "
        f"{len(currencies)} currencies, over {days} days"
    )

    all_records = []

    for coin in coins:
        coin_id = coin["id"]
        coin_name = coin["name"]

        for currency in currencies:
            logger.info(f"Fetching OHLC for {coin_id} in {currency}")

            url = HISTORICAL_API.format(
                coin=coin_id, currency=currency, days=days
            )
            response = requests.get(url)

            if response.status_code != 200:
                logger.error(
                    f"Failed OHLC request for {coin_id} in {currency}"
                )
                continue

            try:
                ohlc_data = response.json()
            except Exception:
                logger.error(
                    f"Could not decode OHLC JSON for {coin_id} in {currency}"
                )
                continue

            # Each row is [timestamp_ms, open, high, low, close]
            for row in ohlc_data:
                if len(row) != 5:
                    logger.warning(
                        f"Incorrect OHLC row format for {coin_id}: {row}"
                    )
                    continue

                ts_ms, open_, high_, low_, close_ = row

                all_records.append(
                    {
                        "coin_id": coin_id,
                        "coin_name": coin_name,
                        "currency": currency,
                        "timestamp": pd.to_datetime(ts_ms, unit="ms"),
                        "open": open_,
                        "high": high_,
                        "low": low_,
                        "close": close_,
                    }
                )

    logger.info(f"Extracted {len(all_records)} total OHLC rows.")
    return all_records
