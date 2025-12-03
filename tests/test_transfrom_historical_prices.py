import pandas as pd
from src.transform.transform_historical_prices import (
    transform_historical_prices,
)


def test_empty_input_returns_empty_dfs():
    result = transform_historical_prices([])

    assert isinstance(result["clean"], pd.DataFrame)
    assert isinstance(result["stats"], pd.DataFrame)
    assert result["clean"].empty
    assert result["stats"].empty


def test_timestamp_conversion_and_sorting():
    raw = [
        {
            "coin_id": "btc",
            "coin_name": "Bitcoin",
            "currency": "gbp",
            "timestamp_ms": 2000,
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 1.5,
        },
        {
            "coin_id": "btc",
            "coin_name": "Bitcoin",
            "currency": "gbp",
            "timestamp_ms": 1000,
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 1.0,
        },
    ]

    result = transform_historical_prices(raw)
    df = result["clean"]

    # Should be sorted ascending by timestamp
    assert df.iloc[0]["timestamp_ms"] == 1000
    assert df.iloc[1]["timestamp_ms"] == 2000

    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_normalized_close_correct():
    raw = [
        {
            "coin_id": "btc",
            "coin_name": "Bitcoin",
            "currency": "gbp",
            "timestamp_ms": 1000,
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 10,
        },
        {
            "coin_id": "btc",
            "coin_name": "Bitcoin",
            "currency": "gbp",
            "timestamp_ms": 2000,
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 20,
        },
    ]

    df = transform_historical_prices(raw)["clean"]

    # Normalised close: close / first_close
    assert df.iloc[0]["normalized_close"] == 1.0
    assert df.iloc[1]["normalized_close"] == 2.0


def test_stats_table_values():
    raw = [
        {
            "coin_id": "btc",
            "coin_name": "Bitcoin",
            "currency": "gbp",
            "timestamp_ms": 1000,
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 10,
        },
        {
            "coin_id": "btc",
            "coin_name": "Bitcoin",
            "currency": "gbp",
            "timestamp_ms": 2000,
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 15,
        },
    ]

    stats = transform_historical_prices(raw)["stats"]

    assert len(stats) == 1
    row = stats.iloc[0]

    assert row["coin_name"] == "Bitcoin"
    assert row["max_close"] == 15
    assert row["min_close"] == 10
    assert row["total_return"] == (15 - 10) / 10
