from datetime import datetime, timezone
from src.utils.logger import get_logger

logger = get_logger(__name__)


def transform_current_prices(
    raw_data: dict, coins: list[dict], currencies: list[str]
) -> list[dict]:
    """
    Transform the nested API structure of current price data into a list of
    dictionaries suitable for analysis

    Args:
        raw_data (dict): API response from extract step
        coins (list[dict]): list of coins from config
        currencies (list[str]): list of currencies from config

    Returns:
        list[dict]: Cleaned and flattened list of price records
    """

    logger.info("Starting transformation of current price data...")
    logger.info(
        f"Transforming data for {len(coins)} coins and {len(currencies)} currencies."
    )

    transformed = []
    timestamp = datetime.now(timezone.utc).isoformat()

    # Maps coin id to coin name - constant time lookup
    coin_lookup = {coin["id"]: coin["name"] for coin in coins}

    for coin_id, values in raw_data.items():
        if coin_id not in coin_lookup:
            logger.warning(
                f"Unknown coin ID detected in API response: {coin_id}"
            )

        for currency in currencies:
            price = values.get(currency)
            market_cap = values.get(f"{currency}_market_cap")
            volume_24h = values.get(f"{currency}_24h_vol")
            change_24h = values.get(f"{currency}_24h_change")

            if price is None:
                logger.warning(f"Missing price for {coin_id} in {currency}")

            if market_cap is None:
                logger.debug(f"No market cap data for {coin_id} in {currency}")

            if volume_24h is None:
                logger.debug(f"No 24h volume data for {coin_id} in {currency}")

            if change_24h is None:
                logger.debug(f"No 24h % change for {coin_id} in {currency}")

            record = {
                "coin_id": coin_id,
                "coin_name": coin_lookup.get(coin_id, coin_id.capitalize()),
                "currency": currency,
                "price": price,
                "market_cap": market_cap,
                "volume_24h": volume_24h,
                "change_24h": change_24h,
                "timestamp": timestamp,
            }

            transformed.append(record)

    logger.info(f"Transformation complete - produced {len(transformed)} rows.")

    return transformed
