import pytest  # noqa: F401
import json
from unittest.mock import patch, MagicMock, mock_open
from src.extraction.extract_current_prices import extract_current_prices
from src.utils.config import COINS
from requests.exceptions import HTTPError


@patch("requests.get")
def test_returns_dict(mock_get):
    """
    This test checks that the extractor returns a dictionary
    It uses a mocked API response to avoid calling the real CoinGecko API.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 120, "eur": 110}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])
    assert isinstance(data, dict)


@patch("requests.get")
def test_expected_coins_present(mock_get):
    """
    This test verifies that the extractor returns an entry for each coin
    listed in COINS.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"gbp": 100},
        "ethereum": {"gbp": 100},
        "solana": {"gbp": 100},
        "binancecoin": {"gbp": 100},
        "ripple": {"gbp": 100},
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    data = extract_current_prices(COINS, ["gbp"])
    ids = [coin["id"] for coin in COINS]
    for coin_id in ids:
        assert coin_id in data


@patch("requests.get")
def test_currencies_present(mock_get):
    """
    Tests that the extractor includes the expected currencies in the output
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 110, "eur": 105}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])
    for currency in ["gbp", "usd", "eur"]:
        assert currency in data["bitcoin"]


@patch("requests.get")
def test_values_are_numeric(mock_get):
    """
    Ensures the returned price values are numeric (int or float)
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 110, "eur": 105}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])
    for currency in ["gbp", "usd", "eur"]:
        assert isinstance(data["bitcoin"][currency], (int, float))


@patch("requests.get")
def test_api_mock(mock_get):
    """
    A more direct test confirming that the mock API response is passed
    through the extractor unchanged
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"gbp": 100, "usd": 120, "eur": 110}
    }
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    data = extract_current_prices([{"id": "bitcoin"}], ["gbp", "usd", "eur"])
    assert "bitcoin" in data
    assert data["bitcoin"]["usd"] == 120


@patch("requests.get")
def test_api_http_error_uses_backup(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("HTTP Error")

    mock_response.status_code = 500
    mock_response.reason = "Server Error"

    mock_get.return_value = mock_response

    fake_backup = {"bitcoin": {"gbp": 999}}

    with patch("pathlib.Path.exists", return_value=True):
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(fake_backup))
        ):
            data = extract_current_prices([{"id": "bitcoin"}], ["gbp"])

    assert data == fake_backup


@patch("requests.get")
def test_json_decode_error_uses_backup(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError("json error")
    mock_get.return_value = mock_response

    fake_backup = {"bitcoin": {"gbp": 200}}

    with patch("pathlib.Path.exists", return_value=True):
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(fake_backup))
        ):
            data = extract_current_prices([{"id": "bitcoin"}], ["gbp"])

    assert data == fake_backup
