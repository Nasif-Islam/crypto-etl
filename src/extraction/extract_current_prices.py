import json
import requests
from src.utils.logger import get_logger
from src.utils.timer import timer
from src.utils.config import RAW_DIR

logger = get_logger(__name__)

API_URL = "https://api.coingecko.com/api/v3/simple/price"
BACKUP_FILE = RAW_DIR / "backup_current_prices.json"


@timer("Current Crypto Price Extraction")
def extract_current_prices(coins: list[dict], currencies: list[str]) -> dict:
    """
    Extract crypto prices from CoinGecko.
    If API request fails, fallback to loading backup JSON.
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
        logger.error("API request timed out after 10 seconds")
        logger.warning("Loading backup file instead...")
        if BACKUP_FILE.exists():
            with open(BACKUP_FILE) as f:
                return json.load(f)
        return {}

    except requests.exceptions.ConnectionError:
        logger.error("Connection error — network/API issue")
        logger.warning("Loading backup file instead...")
        if BACKUP_FILE.exists():
            with open(BACKUP_FILE) as f:
                return json.load(f)
        return {}

    except requests.exceptions.HTTPError as e:
        status = response.status_code
        logger.error(f"HTTP error {status}: {response.reason} - {e}")

        if status == 429:
            logger.error("Rate limit hit (429)")
        elif status == 404:
            logger.error("Endpoint not found (404)")
        elif 500 <= status < 600:
            logger.error("Server error on CoinGecko (5xx)")

        logger.warning("Loading backup file instead...")
        if BACKUP_FILE.exists():
            with open(BACKUP_FILE) as f:
                return json.load(f)
        return {}

    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected request exception: {e}")
        logger.warning("Loading backup file instead...")
        if BACKUP_FILE.exists():
            with open(BACKUP_FILE) as f:
                return json.load(f)
        return {}

    logger.info("API request successful. Decoding JSON...")

    try:
        data = response.json()
    except ValueError:
        logger.error("Failed to decode JSON from API.")
        logger.warning("Loading backup file instead...")
        if BACKUP_FILE.exists():
            with open(BACKUP_FILE) as f:
                return json.load(f)
        return {}

    if not isinstance(data, dict):
        logger.error(f"Unexpected response type: {type(data)}")
        logger.warning("Loading backup file instead...")
        if BACKUP_FILE.exists():
            with open(BACKUP_FILE) as f:
                return json.load(f)
        return {}

    # Save fresh backup
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Backup saved to {BACKUP_FILE}")
    logger.info(f"Extraction successful — received data for {len(data)} coins")

    return data
