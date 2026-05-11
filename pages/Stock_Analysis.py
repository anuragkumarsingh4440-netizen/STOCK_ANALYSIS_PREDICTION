import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import google.generativeai as genai
import re

from pages.utils.plotly_figure import (
    plotly_table,
    candlestick,
    RSI,
    MACD,
    Moving_average,
    close_chart
)

# ================== CONFIG ==================
st.set_page_config(
    page_title="AIML Stock Analysis",
    page_icon="📈",
    layout="wide",
)

# ================== GEMINI SETUP ==================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

@st.cache_data(ttl=3600)
def get_ticker_from_company(user_input):
    try:
        prompt = f"""
        Convert the following company name into its stock ticker symbol.

        Rules:
        - Only return ticker (no explanation)
        - Indian stocks → add .NS
        - US stocks → normal format

        Company: {user_input}
        """

        response = model.generate_content(prompt)
        ticker = response.text.strip().upper()

        # ✅ clean output
        ticker = re.sub(r"[^A-Z\.]", "", ticker)

        return ticker
    except:
        return user_input.upper()

# ================== CACHE (FIXED) ==================
@st.cache_data(ttl=600)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return dict(stock.fast_info)   # ✅ fix
    except:
        return {}

@st.cache_data(ttl=600)
def get_history(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period="max")
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def download_data(ticker, start, end):
    try:
        return yf.download(ticker, start=start, end=end)
    except:
        return pd.DataFrame()

# ================== UI ==================
st.markdown("""
<style>
.main {background-color: #f5f9ff;}
.title-style {
    font-size: 52px;
    font-weight: 800;
    color: #0b1f33;
    text-align: center;
}
.sub-style {
    font-size: 20px;
    color: #4b6584;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-style">AIML Stock Analysis 📈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-style">AI-powered ticker detection + analysis</div>', unsafe_allow_html=True)

# ================== INPUT ==================
col1, col2, col3 = st.columns(3)
today = dt.date.today()

with col1:
    company_name = st.text_input("Enter Company Name", "Tesla")

# ✅ Convert to ticker using Gemini
ticker = get_ticker_from_company(company_name)

st.success(f"Detected Ticker: {ticker}")

with col2:
    start_date = st.date_input(
        "Start Date",
        dt.date(today.year - 1, today.month, today.day)
    )

with col3:
    end_date = st.date_input("End Date", today)

st.markdown("---")

# ================== STOCK INFO ==================
info = get_stock_info(ticker)

st.subheader(f"{ticker} Company Overview")

st.write("Basic Info:")
st.write(info)

# ================== METRICS ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Last Price", info.get("lastPrice", "N/A"))

with col2:
    st.metric("Market Cap", info.get("marketCap", "N/A"))

with col3:
    st.metric("Volume", info.get("lastVolume", "N/A"))

# ================== HISTORICAL DATA ==================
st.markdown("## Historical Market Data")

data = download_data(ticker, start_date, end_date)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

col1, col2, col3 = st.columns(3)

if not data.empty and len(data) >= 2:
    latest = float(data["Close"].iloc[-1])
    prev = float(data["Close"].iloc[-2])

    col1.metric("Latest Close", f"{latest:.2f}", f"{latest-prev:.2f}")
    col2.metric("Highest Price", f"{data['High'].max():.2f}")
    col3.metric("Lowest Price", f"{data['Low'].min():.2f}")
else:
    st.warning("Not enough data")

# ================== TABLE ==================
last_10_df = data.tail(10).sort_index(ascending=False).round(3)

st.write("### Historical Data (Last 10 Days)")

st.plotly_chart(
    plotly_table(last_10_df),
    use_container_width=True
)

# ================== TECHNICAL ==================
st.markdown("## Technical Analysis")

(col1, col2, col3, col4, col5, col6, col7) = st.columns(7)

num_period = "1mo"

with col1:
    if st.button("5D"): num_period = "5d"
with col2:
    if st.button("1M"): num_period = "1mo"
with col3:
    if st.button("6M"): num_period = "6mo"
with col4:
    if st.button("YTD"): num_period = "ytd"
with col5:
    if st.button("1Y"): num_period = "1y"
with col6:
    if st.button("5Y"): num_period = "5y"
with col7:
    if st.button("MAX"): num_period = "max"

# ================== CHART SETTINGS ==================
col1, col2 = st.columns([1, 1])

with col1:
    chart_type = st.selectbox("Chart Type", ("Candle", "Line"))

with col2:
    if chart_type == "Candle":
        indicators = st.selectbox("Technical Indicator", ("RSI", "MACD"))
    else:
        indicators = st.selectbox("Technical Indicator", ("RSI", "Moving Average", "MACD"))

# ================== FETCH DATA ==================
chart_data = get_history(ticker)

if isinstance(chart_data.columns, pd.MultiIndex):
    chart_data.columns = chart_data.columns.get_level_values(0)

# ================== CHART ==================
if chart_type == "Candle":
    st.plotly_chart(candlestick(chart_data, num_period), use_container_width=True)
else:
    st.plotly_chart(close_chart(chart_data, num_period), use_container_width=True)

# ================== INDICATORS ==================
if indicators == "RSI":
    st.plotly_chart(RSI(chart_data, num_period), use_container_width=True)

elif indicators == "MACD":
    st.plotly_chart(MACD(chart_data, num_period), use_container_width=True)

elif indicators == "Moving Average":
    st.plotly_chart(Moving_average(chart_data, num_period), use_container_width=True)
