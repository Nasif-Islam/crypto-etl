from src.extraction.extract_current_prices import extract_current_prices
from src.transform.transform_current_prices import transform_current_prices
from src.utils.config import COINS, CURRENCIES


def main():
    print("\nRunning Extract + Transform test...\n")

    # 1. Extract
    raw_data = extract_current_prices(COINS, CURRENCIES)
    print("--- RAW DATA SAMPLE ---")
    first_coin = list(raw_data.keys())[0]
    print(first_coin, ":", raw_data[first_coin])
    print()

    # 2. Transform
    transformed = transform_current_prices(raw_data, COINS, CURRENCIES)

    # 3. Show formatted output
    print("--- TRANSFORMED DATA SAMPLE ---\n")
    for row in transformed[:5]:
        print(row)

    # 4. Validate structure
    print("\nValidating structure...\n")

    if isinstance(transformed, list):
        print("✔ Output is a list")

    if transformed and isinstance(transformed[0], dict):
        print("✔ Each item is a dictionary")

    expected_keys = {
        "coin_id",
        "coin_name",
        "currency",
        "price",
        "market_cap",
        "volume_24h",
        "change_24h",
        "timestamp",
    }

    missing = expected_keys - transformed[0].keys()
    if not missing:
        print("✔ All expected keys present")
    else:
        print("❌ Missing keys:", missing)

    print("\nETL test completed.\n")


if __name__ == "__main__":
    main()
