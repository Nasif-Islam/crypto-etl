import pandas as pd
from src.utils.logger import get_logger
from src.utils.timer import timer

logger = get_logger(__name__)


@timer("Transform Historical Crypto Prices")
def transform_historical_prices(raw_records: list[dict]):
    """
    Clean and enrich historical OHLC crypto price data

    Returns:
        {
            "clean": ohlc_df,
            "stats": stats_table
        }
    """

    logger.info("Starting transformation of historical OHLC data...")

    if not raw_records:
        logger.warning("No historical records received; returning empty DataFrames")
        return {"clean": pd.DataFrame(), "stats": pd.DataFrame()}

    ohlc_df = pd.DataFrame(raw_records)
    logger.info(f"Initial DataFrame created with {len(ohlc_df)} rows")

    # Convert timestamp from ms to datetime
    ohlc_df["timestamp"] = pd.to_datetime(ohlc_df["timestamp_ms"], unit="ms")
    # Sort chronologically
    ohlc_df = ohlc_df.sort_values(["coin_id", "timestamp"]).reset_index(drop=True)
    logger.info("Timestamps converted and sorted")

    # Remove duplicates & ensure valid OHLC rows
    ohlc_df = ohlc_df.drop_duplicates(subset=["coin_id", "timestamp"])
    ohlc_df = ohlc_df.dropna(subset=["open", "high", "low", "close"])

    # Enforce numeric types for OHLC values
    ohlc_columns = ["open", "high", "low", "close"]
    ohlc_df[ohlc_columns] = ohlc_df[ohlc_columns].apply(pd.to_numeric, errors="coerce")
    ohlc_df = ohlc_df.dropna(subset=ohlc_columns)

    ohlc_df["pct_change"] = ohlc_df.groupby("coin_id")["close"].pct_change()

    ohlc_df["rolling_7d"] = ohlc_df.groupby("coin_id")["close"].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    ohlc_df["rolling_30d"] = ohlc_df.groupby("coin_id")["close"].transform(
        lambda x: x.rolling(30, min_periods=1).mean()
    )

    # Normalized close price (for coin comparisons)
    ohlc_df["normalized_close"] = ohlc_df.groupby("coin_id")["close"].transform(
        lambda x: x / x.iloc[0] if x.iloc[0] != 0 else x
    )

    stats_table = (
        ohlc_df.groupby("coin_id")
        .agg(
            coin_name=("coin_name", "first"),
            max_close=("close", "max"),
            min_close=("close", "min"),
            mean_volatility=("pct_change", "mean"),
            total_return=(
                "close",
                lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0],
            ),
        )
        .reset_index()
    )

    logger.info("Historical transformation complete")

    return {
        "clean": ohlc_df,
        "stats": stats_table,
    }
