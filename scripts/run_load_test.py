import pandas as pd
from src.load.load_current_prices import load_current_prices

# create sample df
df = pd.DataFrame(
    {
        "coin_id": ["bitcoin", "ethereum"],
        "currency": ["usd", "usd"],
        "price": [100, 200],
        "market_cap": [1000, 2000],
        "volume_24h": [500, 700],
        "change_24h": [1.2, -0.5],
        "timestamp": ["2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z"],
    }
)


def main():
    print("\nRunning load test...\n")
    path = load_current_prices(df, "test_prices.csv")
    print(f"CSV saved at: {path}")


if __name__ == "__main__":
    main()
