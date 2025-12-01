import pandas as pd
from src.load.load_current_prices import load_current_prices


def test_load_creates_csv_file(tmp_path, monkeypatch):
    """
    Test that load_current_prices creates a CSV file in the correct location

    - tmp_path: pytest temporary folder (isolated)
    - monkeypatch: overriding CLEANED_DIR so real project files are unaffected
    """

    # Patch CLEANED_DIR so the function writes into tmp_path
    monkeypatch.setattr("src.load.load_current_prices.CLEANED_DIR", tmp_path)

    # Test DataFrame
    df = pd.DataFrame(
        {
            "coin_id": ["bitcoin"],
            "currency": ["usd"],
            "price": [100],
            "market_cap": [1000],
            "volume_24h": [500],
            "change_24h": [1.2],
            "timestamp": ["2025-01-01T00:00:00Z"],
        }
    )

    filepath = load_current_prices(df, "test_prices.csv")
    saved_file = tmp_path / "test_prices.csv"

    assert saved_file.exists(), "CSV file was not created"
    assert filepath == str(
        saved_file
    ), "Returned path does not match file created"


def test_load_writes_correct_content(tmp_path, monkeypatch):
    """
    Ensure that the CSV written to disk contains the correct data
    """

    monkeypatch.setattr("src.load.load_current_prices.CLEANED_DIR", tmp_path)

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

    load_current_prices(df, "test_prices.csv")
    saved_file = tmp_path / "test_prices.csv"

    loaded_df = pd.read_csv(saved_file)

    # Check the content matches
    pd.testing.assert_frame_equal(df, loaded_df)


def test_load_overwrites_existing_file(tmp_path, monkeypatch):
    """
    Test that saving a second time overwrites the existing CSV file
    """

    monkeypatch.setattr("src.load.load_current_prices.CLEANED_DIR", tmp_path)

    df1 = pd.DataFrame({"coin_id": ["bitcoin"]})
    df2 = pd.DataFrame({"coin_id": ["ethereum"]})

    load_current_prices(df1, "overwrite.csv")
    load_current_prices(df2, "overwrite.csv")

    saved_file = tmp_path / "overwrite.csv"
    loaded = pd.read_csv(saved_file)

    assert (
        loaded.iloc[0]["coin_id"] == "ethereum"
    ), "File did not overwrite correctly"
