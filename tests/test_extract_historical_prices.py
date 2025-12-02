import pytest  # noqa: F401
import pandas as pd
from unittest.mock import patch, MagicMock
from src.extraction.extract_historical_prices import extract_historical_ohlc

MOCK_COINS = [{"id": "bitcoin", "name": "Bitcoin"}]
MOCK_CURRENCIES = ["usd"]
MOCK_DAYS = 10

MOCK_OHLC_RESPONSE = [
    [1700000000000, 35000, 36000, 34000, 35500],
    [1700086400000, 35500, 36500, 34500, 36000],
]


@patch("src.extraction.extract_historical_prices.requests.get")
def test_extract_historical_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_OHLC_RESPONSE
    mock_get.return_value = mock_response

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)

    assert len(records) == len(MOCK_OHLC_RESPONSE)

    first = records[0]
    assert first["coin_id"] == "bitcoin"
    assert first["coin_name"] == "Bitcoin"
    assert first["currency"] == "usd"
    assert isinstance(first["timestamp"], pd.Timestamp)
    assert (
        "open" in first
        and "high" in first
        and "low" in first
        and "close" in first
    )


@patch("src.extraction.extract_historical_prices.requests.get")
def test_extract_historical_skips_bad_rows(mock_get):
    bad_data = [
        [1700000000000, 35000, 36000],
        [1700086400000, 35500, 36500, 34500, 36000],
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = bad_data
    mock_get.return_value = mock_response

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)

    assert len(records) == 1


@patch("src.extraction.extract_historical_prices.requests.get")
def test_extract_historical_api_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)

    assert records == []


@patch("src.extraction.extract_historical_prices.requests.get")
def test_extract_historical_json_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Bad JSON")
    mock_get.return_value = mock_response

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)

    assert records == []
