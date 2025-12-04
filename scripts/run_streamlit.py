import subprocess
from pathlib import Path


def main():
    """Launch the Streamlit dashboard"""
    root = Path(__file__).resolve().parents[1]
    app_path = root / "streamlit_app" / "0_Market_Overview.py"
    subprocess.run(["streamlit", "run", str(app_path)])
