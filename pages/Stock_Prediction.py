import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import re
import datetime as dt

from pages.utils.model_train import (
    get_data,
    get_rolling_mean,
    get_differencing_order,
    scaling,
    evaluate_model,
    get_forecast,
    inverse_scaling
)

from pages.utils.plotly_figure import (
    plotly_table,
    Moving_average_forecast
)

# ================== CONFIG ==================
st.set_page_config(
    page_title="AI Stock Prediction",
    page_icon="📈",
    layout="wide",
)

# ================== GEMINI SETUP ==================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ================== GEMINI FUNCTIONS ==================
@st.cache_data(ttl=3600)
def get_ticker_from_company(user_input):
    try:
        prompt = f"""
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

# ✅ fallback mapping (very important)
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

# ✅ AI Investment Tip
@st.cache_data(ttl=300)
def get_ai_investment_tip(ticker):
    try:
        prompt = f"""
        You are a stock advisor.

        Give exactly 2 short investment tips for {ticker}.

        Rules:
        - Only 2 lines
        - Simple language
        - No explanation
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except:
        return "AI insight not available."

# ================== STOCK INFO ==================
@st.cache_data(ttl=600)
def get_stock_info(ticker):
    try:
        return dict(yf.Ticker(ticker).fast_info)
    except:
        return {}

# ================== UI ==================
st.markdown("""
<style>
.main {background-color: #f5f9ff;}
.title-style {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    color: #0b1f33;
}
.sub-style {
    font-size: 20px;
    text-align: center;
    color: #4b6584;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-style">AI Stock Prediction Dashboard 📈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-style">Gemini + ARIMA Forecasting + AI Insights</div>', unsafe_allow_html=True)

# ================== INPUT ==================
col1, col2, col3 = st.columns(3)

with col1:
    company_name = st.text_input("Enter Company Name", "Tesla")

# ✅ AI → ticker
ticker_ai = get_ticker_from_company(company_name)
ticker = fallback_ticker(ticker_ai)

st.success(f"Detected Ticker: {ticker}")

st.subheader(f"Predicting Next 30 Days for: {ticker}")

# ================== DATA ==================
try:
    close_price = get_data(ticker)

    if close_price is None or len(close_price) == 0:
        st.error("No data found. Try another company.")
        st.stop()

except:
    st.error("Error fetching data")
    st.stop()

# ================== MODEL ==================
rolling_price = get_rolling_mean(close_price)

differencing_order = get_differencing_order(rolling_price)

scaled_data, scaler = scaling(rolling_price)

rmse = evaluate_model(scaled_data, differencing_order)

col1, col2 = st.columns(2)

with col1:
    st.metric("Model RMSE", rmse)

with col2:
    st.metric("Prediction Horizon", "30 Days")

# ================== AI BUTTON ==================
st.markdown("## 🤖 AI Investment Insight")

if st.button("🔮 AI Preview"):
    with st.spinner("Generating AI insight..."):
        tip = get_ai_investment_tip(ticker)
    st.info(f"💡 {tip}")

# ================== FORECAST ==================
forecast = get_forecast(scaled_data, differencing_order)

if forecast.empty:
    st.error("Forecast failed")
    st.stop()

forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

# ================== TABLE ==================
st.markdown("## Forecast Data")

fig = plotly_table(forecast.round(3))
st.plotly_chart(fig, width="stretch")

# ================== VISUAL ==================
rolling_price = rolling_price.copy()
rolling_price.columns = ['Close']
rolling_price.index = pd.to_datetime(rolling_price.index)

forecast.index = pd.to_datetime(forecast.index)

rolling_price = rolling_price.reset_index()
forecast = forecast.reset_index()

rolling_price.columns = ['Date','Close']
forecast.columns = ['Date','Close']

combined = pd.concat([rolling_price, forecast], ignore_index=True)
combined = combined.set_index('Date')

# ================== FINAL CHART ==================
st.markdown("## Historical vs Forecast")

st.plotly_chart(
    Moving_average_forecast(combined.iloc[150:]),
    width="stretch"
)
