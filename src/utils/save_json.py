import json
from src.utils.logger import get_logger
from src.utils.config import RAW_DIR

logger = get_logger(__name__)


def save_raw_json(
    data: dict, filename: str = "backup_current_prices.json"
) -> str:
    """
    Save raw JSON data to the data/raw folder
    Can be run manually to update the backup with the latest prices

    Args:
        data (dict): Raw extracted data.
        filename (str): File name for the backup.

    Returns:
        str: Path where the backup file was saved.
    """

    output_path = RAW_DIR / filename

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"Backup JSON saved/updated at: {output_path}")
    return str(output_path)
