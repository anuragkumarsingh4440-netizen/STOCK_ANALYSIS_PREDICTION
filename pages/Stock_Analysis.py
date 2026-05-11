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

# ================== GEMINI ==================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

@st.cache_data(ttl=3600)
def get_ticker_from_company(user_input):
    try:
        prompt = f"""
        You are a stock expert.

        Convert company name to Yahoo Finance ticker.

        Rules:
        - Output ONLY ticker
        - Tesla -> TSLA
        - Apple -> AAPL
        - Google -> GOOGL
        - Indian stocks -> .NS

        Company: {user_input}
        """

        response = model.generate_content(prompt)
        ticker = response.text.strip().upper()
        ticker = re.sub(r"[^A-Z\.]", "", ticker)

        return ticker
    except:
        return user_input.upper()

# ✅ fallback mapping (VERY IMPORTANT)
def fallback_ticker(name):
    mapping = {
        "TESLA": "TSLA",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "APPLE": "AAPL",
        "AMAZON": "AMZN",
        "MICROSOFT": "MSFT",
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "INFOSYS": "INFY.NS"
    }
    return mapping.get(name.upper(), name.upper())

# ================== CACHE ==================
@st.cache_data(ttl=600)
def get_stock_info(ticker):
    try:
        return dict(yf.Ticker(ticker).fast_info)
    except:
        return {}

@st.cache_data(ttl=600)
def get_history(ticker):
    try:
        return yf.Ticker(ticker).history(period="max")
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
.title-style {font-size: 52px; font-weight: 800; color: #0b1f33; text-align: center;}
.sub-style {font-size: 20px; color: #4b6584; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-style">AIML Stock Analysis 📈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-style">AI-powered ticker detection</div>', unsafe_allow_html=True)

# ================== INPUT ==================
col1, col2, col3 = st.columns(3)
today = dt.date.today()

with col1:
    company_name = st.text_input("Enter Company Name", "Tesla")

# ✅ AI + fallback
ticker_ai = get_ticker_from_company(company_name)
ticker = fallback_ticker(ticker_ai)

st.success(f"Detected Ticker: {ticker}")

with col2:
    start_date = st.date_input("Start Date", dt.date(today.year-1, today.month, today.day))

with col3:
    end_date = st.date_input("End Date", today)

st.markdown("---")

# ================== STOCK INFO ==================
info = get_stock_info(ticker)

st.subheader(f"{ticker} Company Overview")
st.write(info)

# ================== HISTORICAL ==================
data = download_data(ticker, start_date, end_date)

if data.empty:
    st.error("No data found for this stock. Try another company name.")
    st.stop()

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# ================== METRICS ==================
col1, col2, col3 = st.columns(3)

latest = float(data["Close"].iloc[-1])
prev = float(data["Close"].iloc[-2])

col1.metric("Latest Close", f"{latest:.2f}", f"{latest-prev:.2f}")
col2.metric("High", f"{data['High'].max():.2f}")
col3.metric("Low", f"{data['Low'].min():.2f}")

# ================== TABLE ==================
last_10_df = data.tail(10).sort_index(ascending=False)

st.plotly_chart(plotly_table(last_10_df), width="stretch")

# ================== TECHNICAL ==================
st.markdown("## Technical Analysis")

cols = st.columns(7)
period_map = ["5d","1mo","6mo","ytd","1y","5y","max"]

num_period = "1mo"
for i, label in enumerate(["5D","1M","6M","YTD","1Y","5Y","MAX"]):
    if cols[i].button(label):
        num_period = period_map[i]

# ================== CHART SETTINGS ==================
col1, col2 = st.columns(2)

chart_type = col1.selectbox("Chart Type", ("Candle","Line"))
indicators = col2.selectbox("Indicator", ("RSI","MACD","Moving Average"))

# ================== FETCH DATA ==================
chart_data = get_history(ticker)

if chart_data.empty:
    st.error("No chart data available")
    st.stop()

if isinstance(chart_data.columns, pd.MultiIndex):
    chart_data.columns = chart_data.columns.get_level_values(0)

# ================== CHART ==================
if chart_type == "Candle":
    st.plotly_chart(candlestick(chart_data, num_period), width="stretch")
else:
    st.plotly_chart(close_chart(chart_data, num_period), width="stretch")

# ================== INDICATOR ==================
if indicators == "RSI":
    st.plotly_chart(RSI(chart_data, num_period), width="stretch")

elif indicators == "MACD":
    st.plotly_chart(MACD(chart_data, num_period), width="stretch")

elif indicators == "Moving Average":
    st.plotly_chart(Moving_average(chart_data, num_period), width="stretch")
