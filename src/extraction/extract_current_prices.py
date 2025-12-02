import requests
from src.utils.logger import get_logger
from src.utils.timer import timer

logger = get_logger(__name__)

API_URL = "https://api.coingecko.com/api/v3/simple/price"


@timer("Current Crypto Price Extraction")
def extract_current_prices(coins: list[dict], currencies: list[str]) -> dict:
    """
    Extract crypto prices from CoinGecko

    Args:
        coins (list[dict]): list of coin dicts from config
        currencies (list[str]): list of fiat currencies e.g. ["gbp", "usd"]

    Returns:
        dict: API response containing price data for each coin
    """

    coin_ids = ",".join([coin["id"] for coin in coins])
    vs_currencies = ",".join(currencies)

    logger.info("Preparing API request...")
    logger.info(f"Coins requested: {coin_ids}")
    logger.info(f"Currencies requested: {vs_currencies}")

    params = {
        "ids": coin_ids,
        "vs_currencies": vs_currencies,
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
    }

    logger.info("Sending request to CoinGecko API...")
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("API request timed out after 10 seconds.")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("Connection error — check your network or API status.")
        raise
    except requests.exceptions.HTTPError as e:
        status = response.status_code
        logger.error(f"HTTP error {status}: {response.reason} - {e}")
        if status == 429:
            logger.error(
                "Rate limit hit — CoinGecko API throttled the request."
            )
        elif status == 404:
            logger.error("Endpoint not found — check API URL.")
        elif 500 <= status < 600:
            logger.error("Server error on CoinGecko’s side.")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected request exception occurred: {e}")
        raise
    else:
        logger.info("API request successful.")

    logger.info("Decoding JSON response...")
    try:
        data = response.json()
    except ValueError as e:
        logger.error(f"Failed to decode JSON: {e}")
        raise

    if not isinstance(data, dict):
        logger.error(f"Unexpected response type: {type(data)}")
        raise ValueError("API returned unexpected JSON format")

    logger.info(f"Extraction successful - received data for {len(data)} coins")

    return data
