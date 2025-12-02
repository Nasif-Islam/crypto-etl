import pytest  # noqa: F401
import json  # noqa: F401
from unittest.mock import patch, MagicMock, mock_open
from src.extraction.extract_historical_prices import extract_historical_ohlc

MOCK_COINS = [{"id": "bitcoin", "name": "Bitcoin"}]
MOCK_CURRENCIES = ["usd"]
MOCK_DAYS = 10

MOCK_OHLC_RESPONSE = [
    [1700000000000, 35000, 36000, 34000, 35500],
    [1700086400000, 35500, 36500, 34500, 36000],
]


@patch("src.extraction.extract_historical_prices.requests.get")
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
@patch("builtins.open", new_callable=mock_open)
def test_extract_historical_success(mock_file, mock_exists, mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_OHLC_RESPONSE
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)

    assert len(records) == 2

    first = records[0]
    assert first["coin_id"] == "bitcoin"
    assert first["coin_name"] == "Bitcoin"
    assert first["currency"] == "usd"

    assert first["timestamp_ms"] == 1700000000000

    for key in ["open", "high", "low", "close"]:
        assert key in first


@patch("src.extraction.extract_historical_prices.requests.get")
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
@patch("builtins.open", new_callable=mock_open)
def test_extract_historical_skips_bad_rows(mock_file, mock_exists, mock_get):
    bad_data = [
        [1700000000000, 35000, 36000],  # invalid
        [1700086400000, 35500, 36500, 34500, 36000],  # valid
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = bad_data
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)

    assert len(records) == 1


@patch("src.extraction.extract_historical_prices.requests.get")
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
@patch("builtins.open", new_callable=mock_open)
def test_extract_historical_api_failure_no_backup(
    mock_file, mock_exists, mock_get
):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)
    assert records == []


@patch("src.extraction.extract_historical_prices.requests.get")
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
@patch("builtins.open", new_callable=mock_open)
def test_extract_historical_json_error_no_backup(
    mock_file, mock_exists, mock_get
):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError("Bad JSON")
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS, MOCK_CURRENCIES, MOCK_DAYS)
    assert records == []
