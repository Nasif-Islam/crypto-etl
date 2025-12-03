import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go

# -------------------------------------------------------------
# IMPORT PROJECT CONFIG
# -------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from src.utils.config import COINS  # noqa: E402

st.set_page_config(page_title="Historical Analysis", layout="wide")

# -------------------------------------------------------------
# LOAD HISTORICAL DATA
# -------------------------------------------------------------
DATA_DIR = ROOT_DIR / "data" / "cleaned"
df_historical = pd.read_csv(DATA_DIR / "historical_crypto_prices.csv")

df_historical["timestamp"] = pd.to_datetime(df_historical["timestamp"])

# -------------------------------------------------------------
# SYMBOL & NAME MAPPING FROM CONFIG
# -------------------------------------------------------------
SYMBOL_MAP = {c["name"]: c["symbol"] for c in COINS}
DISPLAY_NAME_MAP = {c["name"]: f"{c['name']} ({c['symbol']})" for c in COINS}

df_historical["symbol"] = df_historical["coin_name"].map(SYMBOL_MAP)
df_historical["display_name"] = df_historical["coin_name"].map(
    DISPLAY_NAME_MAP
)

# -------------------------------------------------------------
# PAGE TITLE + INTRO
# -------------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0;'>
        Historical Cryptocurrency Analysis
    </h1>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style='text-align: center; font-size: 17px; margin-top: 10px;'>
        Explore long-term price movements, volatility patterns, and market trends.<br>
        View candlestick charts, closing prices, and rolling averages for each cryptocurrency.
    </div>
    """,
    unsafe_allow_html=True,
)

# Optional coverage timestamp
latest = df_historical["timestamp"].max().strftime("%Y-%m-%d")
st.markdown(
    f"<p style='text-align:center; color:#AAAAAA;'>Data available up to: <b>{latest}</b></p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# -------------------------------------------------------------
# SIDEBAR FILTERS: COIN + DATE RANGE
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# SECTION TITLE
# -------------------------------------------------------------
st.subheader(f"Historical Data — {selected_display_name}")

# -------------------------------------------------------------
# TABS FOR DIFFERENT CHARTS
# -------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["Candlestick Chart", "Closing Price", "Rolling Averages"]
)

# -------------------------------------------------------------
# TAB 1 — CANDLESTICK
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# TAB 2 — DAILY CLOSE PRICE
# -------------------------------------------------------------
with tab2:
    st.markdown("### Daily Closing Price")

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

# -------------------------------------------------------------
# TAB 3 — ROLLING AVERAGES
# -------------------------------------------------------------
with tab3:
    st.markdown("### Rolling Averages (7-day & 30-day)")

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
