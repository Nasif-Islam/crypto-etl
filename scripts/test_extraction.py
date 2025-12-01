from src.extraction.fetch_crypto_prices import extract_crypto_prices
from src.utils.config import COINS, CURRENCIES


def main():
    print("\nRunning extraction test...\n")

    data = extract_crypto_prices(COINS, CURRENCIES)

    print("/n--- Extracted Crypto Data ---\n")
    print(data)
    print("\nExtraction test completed.\n")


if __name__ == "__main__":
    main()
