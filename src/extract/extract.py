import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def extract_crypto_prices(coins: list[str], currencies: list[str]) -> dict:
    """
    Extract crypto pries from CoinGecko.

    Args:
        coins (list[str]): list of coin dicts from config
        currencies (list[str]): list of fiat currencies e.g. ["gbp", "usd"]

    Returns:
        dict: API response containing price data for each coin
    """

    coin_ids = ",".join([coin["id"] for coin in coins])
    vs_currencies = ",".join(currencies)

    params = {
        "ids": coin_ids,
        "vs_currencies": vs_currencies,
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    logger.info("Starting extraction for coins: {coin_ids}")

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestsException as e:
        logger.error(f"APi request failed: {e}")
        raise

    try:
        data = response.json()
    except ValueError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return data

    if not isinstance(data, dict):
        logger.error(f"Unexpected response type: {type(data)}")
        raise ValueError

    logger.info(f"Extraction successful - received data for {len(data)} coins")

    return data
