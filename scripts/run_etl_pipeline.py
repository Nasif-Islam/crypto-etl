from src.utils.logger import get_logger
from src.utils.timer import timer

from src.extraction.extract_current_prices import extract_current_prices
from src.transform.transform_current_prices import transform_current_prices
from src.load.load_current_prices import load_current_prices

from src.extraction.extract_historical_prices import extract_historical_ohlc
from src.transform.transform_historical_prices import (
    transform_historical_prices,
)
from src.load.load_historical_prices import load_historical_prices

from src.utils.config import COINS, CURRENCIES, DEFAULT_CURRENCY, DEFAULT_DAYS


logger = get_logger(__name__)


@timer("Current Price ETL")
def run_current_etl():
    logger.info("===== Running Current Price ETL =====")

    raw_current = extract_current_prices(COINS, CURRENCIES)

    df_current = transform_current_prices(raw_current)

    output_path = load_current_prices(df_current)

    logger.info(f"Current price ETL completed - data saved to {output_path}")


@timer("Historical Price ETL")
def run_historical_etl():
    logger.info("===== Running Historical Price ETL =====")

    raw_historical = extract_historical_ohlc(
        COINS, DEFAULT_CURRENCY, DEFAULT_DAYS
    )

    transformed = transform_historical_prices(raw_historical)

    output_paths = load_historical_prices(transformed)

    logger.info(
        f"Historical price ETL completed - data saved to  "
        f"{output_paths['clean_path']} and {output_paths['stats_path']}"
    )


@timer("Full ETL Pipeline")
def run_full_pipeline():
    logger.info("===== STARTING FULL CRYPTO ETL PIPELINE =====")

    run_current_etl()
    run_historical_etl()

    logger.info("=== FULL ETL PIPELINE FINISHED SUCCESSFULLY ===")


def main():
    run_full_pipeline()


if __name__ == "__main__":
    main()
