from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

COINS = [
    {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
    {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
    {"id": "binancecoin", "symbol": "BNB", "name": "BNB"},
    {"id": "solana", "symbol": "SOL", "name": "Solana"},
    {"id": "ripple", "symbol": "XRP", "name": "XRP"},
]

CURRENCIES = ["gbp", "usd", "eur"]
DEFAULT_CURRENCY = "gbp"
DEFAULT_DAYS = 365

RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
HASH_DIR = BASE_DIR / "data" / "hashes"
LOG_DIR = BASE_DIR / "logs"
