import json
from unittest.mock import patch, MagicMock
from src.extraction.extract_historical_prices import extract_historical_ohlc

MOCK_COINS = [{"id": "bitcoin", "name": "Bitcoin"}]

VALID_10_ROWS = [[1700000000000 + i, 1, 2, 3, 4] for i in range(10)]
BACKUP_DATA = [{"coin_id": "bitcoin"}]


def test_extract_success(tmp_path):
    fake_backup = tmp_path / "backup.json"

    with patch(
        "src.extraction.extract_historical_prices.BACKUP_FILE", fake_backup
    ):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = VALID_10_ROWS

        with patch(
            "src.extraction.extract_historical_prices.requests.get",
            return_value=mock_resp,
        ):
            with patch("src.extraction.extract_historical_prices.time.sleep"):
                results = extract_historical_ohlc(MOCK_COINS)

    assert len(results) == 10
    assert fake_backup.exists()  # backup written on success


def test_extract_fails_if_less_than_10_rows_no_backup(tmp_path):
    fake_backup = tmp_path / "backup.json"  # does NOT exist

    with patch(
        "src.extraction.extract_historical_prices.BACKUP_FILE", fake_backup
    ):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = VALID_10_ROWS[:3]

        with patch(
            "src.extraction.extract_historical_prices.requests.get",
            return_value=mock_resp,
        ):
            with patch("src.extraction.extract_historical_prices.time.sleep"):
                results = extract_historical_ohlc(MOCK_COINS)

    assert results == []


def test_extract_less_than_10_rows_loads_backup(tmp_path):
    fake_backup = tmp_path / "backup.json"
    fake_backup.write_text(json.dumps(BACKUP_DATA))

    with patch(
        "src.extraction.extract_historical_prices.BACKUP_FILE", fake_backup
    ):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = VALID_10_ROWS[:2]

        with patch(
            "src.extraction.extract_historical_prices.requests.get",
            return_value=mock_resp,
        ):
            with patch("src.extraction.extract_historical_prices.time.sleep"):
                results = extract_historical_ohlc(MOCK_COINS)

    assert results == BACKUP_DATA


def test_extract_api_error_no_backup(tmp_path):
    fake_backup = tmp_path / "backup.json"

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("error")

    with patch(
        "src.extraction.extract_historical_prices.BACKUP_FILE", fake_backup
    ):
        with patch(
            "src.extraction.extract_historical_prices.requests.get",
            return_value=mock_resp,
        ):
            with patch("src.extraction.extract_historical_prices.time.sleep"):
                results = extract_historical_ohlc(MOCK_COINS)

    assert results == []


def test_extract_api_error_loads_backup(tmp_path):
    fake_backup = tmp_path / "backup.json"
    fake_backup.write_text(json.dumps(BACKUP_DATA))

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("error")

    with patch(
        "src.extraction.extract_historical_prices.BACKUP_FILE", fake_backup
    ):
        with patch(
            "src.extraction.extract_historical_prices.requests.get",
            return_value=mock_resp,
        ):
            with patch("src.extraction.extract_historical_prices.time.sleep"):
                results = extract_historical_ohlc(MOCK_COINS)

    assert results == BACKUP_DATA


def test_extract_empty_response_no_backup(tmp_path):
    fake_backup = tmp_path / "backup.json"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []

    with patch(
        "src.extraction.extract_historical_prices.BACKUP_FILE", fake_backup
    ):
        with patch(
            "src.extraction.extract_historical_prices.requests.get",
            return_value=mock_resp,
        ):
            with patch("src.extraction.extract_historical_prices.time.sleep"):
                results = extract_historical_ohlc(MOCK_COINS)

    assert results == []
