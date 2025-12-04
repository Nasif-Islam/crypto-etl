# Crypto-ETL — Detailed Technical Documentation

# Project Goals
The primary goal of this project was to design and implement a complete **Extract–Transform–Load (ETL)** pipeline using Python, incorporating good engineering practices including:

- Clean modular architecture
- Real-world API extraction
- Structured data cleaning & validation
- Feature engineering & enrichment
- Automated logging & timing
- Test-driven development
- Reproducible, transparent data storage
- Interactive data visualization with Streamlit/Plotly

---

# Choice of Data
I chose the **CoinGecko API** as the data source for several reasons:

### Public & free API  
No authentication required, making it ideal for a reproducible ETL demonstration

### Multiple endpoints  
Supports both **current price** & **historical OHLC time series** data, allowing for a multi-stage ETL

### Dynamic dataset  
Cryptocurrency markets provide natural volatility, making enrichment (e.g., percentage change, rolling volatility) meaningful

### Sufficient data volume
Historical data for 5 coins × 365 days produces hundreds of rows — aligned with complexity requirements
(This pipeline can easily scale to more coins/currencies or longer timeframes as the user sets this in the config file)

---

# ETL Architecture Overview

The project follows a **standardized architecture**:

```
src/
  extraction/
  transform/
  load/
  utils/
streamlit_app/
data/
  raw/
  cleaned/
scripts/
docs/
tests/
```

This modular design ensures clear separation of responsibilities

---

# Configuration, Logging, and Timer System

## Config File
All project-wide settings live in `src/utils/config.py`, including:

- List of supported cryptocurrencies
- Supported fiat currencies
- Directory paths
- Defaults (days, base currency)

This prevents magic values and centralizes configuration

---

## Logger
A custom logger provides:

- Environment‑specific logging (etl_dev.log, etl_test.log)
- Timestamps and log levels
- Logs for each ETL stage
- Error and fallback messages

Logging increases transparency, supports debugging, and mimics real production systems

---

## Timer Decorator
A custom @timer decorator measures and logs the execution time of key ETL functions.
This adds lightweight performance monitoring to the pipeline and makes it easy to identify slower stages, 
support optimization efforts, and track performance changes over time.

---

# Extraction

The extraction stage retrieves data from **two CoinGecko API endpoints**:

---

## Current Prices Endpoint

Retrieves:

- Current price
- Market cap
- 24h volume
- 24h percentage change
- Timestamp  

### Workflow:
1. Build API request
2. Fetch data for set coins and currencies
3. Validate response
4. Parse JSON
5. Save backup file to `data/raw//backup_current_prices.json`  

---

## Historical OHLC Endpoint

Retrieves:

- Open
- High
- Low
- Close
- Timestamp

Performed per coin:

1. Request OHLC for 365 days (User sets default days in config file)
2. Validate row count
3. Save raw OHLC JSON
4. Combine all coins into a master dataset  

---

## Raw Data Storage

Raw JSON file is stored in:

```
data/raw/
  backup_current_prices.json
  backup_historical_prices.json
  ...
```

This acts as the **single source of truth**m supporting reproducibility

---

# Transformation

Transformations use **pandas**, with distinct logic for current and historical datasets

---

## Transform — Current Prices

### Cleaning:
- Flatten nested JSON
- Standardize column names
- Convert columns to numeric types
- Remove invalid rows  

### Validation:
- Ensure expected row counts
- Validate required fields
- Drop faulty entries  

### Enrichment:
- Add timestamp
- Map coin symbols
- Sort rows  

**Output:**  
`data/cleaned/current_crypto_prices.csv`

---

## Transform — Historical Prices

### Cleaning:
- Expand OHLC arrays
- Convert UNIX timestamps to pandas datetime format
- Sort rows chronologically  

### Enrichment:
- `pct_change`  
- `volatility_7d` (rolling SD of returns)  
- `volatility_30d` (rolling SD of returns)  
- `normalized_close`  
- Aggregated stats table  

