import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.load.load_current_prices import load_current_prices


def fake_cleaned_dir(tmp_path, exists=True):
    """
    Returns a fake CLEANED_DIR Path-like object that:
    - has exists() and mkdir()
    - supports CLEANED_DIR / filename and returns a real path in tmp_path
    """
    fake = MagicMock()

    fake.exists.return_value = exists
    fake.mkdir.return_value = None

    fake.__truediv__.side_effect = lambda filename: tmp_path / filename

    return fake


def test_load_creates_directory_if_missing(tmp_path):
    df = pd.DataFrame({"coin": ["bitcoin"], "price": [50000]})

    fake_dir = fake_cleaned_dir(tmp_path, exists=False)

    with patch("src.load.load_current_prices.CLEANED_DIR", fake_dir):
        with patch(
            "src.load.load_current_prices.os.path.getsize", return_value=1500
        ):
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:

                mock_to_csv.side_effect = lambda path, index=False: (
                    tmp_path / "current_crypto_prices.csv"
                ).write_text("data")

                result_path = load_current_prices(df)

    fake_dir.mkdir.assert_called_once()
    assert "current_crypto_prices.csv" in result_path


def test_load_writes_csv_successfully(tmp_path):
    df = pd.DataFrame({"coin": ["ethereum"], "price": [1800]})

    fake_dir = fake_cleaned_dir(tmp_path, exists=True)

    with patch("src.load.load_current_prices.CLEANED_DIR", fake_dir):
        with patch(
            "src.load.load_current_prices.os.path.getsize", return_value=2048
        ):
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:

                mock_to_csv.side_effect = lambda path, index=False: (
                    tmp_path / "current_crypto_prices.csv"
                ).write_text("data")

                result_path = load_current_prices(df)

    mock_to_csv.assert_called_once()
    assert "current_crypto_prices.csv" in result_path


def test_load_raises_error_on_write_failure(tmp_path):
    df = pd.DataFrame({"coin": ["xrp"], "price": [0.50]})

    fake_dir = fake_cleaned_dir(tmp_path, exists=True)

    with patch("src.load.load_current_prices.CLEANED_DIR", fake_dir):
        with patch(
            "pandas.DataFrame.to_csv", side_effect=Exception("Write failed")
        ):

            with pytest.raises(Exception):
                load_current_prices(df)
