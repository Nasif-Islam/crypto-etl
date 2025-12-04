import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from src.utils.config import (  # noqa: E402
    COINS,
    DEFAULT_CURRENCY,
    DEFAULT_DAYS,
)

st.set_page_config(page_title="Historical Analysis", layout="wide")

# Load historical data
DATA_DIR = ROOT_DIR / "data" / "cleaned"
df_historical = pd.read_csv(DATA_DIR / "historical_crypto_prices.csv")

df_historical["timestamp"] = pd.to_datetime(df_historical["timestamp"])

# Symbol & name mapping for formatting coins
SYMBOL_MAP = {c["name"]: c["symbol"] for c in COINS}
DISPLAY_NAME_MAP = {c["name"]: f"{c['name']} ({c['symbol']})" for c in COINS}

df_historical["symbol"] = df_historical["coin_name"].map(SYMBOL_MAP)
df_historical["display_name"] = df_historical["coin_name"].map(
    DISPLAY_NAME_MAP
)

# Title & Description
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0;'>
        Historical Cryptocurrency Analysis
    </h1>
    """,
    unsafe_allow_html=True,
)

currency_display = DEFAULT_CURRENCY.upper()

st.markdown(
    f"""
    <div style='text-align: center; font-size: 18px; margin-top: 15px;'>

    • Analyse long-term price movements using <b>OHLC</b> data from the CoinGecko API<br>
    • View interactive <b>candlestick charts</b> and <b>closing-price trends</b><br>
    • Explore <b>rolling averages</b> to understand short-term vs. long-term behaviour<br>
    • Select the coin & data range using the sidebar filter on the left<br>
    • Filters apply to all charts and views on this page<br><br>

    Time span: <b>Last {DEFAULT_DAYS} days</b><br>
    Default currency: <b>{currency_display}</b><br><br>

    <i>Note: Historical prices are returned in fixed time intervals by the API and may not represent exact daily values.</i>

    </div>
    """,
    unsafe_allow_html=True,
)

# Data coverage badge
try:
    ts = pd.to_datetime(df_historical["timestamp"].max())

    st.markdown(
        f"""
    <div style="display: flex; justify-content: center; margin-top: 10px;">
        <span style="
            background-color: #1e1e1e;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 14px;
            color: #cccccc;
            border: 1px solid #444;
        ">
            ⏱ Data available up to: <b>{ts.strftime('%Y-%m-%d %H:%M:%S UTC')}</b>
        </span>
    </div>
    """,
        unsafe_allow_html=True,
    )

except Exception:
    st.markdown(
        """
    <div style="display: flex; justify-content: center; margin-top: 10px;">
        <span style="
            background-color: #1e1e1e;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 14px;
            color: #cccccc;
            border: 1px solid #444;
        ">
            ⏱ Data available up to: <b>Unknown</b>
        </span>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")


# Sidebar filters - coins & date range (calendar)
coin_options = sorted(df_historical["display_name"].unique())
selected_display_name = st.sidebar.selectbox(
    "Select cryptocurrency:", coin_options
)

selected_coin_name = selected_display_name.split(" (")[0]

df_coin = df_historical[
    df_historical["coin_name"] == selected_coin_name
].copy()

min_date = df_coin["timestamp"].min()
max_date = df_coin["timestamp"].max()

date_range = st.sidebar.date_input(
    "Select date range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    df_coin = df_coin[
        (df_coin["timestamp"] >= pd.to_datetime(start))
        & (df_coin["timestamp"] <= pd.to_datetime(end))
    ]

# Section Title
st.subheader(f"Historical Data — {selected_display_name}")

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["Candlestick Chart", "Closing Price", "Rolling Averages"]
)

# TAB 1 — Candlestick
with tab1:
    st.markdown("### Candlestick Price Chart")

    fig_candle = go.Figure(
        data=[
            go.Candlestick(
                x=df_coin["timestamp"],
                open=df_coin["open"],
                high=df_coin["high"],
                low=df_coin["low"],
                close=df_coin["close"],
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
            )
        ]
    )

    fig_candle.update_layout(
        template="plotly_dark",
        height=550,
        xaxis_title="Date",
        yaxis_title="Price (GBP)",
    )

    st.plotly_chart(fig_candle, use_container_width=True)

# Closing price tab
with tab2:
    st.markdown("### Closing Price Trend")

    fig_close = go.Figure()

    fig_close.add_trace(
        go.Scatter(
            x=df_coin["timestamp"],
            y=df_coin["close"],
            mode="lines",
            name="Close Price",
            line=dict(width=2),
        )
    )

    fig_close.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Date",
        yaxis_title="Close Price (GBP)",
    )

    st.plotly_chart(fig_close, use_container_width=True)

# Rolling averages tab
with tab3:
    st.markdown("### Moving Averages (MA7 & MA30)")

    fig_roll = go.Figure()

    fig_roll.add_trace(
        go.Scatter(
            x=df_coin["timestamp"],
            y=df_coin["rolling_7d"],
            mode="lines",
            name="7-Day Average",
            line=dict(width=2),
        )
    )

    fig_roll.add_trace(
        go.Scatter(
            x=df_coin["timestamp"],
            y=df_coin["rolling_30d"],
            mode="lines",
            name="30-Day Average",
            line=dict(width=2),
        )
    )

    fig_roll.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Date",
        yaxis_title="Price (GBP)",
    )

    st.plotly_chart(fig_roll, use_container_width=True)
