import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt

from pages.utils.plotly_figure import (
    plotly_table,
    candlestick,
    RSI,
    MACD,
    Moving_average,
    close_chart
)

# ✅ ADD THIS FUNCTION (FIX)
@st.cache_data(ttl=600)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.fast_info   # ✅ safe
    except:
        return {}

st.set_page_config(
    page_title="AIML Stock Analysis",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
.main {background-color: #f5f9ff;}
.title-style {font-size: 52px; font-weight: 800; color: #0b1f33; text-align: center;}
.sub-style {font-size: 20px; color: #4b6584; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-style">AIML Based Stock Prices Analysis 📈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-style">Analyze stock performance</div>', unsafe_allow_html=True)

# INPUTS
col1, col2, col3 = st.columns(3)
today = dt.date.today()

with col1:
    ticker = st.text_input("Stock Ticker", "TSLA")

with col2:
    start_date = st.date_input("Start Date", dt.date(today.year-1, today.month, today.day))

with col3:
    end_date = st.date_input("End Date", today)

st.markdown("---")

# ✅ ✅ FIXED LINE (IMPORTANT)
info = get_stock_info(ticker)

st.subheader(f"{ticker} Company Overview")

st.write(info)   # (fast_info doesn't have long summary)

# METRICS (same structure)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Last Price", info.get("lastPrice", "N/A"))

with col2:
    st.metric("Market Cap", info.get("marketCap", "N/A"))

with col3:
    st.metric("Volume", info.get("lastVolume", "N/A"))

st.markdown("## Historical Market Data")

data = yf.download(ticker, start=start_date, end=end_date)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

col1, col2, col3 = st.columns(3)

if not data.empty and len(data) >= 2:

    latest_close = float(data["Close"].iloc[-1])
    prev_close = float(data["Close"].iloc[-2])

    col1.metric("Latest Close", f"{latest_close:.2f}", f"{latest_close-prev_close:.2f}")
    col2.metric("High", f"{data['High'].max():.2f}")
    col3.metric("Low", f"{data['Low'].min():.2f}")

else:
    st.warning("Not enough data")

last_10_df = data.tail(10).sort_index(ascending=False).round(3)

st.plotly_chart(plotly_table(last_10_df), use_container_width=True)

st.markdown("## Technical Analysis")

(col1, col2, col3, col4, col5, col6, col7) = st.columns(7)

num_period = "1mo"

with col1:
    if st.button("5D"):
        num_period = "5d"

with col2:
    if st.button("1M"):
        num_period = "1mo"

with col3:
    if st.button("6M"):
        num_period = "6mo"

with col4:
    if st.button("YTD"):
        num_period = "ytd"

with col5:
    if st.button("1Y"):
        num_period = "1y"

with col6:
    if st.button("5Y"):
        num_period = "5y"

with col7:
    if st.button("MAX"):
        num_period = "max"

col1, col2 = st.columns([1, 1])

with col1:
    chart_type = st.selectbox("Chart Type", ("Candle", "Line"))

with col2:
    indicators = st.selectbox("Indicator", ("RSI", "Moving Average", "MACD"))

ticker_data = yf.Ticker(ticker)

new_df = ticker_data.history(period="max")

if isinstance(new_df.columns, pd.MultiIndex):
    new_df.columns = new_df.columns.get_level_values(0)

# ✅ removing duplicate data1 call (safe optimization)
data1 = new_df

# CHART
if chart_type == "Candle":
    st.plotly_chart(candlestick(new_df, num_period), use_container_width=True)
else:
    st.plotly_chart(close_chart(new_df, num_period), use_container_width=True)

# INDICATORS
if indicators == "RSI":
    st.plotly_chart(RSI(new_df, num_period), use_container_width=True)

elif indicators == "MACD":
    st.plotly_chart(MACD(new_df, num_period), use_container_width=True)

elif indicators == "Moving Average":
    st.plotly_chart(Moving_average(new_df, num_period), use_container_width=True)
