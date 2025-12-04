# Crypto-ETL
An ETL pipeline for extracting, transforming and loading cryptocurrency market data from the CoinGecko API

## Overview
Crypto-ETL retrieves both **current prices** and **historical OHLC data**, stores the raw responses as JSON, and processes them into clean, analysis-ready CSV files.
A Streamlit dashboard is provided for interactive visualization.

## Tech Stack
- **Python 3.12+**
- **pandas** – data processing 
- **Streamlit** – interactive dashboard  
- **Plotly** – visualization  
- **pytest** – testing framework  

## Features
- Extracts **current** and **historical** cryptocurrency data  
- Cleans, validates, and enriches data using pandas  
- Loads cleaned data into CSV files  
- Modular and testable ETL architecture  
- Streamlit dashboard for visual exploration  

## Installation

Clone the repository and switch directory
```bash
git clone https://github.com/Nasif-Islam/crypto-etl.git
cd crypto-etl
```

Create a virtual environment and activate it
```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

Install dependencies in editable mode
```bash
pip install -e .
```

## Usage

### Run the ETL pipeline
Set the environment (dev or test) and run the pipeline
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

## Documentation
More in-depth documentation can be found in the [docs/](docs/) directory:
- [PROJECT DOCUMENTATION](docs/PROJECT_DOCUMENTATION.md)

## License
This project is licensed under the MIT license

Created by Nasif Islam
