import streamlit as st

st.set_page_config(page_title="About This Project")

st.title("About This Project")

st.markdown(
    """
    ## Overview
    This dashboard provides an interactive view of live and historical cryptocurrency
    data. It includes price tracking, trend analysis, comparisons, and statistical
    insights — all presented through a clean Streamlit interface

    The displayed cryptocurrencies, default currency, and supported currency options
    are fully configurable via a Python config file

    ---

    ## Features
    - Live market data and KPIs  
    - Multi-currency price views  
    - Historical candlestick charts  
    - Moving averages and volatility trends  
    - Cross-asset comparison tools  
    - Summary metrics from full historical datasets  

    ---

    ## Data Source
    Market data is retrieved from the **CoinGecko API**, with local caching for
    performance and reliability

    ---

    ## Developer
    **Nasif Islam**  
    GitHub: [https://github.com/Nasif-Islam](https://github.com/Nasif-Islam)

    ---

    ## Version
    **v1.0.0**
    """
)
