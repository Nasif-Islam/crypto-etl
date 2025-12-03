from src.utils.logger import get_logger
from src.utils.config import CLEANED_DIR
from src.utils.timer import timer

logger = get_logger(__name__)


@timer("Load Historical Crypto Prices")
def load_historical_prices(
    data: dict,
    clean_filename: str = "historical_crypto_prices.csv",
    stats_filename: str = "historical_crypto_stats.csv",
) -> dict:
    """
    Save the transformed historical OHLC data and stats table into CSV files

    Args:
        data (dict): {
            "clean": pd.DataFrame,
            "stats": pd.DataFrame
        }
        clean_filename (str): output CSV for the cleaned OHLC dataset
        stats_filename (str): output CSV for the summary stats table

    Returns:
        dict: {
            "clean_path": str,
            "stats_path": str
        }
    """

    logger.info("Starting load step for historical OHLC data...")

    if "clean" not in data or "stats" not in data:
        raise ValueError(
            "Input to load_historical_prices must contain 'clean' & 'stats' dfs"
        )

    clean_df = data["clean"]
    stats_df = data["stats"]

    if not CLEANED_DIR.exists():
        logger.info(f"Directory {CLEANED_DIR} does not exist. Creating it...")
        CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    clean_path = CLEANED_DIR / clean_filename
    stats_path = CLEANED_DIR / stats_filename

    # Convert cleaned OHLC dataframe to csv
    try:
        clean_df.to_csv(clean_path, index=False)
        logger.info(
            f"Saved CLEAN OHLC data → {clean_path} ({len(clean_df)} rows)"
        )
    except Exception as e:
        logger.error(f"Failed to write cleaned OHLC CSV: {e}")
        raise

    # Convert stats dataframe to csv
    try:
        stats_df.to_csv(stats_path, index=False)
        logger.info(f"Saved STATS table → {stats_path} ({len(stats_df)} rows)")
    except Exception as e:
        logger.error(f"Failed to write stats CSV: {e}")
        raise

    logger.info("Historical price load step completed successfully.")

    return {
        "clean_path": str(clean_path),
        "stats_path": str(stats_path),
    }
