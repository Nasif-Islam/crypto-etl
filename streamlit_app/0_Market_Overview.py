import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.utils.config import CURRENCIES, DEFAULT_CURRENCY, COINS  # noqa: E402

st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide")

# Load data
DATA_DIR = ROOT_DIR / "data" / "cleaned"
df_current = pd.read_csv(DATA_DIR / "current_crypto_prices.csv")

# Dynamic symbol + display name mapping from config
SYMBOL_MAP = {c["name"]: c["symbol"] for c in COINS}
DISPLAY_NAME_MAP = {c["name"]: f"{c['name']} ({c['symbol']})" for c in COINS}

df_current["symbol"] = df_current["coin_name"].map(SYMBOL_MAP)
df_current["display_name"] = df_current["coin_name"].map(DISPLAY_NAME_MAP)

# Sidebar currency selector
currency_options = [c.upper() for c in CURRENCIES]

currency = st.sidebar.radio(
    "Currency (only applies to current prices):",
    currency_options,
    index=currency_options.index(DEFAULT_CURRENCY.upper()),
)

currency_lower = currency.lower()

df_filtered = df_current[df_current["currency"] == currency_lower].copy()

# Dynamic color palette for graphs
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

df_filtered["color"] = df_filtered["symbol"].map(color_map)

# Page header
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0;'>
        Cryptocurrency Dashboard
    </h1>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h3 style='text-align: center; margin-top: 0;'>
        Live Cryptocurrency Market Overview
    </h3>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style='text-align: center; font-size: 18px; margin-top: 15px;'>

    • Live cryptocurrency prices updated directly from the <b>CoinGecko API<b><br>
    • <b>Market capitalization</b> — total value of each cryptocurrency<br>
    • <b>24h price change (%)</b> — percentage movement over the past day<br>
    • <b>24h trading volume</b> — total value traded in the last 24 hours<br><br>

    Use the <b>currency selector</b> in the left sidebar to view prices in various currencies
    </div>
    """,
    unsafe_allow_html=True,
)

# Timestamp (badge style)
try:
    ts = pd.to_datetime(df_filtered["timestamp"].max())

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
            ⏱ Last Updated: <b>{ts.strftime('%Y-%m-%d %H:%M:%S UTC')}</b>
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
            ⏱ Last Updated: <b>Unknown</b>
        </span>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")


# Format data for display
def fmt(num):
    if abs(num) >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    return f"{num:,.2f}"


df_display = df_filtered.copy()
df_display["price_fmt"] = df_display["price"].apply(fmt)
df_display["market_cap_fmt"] = df_display["market_cap"].apply(fmt)
df_display["volume_24h_fmt"] = df_display["volume_24h"].apply(fmt)
df_display["change_24h_fmt"] = df_display["change_24h"].map(lambda x: f"{x:.2f}%")

# Tabs
tab_overview, tab_prices, tab_market_cap, tab_volume = st.tabs(
    ["Overview", "Prices", "Market Cap", "Volume"]
)

# Overview tab
with tab_overview:
    st.subheader(f"Market Snapshot ({currency})")

    kpi_cols = st.columns(len(df_display))

    for col, (_, row) in zip(kpi_cols, df_display.iterrows()):
        delta_color = "normal" if row["change_24h"] >= 0 else "inverse"

        col.metric(
            label=row["display_name"],
            value=f"{row['price_fmt']} {currency}",
            delta=f"{row['change_24h']:.2f}%",
            delta_color=delta_color,
        )

    st.markdown("---")

    st.markdown("#### Current Price Table")

    table_df = df_display[
        [
            "display_name",
            "currency",
            "price_fmt",
            "market_cap_fmt",
            "volume_24h_fmt",
            "change_24h_fmt",
        ]
    ].rename(
        columns={
            "display_name": "Cryptocurrency",
            "currency": "Currency",
            "price_fmt": "Price",
            "market_cap_fmt": "Market Cap",
            "volume_24h_fmt": "24h Volume",
            "change_24h_fmt": "24h Change",
        }
    )

    st.dataframe(table_df, width="stretch")

# Prices tabs
with tab_prices:
    st.subheader(f"Price Comparison ({currency})")

    fig_price = go.Figure()

    for _, row in df_display.iterrows():
        fig_price.add_trace(
            go.Bar(
                x=[row["symbol"]],
                y=[row["price"]],
                marker_color=row["color"],
                name=row["display_name"],
            )
        )

    use_log_price = st.checkbox(
        "Logarithmic Scale (Price)", value=True, key="log_price"
    )

    if use_log_price:
        fig_price.update_yaxes(type="log")

    fig_price.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Cryptocurrency",
        yaxis_title=f"Price ({currency})",
        showlegend=False,
    )

    st.plotly_chart(fig_price, width="stretch")

    st.markdown("---")

    st.subheader("24-Hour Price Change (%)")

    fig_change = go.Figure()

    for _, row in df_display.iterrows():
        fig_change.add_trace(
            go.Bar(
                x=[row["symbol"]],
                y=[row["change_24h"]],
                marker_color=row["color"],
                name=row["display_name"],
            )
        )

    fig_change.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Cryptocurrency",
        yaxis_title="Daily % Change",
        showlegend=False,
    )

    st.plotly_chart(fig_change, width="stretch")

# Market cap tab
with tab_market_cap:
    st.subheader("Market Capitalization")

    use_log_market = st.checkbox(
        "Logarithmic Scale (Market Cap)", value=True, key="log_market"
    )

    fig_market = go.Figure()

    for _, row in df_display.iterrows():
        fig_market.add_trace(
            go.Bar(
                x=[row["symbol"]],
                y=[row["market_cap"]],
                marker_color=row["color"],
                name=row["display_name"],
            )
        )

    fig_market.update_yaxes(type="log" if use_log_market else "linear")

    fig_market.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Cryptocurrency",
        yaxis_title=f"Market Cap ({currency})",
        showlegend=False,
    )

    st.plotly_chart(fig_market, width="stretch")

# Volume tab
with tab_volume:
    st.subheader("24-Hour Trading Volume")

    use_log_volume = st.checkbox(
        "Logarithmic Scale (Volume)", value=True, key="log_volume"
    )

    fig_vol = go.Figure()

    for _, row in df_display.iterrows():
        fig_vol.add_trace(
            go.Bar(
                x=[row["symbol"]],
                y=[row["volume_24h"]],
                marker_color=row["color"],
                name=row["display_name"],
            )
        )

    fig_vol.update_yaxes(type="log" if use_log_volume else "linear")

    fig_vol.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Cryptocurrency",
        yaxis_title=f"Volume ({currency})",
        showlegend=False,
    )

    st.plotly_chart(fig_vol, width="stretch")
