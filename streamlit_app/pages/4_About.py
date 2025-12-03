import streamlit as st

st.set_page_config(page_title="About This Project")

st.title("About This Project")

st.markdown(
    """
    ## Project Overview
    This Streamlit dashboard provides real-time and historical insights into major
    cryptocurrencies using a fully automated ETL pipeline.

    The pipeline:
    - Extracts pricing data from the **CoinGecko API**
    - Applies cleaning, transformations, and feature engineering
    - Stores both current and historical datasets locally
    - Powers the interactive dashboard pages you see in the sidebar

    ---

    ## Data Sources
    - **CoinGecko API** — live and historical OHLC pricing  
    - Automatic fallback to cached data if API calls fail  
    - Historical data stored in GBP for consistency

    ---

    ## Dashboard Features
    - Live market overview and KPIs  
    - Price comparisons across multiple currencies  
    - Historical candlestick charts  
    - Normalised price trends  
    - Rolling averages and volatility metrics  
    - Statistical summaries and insights

    ---

    ## Developer
    **Created by Nasif Islam**  
    Built using Python, Streamlit, Plotly, and a custom ETL pipeline.

    ---

    ## Update Frequency
    The ETL pipeline is designed to run on-demand.  
    Each dataset includes a timestamp indicating the last extraction time.

    ---

    ## Version
    **v1.0.0**
    """
)
