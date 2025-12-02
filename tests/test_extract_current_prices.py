import pytest  # noqa: F401
import json  # noqa: F401
from unittest.mock import patch, MagicMock, mock_open
from requests.exceptions import HTTPError
from src.extraction.extract_current_prices import extract_current_prices
from src.utils.config import COINS


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.exists", return_value=False)
@patch("requests.get")
def test_returns_dict(mock_get, mock_exists, mock_file):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"bitcoin": {"gbp": 100}}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    data = extract_current_prices([{"id": "bitcoin"}], ["gbp"])
    assert isinstance(data, dict)


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.exists", return_value=False)
@patch("requests.get")
def test_expected_coins_present(mock_get, mock_exists, mock_file):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "bitcoin": {"gbp": 100},
        "ethereum": {"gbp": 100},
        "solana": {"gbp": 100},
        "binancecoin": {"gbp": 100},
        "ripple": {"gbp": 100},
    }
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    data = extract_current_prices(COINS, ["gbp"])

    for coin in COINS:
        assert coin["id"] in data


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.exists", return_value=False)
@patch("requests.get")
def test_currencies_present(mock_get, mock_exists, mock_file):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 110, "eur": 105}
    }
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])

    assert "usd" in data["bitcoin"]
    assert "gbp" in data["bitcoin"]
    assert "eur" in data["bitcoin"]


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.exists", return_value=False)
@patch("requests.get")
def test_values_are_numeric(mock_get, mock_exists, mock_file):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 110, "eur": 105}
    }
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])

    for val in data["bitcoin"].values():
        assert isinstance(val, (int, float))


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.exists", return_value=False)
@patch("requests.get")
def test_api_mock(mock_get, mock_exists, mock_file):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 120, "eur": 110}
    }
    mock_get.return_value = mock_resp

    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])

    assert data["bitcoin"]["usd"] == 120


@patch("requests.get")
def test_api_http_error_uses_backup(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = HTTPError("HTTP Error")
    mock_resp.status_code = 500
    mock_resp.reason = "Server Error"
    mock_get.return_value = mock_resp

    fake_backup = {"bitcoin": {"gbp": 999}}

    with patch(
        "src.extraction.extract_current_prices.BACKUP_FILE.exists",
        return_value=True,
    ):
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(fake_backup))
        ):
            data = extract_current_prices([{"id": "bitcoin"}], ["gbp"])

    assert data == fake_backup


@patch("requests.get")
def test_json_decode_error_uses_backup(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.side_effect = ValueError("Bad JSON")
    mock_get.return_value = mock_resp

    fake_backup = {"bitcoin": {"gbp": 200}}

    with patch(
        "src.extraction.extract_current_prices.BACKUP_FILE.exists",
        return_value=True,
    ):
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(fake_backup))
        ):
            data = extract_current_prices([{"id": "bitcoin"}], ["gbp"])

    assert data == fake_backup
