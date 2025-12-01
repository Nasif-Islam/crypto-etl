import pandas as pd
import pytest
from src.transform.transform_current_prices import transform_current_prices

# Sample input for testing
MOCK_COINS = [
    {"id": "bitcoin", "name": "Bitcoin"},
    {"id": "ethereum", "name": "Ethereum"},
]

MOCK_CURRENCIES = ["gbp", "usd"]

MOCK_RAW_DATA = {
    "bitcoin": {
        "gbp": 100,
        "gbp_market_cap": 1000,
        "gbp_24h_vol": 500,
        "gbp_24h_change": -1.2,
        "usd": 120,
        "usd_market_cap": 1200,
        "usd_24h_vol": 600,
        "usd_24h_change": -1.5,
    },
    "ethereum": {
        "gbp": 200,
        "gbp_market_cap": 2000,
        "gbp_24h_vol": 700,
        "gbp_24h_change": -2.0,
        "usd": 240,
        "usd_market_cap": 2400,
        "usd_24h_vol": 800,
        "usd_24h_change": -2.2,
    },
}


def test_returns_dataframe():
    df = transform_current_prices(MOCK_RAW_DATA, MOCK_COINS, MOCK_CURRENCIES)
    assert isinstance(df, pd.DataFrame)


def test_correct_number_of_rows():
    df = transform_current_prices(MOCK_RAW_DATA, MOCK_COINS, MOCK_CURRENCIES)
    # 2 coins × 2 currencies = 4 rows
    assert len(df) == 4


def test_required_columns_present():
    df = transform_current_prices(MOCK_RAW_DATA, MOCK_COINS, MOCK_CURRENCIES)

    expected_columns = [
        "timestamp",
        "coin_id",
        "coin_name",
        "currency",
        "price",
        "market_cap",
        "volume_24h",
        "change_24h",
    ]

    for col in expected_columns:
        assert col in df.columns


def test_values_correctly_assigned():
    df = transform_current_prices(MOCK_RAW_DATA, MOCK_COINS, MOCK_CURRENCIES)

    btc_gbp_row = df[
        (df["coin_id"] == "bitcoin") & (df["currency"] == "gbp")
    ].iloc[0]

    assert btc_gbp_row["price"] == 100
    assert btc_gbp_row["market_cap"] == 1000
    assert btc_gbp_row["volume_24h"] == 500
    assert btc_gbp_row["change_24h"] == -1.2


def test_timestamp_exists():
    df = transform_current_prices(MOCK_RAW_DATA, MOCK_COINS, MOCK_CURRENCIES)
    assert df["timestamp"].notna().all()


def test_missing_prices_are_dropped():
    bad_raw = {
        "bitcoin": {
            "gbp": None,  # Missing => should get dropped
            "gbp_market_cap": 100,
            "gbp_24h_vol": 100,
            "gbp_24h_change": 1,
        }
    }

    df = transform_current_prices(bad_raw, MOCK_COINS, ["gbp"])
    assert len(df) == 0  # Row should be removed


def test_numeric_columns_are_numeric():
    df = transform_current_prices(MOCK_RAW_DATA, MOCK_COINS, MOCK_CURRENCIES)
    numeric_cols = ["price", "market_cap", "volume_24h", "change_24h"]

    for col in numeric_cols:
        assert pd.api.types.is_numeric_dtype(df[col])


def test_unknown_coin_id_does_not_crash(caplog):
    bad_raw = {
        "unknowncoin": {
            "gbp": 50,
            "gbp_market_cap": 100,
            "gbp_24h_vol": 10,
            "gbp_24h_change": 0.5,
        }
    }

    df = transform_current_prices(bad_raw, MOCK_COINS, ["gbp"])

    # Should still return a row with coin_name = capitalized fallback
    assert len(df) == 1
    assert df.iloc[0]["coin_name"] == "Unknowncoin"

    # Assert a warning was logged
    assert any(
        "Unknown coin ID" in message for message in caplog.text.split("\n")
    )
