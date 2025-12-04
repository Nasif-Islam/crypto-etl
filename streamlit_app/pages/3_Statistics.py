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

st.set_page_config(page_title="Cryptocurrency Statistics", layout="wide")

# Load Data
DATA_DIR = ROOT_DIR / "data" / "cleaned"

# Summary metrics
STATS_PATH = DATA_DIR / "historical_crypto_stats.csv"
df_stats = pd.read_csv(STATS_PATH)

# Historical data for timestamp badge
HIST_PATH = DATA_DIR / "historical_crypto_prices.csv"
df_hist = pd.read_csv(HIST_PATH)
df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"])

# Validate stats file
expected_cols = {
    "coin_id",
    "coin_name",
    "max_close",
    "min_close",
    "mean_volatility",
    "total_return",
}
missing = expected_cols - set(df_stats.columns)
if missing:
    st.error(f"Missing expected columns in stats CSV: {missing}")
    st.stop()

# Symbol + Icon Mapping
SYMBOL_MAP = {c["name"]: c["symbol"] for c in COINS}
df_stats["symbol"] = df_stats["coin_name"].map(SYMBOL_MAP)

# Page Header
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0;'>
        Cryptocurrency Statistics Overview
    </h1>
    """,
    unsafe_allow_html=True,
)

currency_display = DEFAULT_CURRENCY.upper()

# Description
st.markdown(
    f"""
    <div style='text-align: center; font-size: 18px; margin-top: 15px;'>

    • High-level summary of overall performance, volatility, and long-term return<br>
    • Calculated using the full OHLC dataset extracted from the CoinGecko API<br><br>

    Time span: <b>Last {DEFAULT_DAYS} days</b><br>
    Default currency: <b>{currency_display}</b><br><br>

    </div>
    """,
    unsafe_allow_html=True,
)

# Timestamp badge
try:
    ts = df_hist["timestamp"].max()
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
    pass

st.markdown("---")

# Dynamic Colour Mapping
COLOR_SEQUENCE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
]

symbols = df_stats["symbol"].tolist()
color_map = {
    sym: COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)]
    for i, sym in enumerate(symbols)
}
df_stats["color"] = df_stats["symbol"].map(color_map)


# Helpers function for formatting
def fmt_price(x: float) -> str:
    return f"{x:,.2f}"


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


# KPI Cards
st.write("")

st.subheader("Key Metrics by Cryptocurrency")

cols = st.columns(len(df_stats))

for col, (_, row) in zip(cols, df_stats.iterrows()):
    coin = row["coin_name"]

    with col:
        card_html = f"""
        <div style='
            border: 1px solid #333;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            background-color: #111;
        '>
            <h4 style='margin-bottom: 6px;'>{coin}</h4>
            <p>Max Close: <b>{fmt_price(row['max_close'])}</b></p>
            <p>Min Close: <b>{fmt_price(row['min_close'])}</b></p>
            <p>Mean Volatility: <b>{fmt_pct(row['mean_volatility'])}</b></p>
            <p>Total Return: <b>{fmt_pct(row['total_return'])}</b></p>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")

# Risk vs Return Scatter Plot
st.subheader("Risk vs Return Analysis")

fig_rr = go.Figure()

for _, row in df_stats.iterrows():
    fig_rr.add_trace(
        go.Scatter(
            x=[row["mean_volatility"] * 100],
            y=[row["total_return"] * 100],
            mode="markers+text",
            text=[row["coin_name"]],
            textposition="top center",
            marker=dict(
                size=14,
                color=row["color"],
            ),
            name=row["coin_name"],
        )
    )

fig_rr.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Mean Volatility (%)",
    yaxis_title="Total Return (%)",
    showlegend=False,
)

st.plotly_chart(fig_rr, use_container_width=True)
