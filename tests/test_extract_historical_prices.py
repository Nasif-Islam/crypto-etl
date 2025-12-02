import pytest  # noqa: F401
import json
from unittest.mock import patch, MagicMock, mock_open
from src.extraction.extract_historical_prices import extract_historical_ohlc

MOCK_COINS = [{"id": "bitcoin", "name": "Bitcoin"}]

MOCK_RESPONSE = [
    [1700000000000, 35000, 36000, 34000, 35500],
    [1700086400000, 35500, 36500, 34500, 36000],
]

BACKUP_DATA = [
    {
        "coin_id": "bitcoin",
        "timestamp_ms": 123,
        "open": 1,
        "high": 2,
        "low": 3,
        "close": 4,
        "currency": "gbp",
        "coin_name": "Bitcoin",
    }
]


@patch("src.extraction.extract_historical_prices.time.sleep")
@patch("src.extraction.extract_historical_prices.requests.get")
@patch("src.extraction.extract_historical_prices.open", new_callable=mock_open)
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
def test_extract_historical_success(
    mock_exists, mock_file, mock_get, mock_sleep
):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_RESPONSE
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS)

    assert len(records) == 2

    first = records[0]
    assert first["coin_id"] == "bitcoin"
    assert first["currency"] == "gbp"
    assert first["timestamp_ms"] == 1700000000000

    mock_file.assert_called_once()
    mock_file().write.assert_called_once()


@patch("src.extraction.extract_historical_prices.time.sleep")
@patch("src.extraction.extract_historical_prices.requests.get")
@patch("src.extraction.extract_historical_prices.open", new_callable=mock_open)
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
def test_extract_skips_bad_rows(mock_exists, mock_file, mock_get, mock_sleep):
    bad_data = [
        [1700000000000, 35000],  # Invalid row
        [1700086400000, 35500, 36500, 34500, 36000],  # Valid row
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = bad_data
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS)

    assert len(records) == 1  # Only one row valid


@patch("src.extraction.extract_historical_prices.time.sleep")
@patch("src.extraction.extract_historical_prices.requests.get")
@patch("src.extraction.extract_historical_prices.open", new_callable=mock_open)
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
def test_extract_api_fail_no_backup(
    mock_exists, mock_file, mock_get, mock_sleep
):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("500 error")
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS)

    assert records == []


@patch("src.extraction.extract_historical_prices.time.sleep")
@patch("src.extraction.extract_historical_prices.requests.get")
@patch(
    "src.extraction.extract_historical_prices.open",
    new_callable=mock_open(read_data=json.dumps(BACKUP_DATA)),
)
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=True,
)
def test_extract_api_fail_loads_backup(
    mock_exists, mock_file, mock_get, mock_sleep
):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("500 error")
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS)

    assert records == BACKUP_DATA
    mock_file.assert_called_once()  # backup read
    # Backup should NOT be overwritten
    mock_file().write.assert_not_called()


@patch("src.extraction.extract_historical_prices.time.sleep")
@patch("src.extraction.extract_historical_prices.requests.get")
@patch(
    "src.extraction.extract_historical_prices.open",
    new_callable=mock_open(read_data=json.dumps(BACKUP_DATA)),
)
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=True,
)
def test_extract_partial_loads_backup(
    mock_exists, mock_file, mock_get, mock_sleep
):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []  # empty - failure
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS)

    assert records == BACKUP_DATA
    mock_file().write.assert_not_called()


@patch("src.extraction.extract_historical_prices.time.sleep")
@patch("src.extraction.extract_historical_prices.requests.get")
@patch("src.extraction.extract_historical_prices.open", new_callable=mock_open)
@patch(
    "src.extraction.extract_historical_prices.BACKUP_FILE.exists",
    return_value=False,
)
def test_extract_partial_no_backup(
    mock_exists, mock_file, mock_get, mock_sleep
):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []  # Failure
    mock_get.return_value = mock_resp

    records = extract_historical_ohlc(MOCK_COINS)

    assert records == []  # partial but empty - only 1 coin
    # Backup should not be written
    mock_file().write.assert_not_called()
