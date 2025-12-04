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

st.set_page_config(page_title="Cryptocurrency Comparison", layout="wide")

# Load historical data
DATA_DIR = ROOT_DIR / "data" / "cleaned"
df_historical = pd.read_csv(DATA_DIR / "historical_crypto_prices.csv")

# Ensure timestamp is datetime
df_historical["timestamp"] = pd.to_datetime(df_historical["timestamp"])

# Symbol & display name mapping
SYMBOL_MAP = {c["name"]: c["symbol"] for c in COINS}
DISPLAY_NAME_MAP = {c["name"]: f"{c['name']} ({c['symbol']})" for c in COINS}

df_historical["symbol"] = df_historical["coin_name"].map(SYMBOL_MAP)
df_historical["display_name"] = df_historical["coin_name"].map(DISPLAY_NAME_MAP)

# Page header & description
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0;'>
        Cryptocurrency Comparison
    </h1>
    """,
    unsafe_allow_html=True,
)

currency_display = DEFAULT_CURRENCY.upper()

st.markdown(
    f"""
    <div style='text-align: center; font-size: 18px; margin-top: 15px;'>

    • Compare multiple cryptocurrencies across <b>price</b>, <b>performance</b> and <b>volatility</b><br>
    • Select one or more coins using the sidebar filter on the left<br>
    • Adjust the date range to focus on specific market conditions<br>
    • Filters apply to all charts and views on this page<br><br>

    Time span: <b>Last {DEFAULT_DAYS} days</b><br>
    Default currency: <b>{currency_display}</b><br><br>

    <i>Note: Historical prices are returned in fixed time intervals determined by the API and may not represent exact daily values</i>

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

# Sidebar filters — coins & date range
coin_options = sorted(df_historical["display_name"].unique())

selected_display_names = st.sidebar.multiselect(
    "Select cryptocurrencies to compare:",
    coin_options,
    default=coin_options,
)

if not selected_display_names:
    st.sidebar.warning("Please select at least one cryptocurrency.")
    st.stop()

df_filtered = df_historical[
    df_historical["display_name"].isin(selected_display_names)
].copy()

min_date = df_filtered["timestamp"].min()
max_date = df_filtered["timestamp"].max()

date_range = st.sidebar.date_input(
    "Select date range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    df_filtered = df_filtered[
        (df_filtered["timestamp"] >= pd.to_datetime(start))
        & (df_filtered["timestamp"] <= pd.to_datetime(end))
    ]

# Stops if filters cause no data to be shown - handles edge cases
if df_filtered.empty:
    st.warning("No data available for the selected coins and date range.")
    st.stop()

# Dynamic color palette
COLOR_SEQUENCE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

symbols = df_filtered["symbol"].unique().tolist()
color_map = {
    sym: COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)] for i, sym in enumerate(symbols)
}

# Map colors back into df
df_filtered["color"] = df_filtered["symbol"].map(color_map)

# Section title
st.subheader("Cryptocurrency Comparison")

tab_price, tab_norm, tab_vol = st.tabs(
    ["Price", "Normalized Performance", "Volatility"]
)

# Price Comparison tab (close)
with tab_price:
    st.markdown("### Price Comparison (Close Price)")

    fig_price = go.Figure()

    for name in selected_display_names:
        df_coin = (
            df_filtered[df_filtered["display_name"] == name]
            .sort_values("timestamp")
            .copy()
        )

        fig_price.add_trace(
            go.Scatter(
                x=df_coin["timestamp"],
                y=df_coin["close"],
                mode="lines",
                name=name,
                line=dict(width=2, color=df_coin["color"].iloc[0]),
            )
        )

    fig_price.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Date",
        yaxis_title=f"Close Price ({currency_display})",
        legend_title="Cryptocurrency",
    )

    st.plotly_chart(fig_price, use_container_width=True)

# Normalized Performance tab
with tab_norm:
    st.markdown("### Normalized Performance (from start of selected range)")

    fig_norm = go.Figure()

    for name in selected_display_names:
        df_coin = (
            df_filtered[df_filtered["display_name"] == name]
            .sort_values("timestamp")
            .copy()
        )

        # Normalize based on first close in the filtered date range
        first_close = df_coin["close"].iloc[0]
        df_coin["norm_return_pct"] = (df_coin["close"] / first_close - 1.0) * 100.0

        fig_norm.add_trace(
            go.Scatter(
                x=df_coin["timestamp"],
                y=df_coin["norm_return_pct"],
                mode="lines",
                name=name,
                line=dict(width=2, color=df_coin["color"].iloc[0]),
            )
        )

    fig_norm.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Date",
        yaxis_title="Normalized Return (%)",
        legend_title="Cryptocurrency",
    )

    st.plotly_chart(fig_norm, use_container_width=True)

# Volatility Comparison tab
with tab_vol:
    st.markdown("### Volatility Comparison (Rolling 7-period)")

    fig_vol = go.Figure()

    for name in selected_display_names:
        df_coin = (
            df_filtered[df_filtered["display_name"] == name]
            .sort_values("timestamp")
            .copy()
        )

        # Compute rolling volatility based on percentage change in close
        pct_change = df_coin["close"].pct_change()
        df_coin["rolling_volatility_pct"] = pct_change.rolling(window=7).std() * 100.0

        fig_vol.add_trace(
            go.Scatter(
                x=df_coin["timestamp"],
                y=df_coin["rolling_volatility_pct"],
                mode="lines",
                name=name,
                line=dict(width=2, color=df_coin["color"].iloc[0]),
            )
        )

    fig_vol.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Date",
        yaxis_title="Rolling Volatility (7-period, %)",
        legend_title="Cryptocurrency",
    )

    st.plotly_chart(fig_vol, use_container_width=True)
