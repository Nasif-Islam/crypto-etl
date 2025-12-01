import pandas as pd
from datetime import datetime, timezone
from src.utils.logger import get_logger
from src.utils.timer import timer

logger = get_logger(__name__)

STANDARD_COLUMNS = [
    "timestamp",
    "coin_id",
    "coin_name",
    "currency",
    "price",
    "market_cap",
    "volume_24h",
    "change_24h",
]


@timer("Transform Current Prices")
def transform_current_prices(
    raw_data: dict, coins: list[dict], currencies: list[str]
) -> pd.DataFrame:
    """
    Clean, validate, and standardize cryptocurrency price data using Pandas.

    Args:
        raw_data (dict): API response from extract step
        coins (list[dict]): list of coins from config
        currencies (list[str]): list of currencies from config

    Returns:
        pd.DataFrame: Cleaned, validated, flattened DataFrame of price records
    """

    logger.info("Starting transformation of current price data...")
    logger.info(
        f"Transforming data for {len(coins)} coins and {len(currencies)} currencies"
    )

    logger.info("Flattening raw JSON into tabular rows")
    rows = []
    timestamp = datetime.now(timezone.utc).isoformat()
    # Maps coin id to coin name - constant time lookup
    coin_lookup = {coin["id"]: coin["name"] for coin in coins}

    for coin_id, values in raw_data.items():
        if coin_id not in coin_lookup:
            logger.warning(
                f"Unknown coin ID detected in API response: {coin_id}"
            )

        for currency in currencies:
            rows.append(
                {
                    "timestamp": timestamp,
                    "coin_id": coin_id,
                    "coin_name": coin_lookup.get(
                        coin_id, coin_id.capitalize()
                    ),
                    "currency": currency,
                    "price": values.get(currency),
                    "market_cap": values.get(f"{currency}_market_cap"),
                    "volume_24h": values.get(f"{currency}_24h_vol"),
                    "change_24h": values.get(f"{currency}_24h_change"),
                }
            )

    df = pd.DataFrame(rows)
    logger.info(f"Initial DataFrame created with {len(df)} rows")

    df.columns = [col.lower().strip() for col in df.columns]
    df = df[STANDARD_COLUMNS]

    numeric_cols = ["price", "market_cap", "volume_24h", "change_24h"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    missing_price_rows = df["price"].isna().sum()
    if missing_price_rows > 0:
        logger.warning(
            f"Dropping {missing_price_rows} rows with missing PRICE (required field)"
        )
        df = df.dropna(subset=["price"])

    df["market_cap"] = df["market_cap"].fillna(0)
    df["volume_24h"] = df["volume_24h"].fillna(0)
    df["change_24h"] = df["change_24h"].fillna(0)

    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} duplicate rows")

    if df["price"].lt(0).any():
        logger.warning("Negative prices detected — investigate API response")

    if df["market_cap"].lt(0).any():
        logger.warning(
            "Negative market caps detected — investigate API response"
        )

    if df["volume_24h"].lt(0).any():
        logger.warning(
            "Negative 24h volume detected — investigate API response"
        )

    df = df.sort_values(["coin_id", "currency"]).reset_index(drop=True)

    logger.info(
        f"Transformation complete. Final dataset contains {len(df)} rows"
    )

    return df