**Outputs:**  
`historical_crypto_prices.csv`  
`historical_crypto_stats.csv`

---

# Load

The load phase writes cleaned DataFrames into:

```
data/cleaned/
  current_crypto_prices.csv
  historical_crypto_prices.csv
  historical_crypto_stats.csv
```

Features:

- Auto-create directories  
- Safe overwrites
- Log file size + row count  

---

# Streamlit Dashboard

### Page 0 — Market Overview
- Current price table  
- Market snapshot  
- Currency selector  
- Timestamp display  

### Page 1 — Historical Analysis
- OHLC candlestick chart  
- Rolling volatility chart  
- Line charts  

### Design Principles:
- Interactive  
- Clean layout  
- Uses only cleaned data  

---

# Testing & Coverage

Tests are executed using:

```
run_tests
```

### Coverage Summary:
- **Total: 74%**  
- **Transforms: 91–100%**  
- **Load: Excellent coverage**  
- **Extraction: Robust tests including mocks and fallbacks**

HTML report: `htmlcov/index.html`

Tests include:

- API mock tests  
- Backup fallback tests  
- Data validation  
- Transformation correctness  
- Load file creation tests  
- Timestamp and type checks  

---

# Insights From the Data
The dataset is dynamic, depending on which coins/currencies the user enables in the config.
However, the pipeline allows insights such as:

- Variation in volatility between coins
- How normalised prices evolve over time
- Rolling volatility as a proxy for market risk
- Relationship between 24h volume and short-term price change

---

# Challenges & Takeaways

### Challenges:
- Inconsistent OHLC lengths from API
- Parsing and validating nested JSON structures
- Rate limiting (required adding delays)
- Designing modular code
- File handling & directory management
- Testing IO and API behaviour
- Managing environment variables  

### Takeaways:
- Logging improves debugging experience  
- Raw data storage ensures reproducibility  
- Feature engineering adds analytical depth  
- Automated tests prevent regressions  
- Timers provide insight into performance  

---

# Future Development

Future enhancements include:

### Hash-based change detection  
Skip unnecessary loads when data is unchanged - avoid rewriting csv file if data is identical  
If data is fresh then maybe append to csv instead of overwriting the entire file (optimize costs if using cloud RDBS)

### Database integration  
Move from CSV to SQLite, PostgreSQL or cloud integration (Amazon S3, DynamoDB etc)

### API Rate Limit Handling
Currently solved with a manual delay. Future versions should implement:
- exponential backoff
- retry logic
- detection of HTTP 429 rate limit errors

### Scheduling  
Use cron or GitHub Actions to automate ETL - refreshes every hour?

### Public deployment of Streamlit app  
Enable real‑time access

### More advanced analytics / Visualizations  
- Correlation matrix  
- Price clustering  
- Anomaly detection  
- Forecasting models  

### Testing

#### Unit Tests
Implement more granular mocks to simulate every possible failure path and edge cases, allowing the extraction module to reach 100% test coverage.
This would significantly enhance pipeline reliability and ensure all fallback logic is robust.

#### Component Tests
Future development could include component-level tests to validate that multiple stages (e.g., extraction and transformation) work correctly when combined. 
This ensures that modules integrate properly beyond unit-level behavior

#### End-to-End Tests
Add end-to-end tests that simulate a full ETL run, from API extraction through transformation to CSV loading. 
This would provide confidence that the entire pipeline functions correctly in a production-like flow.


####  Containerization:
Containerize the ETL and Streamlit application using Docker for portability and production-style deployment

### Real-Time Data Streaming:
Integrate WebSocket streams (Binance or Kafka) to support real-time crypto price updates

# Summary

This project demonstrates a full ETL pipeline with:

- Two API sources  
- Robust logging and timing  
- Modular architecture  
- Comprehensive transformations  
- Clean and validated outputs  
- High test coverage  
- An interactive Streamlit dashboard  
- Clear documentation  

