# Crypto-ETL
ETL pipeline for extracting, transforming and loading cryptocurrency price data

## Overview
Crypto-ETL is a Python pipeline that extracts cryptocurrency data from the CoinGecko API, structures and enriches it into dataframes, and exports it as CSV files. The project supports both **current prices** and **historical OHLC data**, with configurable logging for different environments

## Tech Stack
- **Python** – (3.12+)
- **Streamlit** – interactive dashboard  
- **pandas** – data processing and manipulation  
- **Plotly** – data visualization  
- **pytest** – testing framework  

## Features
- Extracts current and historical cryptocurrency prices
- Transform data: clean, validate and enrich with moving averages, normalized prices, etc.
- Load data into CSV files for analysis
- Supports environment-specific logging (`dev` and `test`)
- Streamlit dashboard for visualizing current crypto prices
- Modular and testable architecture

## Installation

Clone the repository and switch directory:
```bash
git clone https://github.com/Nasif-Islam/crypto-etl.git
cd crypto-etl
```

Create a virtual environment and activate it:
```bash
python -m venv .venvs
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

Install dependencies in editable mode:
```bash
pip install -e .
```

## Usage

### Run tests (Optional)
```bash
export ENV=test   # Mac/Linux
set ENV=test      # Windows
run_tests
```

### Run the ETL pipeline
Set the environment (dev or test) and run the pipeline:
```bash
export ENV=dev   # Mac/Linux
set ENV=dev      # Windows
run_etl
```

### Run Streamlit dashboard
```bash
run_streamlit
```
Open the local URL provided in your browser

## Logging
- Environment-specific log files: `etl_dev.log` and `etl_test.log`
- Logs include timestamps, log level and messages for ETL stages

## License
This project is licensed under the MIT license

Created by Nasif Islam  

For detailed technical documentation, see the docs directory
