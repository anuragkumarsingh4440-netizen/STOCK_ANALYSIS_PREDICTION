import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import re

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

# ================== GEMINI ==================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# ================== FUNCTIONS ==================
@st.cache_data(ttl=3600)
def get_ticker_from_company(user_input):
    try:
        prompt = f"""
        Convert company name to Yahoo Finance ticker.

        Rules:
        Only ticker output

        Examples:
        Tesla -> TSLA
        Apple -> AAPL
        Google -> GOOGL
        Reliance -> RELIANCE.NS

        Company: {user_input}
        """
        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            ticker = response.text.strip().upper()
        else:
            ticker = response.candidates[0].content.parts[0].text.strip()

        return re.sub(r"[^A-Z\.]", "", ticker)

    except:
        return user_input.upper()


def fallback_ticker(name):
    mapping = {
        "TESLA": "TSLA",
        "APPLE": "AAPL",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "AMAZON": "AMZN",
        "MICROSOFT": "MSFT",
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "INFOSYS": "INFY.NS"
    }
    return mapping.get(name.upper(), name.upper())


# ✅ ✅ UPDATED AI FUNCTION (FORECAST BASED)
@st.cache_data(ttl=300)
def get_ai_investment_tip(ticker, forecast_df):
    try:

        # ✅ convert forecast to text
        table_text = forecast_df[['Close']].tail(10).to_string()

        prompt = f"""
        You are a stock expert.

        Analyze this predicted stock price data:

        {table_text}

        Give 2 short investment tips.

        Rules:
        - Only 2 lines
        - No explanation
        - Simple language
        - Based on trend (rising/falling)
        """

        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            return response.candidates[0].content.parts[0].text.strip()

    except Exception as e:
        return f"AI Error: {e}"


# ================== UI ==================
st.markdown("""
<style>
.main {background-color: #f5f9ff;}
.title-style {font-size: 48px; font-weight: 800; text-align: center;}
.sub-style {font-size: 20px; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-style">AI Stock Prediction 📈</div>', unsafe_allow_html=True)

# ================== INPUT ==================
company_name = st.text_input("Enter Company Name", "Tesla")

ticker = fallback_ticker(get_ticker_from_company(company_name))

st.success(f"Ticker: {ticker}")

# ================== DATA ==================
close_price = get_data(ticker)

if close_price is None or len(close_price) == 0:
    st.error("No data found")
    st.stop()

# ================== MODEL ==================
rolling_price = get_rolling_mean(close_price)
differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)

rmse = evaluate_model(scaled_data, differencing_order)
st.metric("RMSE", rmse)

# ================== FORECAST ==================
forecast = get_forecast(scaled_data, differencing_order)

if forecast.empty:
    st.error("Forecast failed")
    st.stop()

forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

# ================== TABLE ==================
st.markdown("## Forecast Data")
st.plotly_chart(plotly_table(forecast), width="stretch")

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

st.plotly_chart(
    Moving_average_forecast(combined.iloc[150:]),
    width="stretch"
)

# ✅ ✅ ✅ BUTTON AT END
st.markdown("## 🤖 AI Investment Insight")

if st.button("🔮 AI Preview"):
    with st.spinner("Analyzing forecast..."):
        tip = get_ai_investment_tip(ticker, forecast)

    st.info(f"💡 {tip}")
``
