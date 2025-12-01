import json
from src.utils.save_json import save_raw_json


def test_save_json_creates_file(tmp_path, monkeypatch):
    """
    Ensure save_raw_json() creates a file in the expected location

    tmp_path:
        Temporary directory created by pytest for isolation.
        Deleted automatically after the test

    monkeypatch:
        Temporarily overrides RAW_DIR so the test does NOT write to the real
        project
    """

    # Redirect RAW_DIR → temporary folder
    monkeypatch.setattr("src.utils.save_json.RAW_DIR", tmp_path)

    data = {"btc": 1}
    filepath = save_raw_json(data, "test_backup.json")

    saved_file = tmp_path / "test_backup.json"

    assert saved_file.exists(), "Backup JSON file was not created"
    assert str(saved_file) == filepath, "Returned file path is incorrect"


def test_save_json_writes_correct_content(tmp_path, monkeypatch):
    """
    Verify that the JSON saved to disk matches the input data exactly
    """

    monkeypatch.setattr("src.utils.save_json.RAW_DIR", tmp_path)

    data = {"eth": {"usd": 3000}}
    save_raw_json(data, "test_backup.json")

    saved_file = tmp_path / "test_backup.json"

    with saved_file.open("r") as f:
        loaded = json.load(f)

    assert loaded == data, "Saved JSON content does not match the input"


def test_save_json_overwrites_existing_file(tmp_path, monkeypatch):
    """
    Ensure saving again using the same filename overwrites older content
    """

    monkeypatch.setattr("src.utils.save_json.RAW_DIR", tmp_path)

    file_path = tmp_path / "overwrite.json"

    # First write
    save_raw_json({"a": 1}, "overwrite.json")

    # Second write should overwrite the file
    save_raw_json({"b": 2}, "overwrite.json")

    with file_path.open("r") as f:
        loaded = json.load(f)

    assert loaded == {"b": 2}, "File did not overwrite old content properly"
