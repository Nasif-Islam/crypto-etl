import pandas as pd
import os
from src.utils.logger import get_logger
from src.utils.config import CLEANED_DIR
from src.utils.timer import timer

logger = get_logger(__name__)


@timer("Load Current Crypto Prices")
def load_current_prices(
    df: pd.DataFrame, filename: str = "current_crypto_prices.csv"
) -> str:
    """
    Save the cleaned DataFrame into a CSV file

    Args:
        df (pd.DataFrame): cleaned price data
        filename (str): filename to save in the cleaned directory

    Returns:
        str: full file path of the saved CSV
    """

    logger.info("Starting load step for current price data...")

    if not CLEANED_DIR.exists():
        logger.info(f"Directory {CLEANED_DIR} does not exist. Creating it...")
        CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = CLEANED_DIR / filename

    logger.info(f"Saving DataFrame to: {output_path}")

    try:
        df.to_csv(output_path, index=False)
    except Exception as e:
        logger.error(f"Failed to save CSV to {output_path}: {e}")
        raise

    file_size_kb = os.path.getsize(output_path) / 1024
    logger.info(f"Saved {len(df)} rows. File size: {file_size_kb:.2f} KB")

    logger.info("Load step completed successfully.")

    return str(output_path)
