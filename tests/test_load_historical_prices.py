import pandas as pd
from pathlib import Path
from src.load.load_historical_prices import load_historical_prices


def test_load_historical_creates_files(tmp_path, monkeypatch):
    """
    Ensure the load function writes two CSVs into CLEANED_DIR
    """

    # Mock CLEANED_DIR for this test
    monkeypatch.setattr(
        "src.load.load_historical_prices.CLEANED_DIR", tmp_path
    )

    clean_df = pd.DataFrame(
        {"coin_id": ["bitcoin"], "close": [50000], "timestamp": ["2024-01-01"]}
    )

    stats_df = pd.DataFrame({"coin_id": ["bitcoin"], "max_close": [50000]})

    data = {"clean": clean_df, "stats": stats_df}

    result_paths = load_historical_prices(data)

    clean_path = Path(result_paths["clean_path"])
    stats_path = Path(result_paths["stats_path"])

    assert clean_path.exists()
    assert stats_path.exists()

    # Check basic file contents
    assert "bitcoin" in clean_path.read_text()
    assert "max_close" in stats_path.read_text()


def test_load_historical_invalid_input_raises_error(tmp_path, monkeypatch):
    """
    Ensure missing 'clean' or 'stats' keys cause a ValueError
    """

    monkeypatch.setattr(
        "src.load.load_historical_prices.CLEANED_DIR", tmp_path
    )

    bad_data = {"clean": pd.DataFrame()}  # missing stats df

    try:
        load_historical_prices(bad_data)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_load_historical_auto_creates_directory(tmp_path, monkeypatch):
    """
    The function should auto-create CLEANED_DIR if missing
    """

    fake_cleaned = tmp_path / "subfolder" / "deep"
    monkeypatch.setattr(
        "src.load.load_historical_prices.CLEANED_DIR", fake_cleaned
    )

    clean_df = pd.DataFrame({"x": [1]})
    stats_df = pd.DataFrame({"y": [2]})
    data = {"clean": clean_df, "stats": stats_df}

    result = load_historical_prices(data)

    assert Path(result["clean_path"]).exists()
    assert Path(result["stats_path"]).exists()


def test_rows_written_correctly(tmp_path, monkeypatch):
    """
    Ensure that the number of rows in the output CSV matches the input DF
    """

    monkeypatch.setattr(
        "src.load.load_historical_prices.CLEANED_DIR", tmp_path
    )

    clean_df = pd.DataFrame({"coin_id": ["btc", "eth"], "close": [1, 2]})
    stats_df = pd.DataFrame({"coin_id": ["btc"], "max_close": [2]})

    result = load_historical_prices({"clean": clean_df, "stats": stats_df})

    clean_output = Path(result["clean_path"]).read_text()
    stats_output = Path(result["stats_path"]).read_text()

    assert clean_output.count("\n") == 3  # header + 2 rows
    assert stats_output.count("\n") == 2  # header + 1 row
