import requests
from src.utils.logger import get_logger
from src.utils.config import COINS, CURRENCIES, DEFAULT_DAYS

logger = get_logger(__name__)

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def extract_crypto_prices(coins: list[str], currencies: list[str]) -> dict:
    """
    Extract crypto pries from CoinGecko.

    Args:
        coins (list[str]): list of coin dicts from config
        currencies (list[str]): fiat currencies like ["gbp", "usd"]

    Returns:
        dict: API response containing price data for each coin
    """

    coin_ids = ",".join([coin["id"] for coin in COINS])
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": "coin_ids",
        "vs_currencies": vs_currencies,
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json
        logger.info("Extraction successful - received data for %d coins", len(data))
        return data
    except requests.exceptions.RequestException as e:
        logger.error("Extraction failed %s", e)
        raise
