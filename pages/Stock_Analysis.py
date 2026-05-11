import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt

from pages.utils.plotly_figure import (
    plotly_table,
    candlestick,
    RSI,
    MACD,
    Moving_average,
    close_chart
)

# ✅ PAGE CONFIG
st.set_page_config(
    page_title="AIML Stock Analysis",
    page_icon="📈",
    layout="wide",
)

# ✅ CACHE FUNCTIONS (VERY IMPORTANT)
@st.cache_data(ttl=600)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.fast_info  # ✅ safe version
    except Exception:
        return {}

@st.cache_data(ttl=600)
def get_stock_history(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def download_data(ticker, start, end):
    try:
        return yf.download(ticker, start=start, end=end)
    except Exception:
        return pd.DataFrame()

# ✅ UI DESIGN
st.markdown("<h1 style='text-align:center;'>AIML Stock Analysis 📈</h1>", unsafe_allow_html=True)

# ✅ INPUTS
col1, col2, col3 = st.columns(3)

today = dt.date.today()

with col1:
    ticker = st.text_input("Stock Ticker", "TSLA")

with col2:
    start_date = st.date_input(
        "Start Date",
        dt.date(today.year - 1, today.month, today.day),
    )

with col3:
    end_date = st.date_input("End Date", today)

st.markdown("---")

# ✅ STOCK INFO
info = get_stock_info(ticker)

st.subheader(f"{ticker} Overview")

st.write("Basic Info (fast API):")
st.write(info)

# ✅ DATA DOWNLOAD
data = download_data(ticker, start_date, end_date)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# ✅ METRICS
col1, col2, col3 = st.columns(3)

if not data.empty and len(data) >= 2:

    latest = float(data["Close"].iloc[-1])
    prev = float(data["Close"].iloc[-2])

    col1.metric("Latest Price", f"{latest:.2f}", f"{latest-prev:.2f}")
    col2.metric("High", f"{data['High'].max():.2f}")
    col3.metric("Low", f"{data['Low'].min():.2f}")

else:
    st.warning("No sufficient data")

# ✅ TABLE
st.write("### Last 10 Days")

last_10 = data.tail(10).sort_index(ascending=False)

st.plotly_chart(plotly_table(last_10), use_container_width=True)

# ✅ TECHNICAL SECTION
st.markdown("## Technical Analysis")

col1, col2 = st.columns(2)

with col1:
    chart_type = st.selectbox("Chart Type", ["Candle", "Line"])

with col2:
    indicators = st.selectbox("Indicator", ["RSI", "MACD", "Moving Average"])

# ✅ PERIOD BUTTONS
col_btn = st.columns(5)

period = "1mo"

if col_btn[0].button("1M"):
    period = "1mo"
if col_btn[1].button("6M"):
    period = "6mo"
if col_btn[2].button("1Y"):
    period = "1y"
if col_btn[3].button("5Y"):
    period = "5y"
if col_btn[4].button("MAX"):
    period = "max"

# ✅ FETCH DATA ONCE
chart_data = get_stock_history(ticker, "max")

if isinstance(chart_data.columns, pd.MultiIndex):
    chart_data.columns = chart_data.columns.get_level_values(0)

# ✅ PLOTTING
if chart_type == "Candle":
    st.plotly_chart(candlestick(chart_data, period), use_container_width=True)
else:
    st.plotly_chart(close_chart(chart_data, period), use_container_width=True)

# ✅ INDICATORS
if indicators == "RSI":
    st.plotly_chart(RSI(chart_data, period), use_container_width=True)

elif indicators == "MACD":
    st.plotly_chart(MACD(chart_data, period), use_container_width=True)

elif indicators == "Moving Average":
    st.plotly_chart(Moving_average(chart_data, period), use_container_width=True)
