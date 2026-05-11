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
        prompt = f"Convert company name into stock ticker: {user_input}"

        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            ticker = response.text
        else:
            ticker = response.candidates[0].content.parts[0].text

        ticker = ticker.strip().upper()
        ticker = re.sub(r"[^A-Z.]", "", ticker)

        return ticker

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


# ✅ AI function using forecast data
@st.cache_data(ttl=300)
def get_ai_investment_tip(ticker, forecast_df):
    try:
        # ✅ clean formatted table
        table_text = forecast_df[["Close"]].tail(10).to_string(
            float_format="%.2f"
        )

        # ✅ safe prompt (no syntax issues)
        prompt = (
            f"Stock: {ticker}\n\n"
            f"Predicted Prices:\n{table_text}\n\n"
            "Give exactly 2 short investment tips based on trend only."
        )

        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        elif hasattr(response, "candidates"):
            return response.candidates[0].content.parts[0].text.strip()

        else:
            return "No AI response."

    except Exception as e:
        return f"AI Error: {str(e)}"


# ================== UI ==================

st.title("📈 AI Stock Prediction Dashboard")

company_name = st.text_input("Enter Company Name", "Tesla")

ticker = fallback_ticker(get_ticker_from_company(company_name))

st.success(f"Detected Ticker: {ticker}")

# ================== DATA ==================

close_price = get_data(ticker)

if close_price is None or len(close_price) == 0:
    st.error("No data found for this stock")
    st.stop()

# ================== MODEL ==================

rolling_price = get_rolling_mean(close_price)
differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)

rmse = evaluate_model(scaled_data, differencing_order)

st.metric("📊 RMSE Score", rmse)

# ================== FORECAST ==================

forecast = get_forecast(scaled_data, differencing_order)

if forecast.empty:
    st.error("Forecast failed")
    st.stop()

forecast["Close"] = inverse_scaling(scaler, forecast["Close"])

# ✅ ✅ CLEAN FORMATTING
forecast = forecast.copy()
forecast["Close"] = forecast["Close"].round(2)
forecast.index = pd.to_datetime(forecast.index)

# ================== TABLE ==================

st.markdown("## 📊 Forecast Data")

st.plotly_chart(
    plotly_table(forecast),
    width="stretch"
)

# ================== VISUAL ==================

rolling_price = rolling_price.copy()
rolling_price.columns = ["Close"]
rolling_price.index = pd.to_datetime(rolling_price.index)

forecast_visual = forecast.copy()

rolling_price = rolling_price.reset_index()
forecast_visual = forecast_visual.reset_index()

rolling_price.columns = ["Date", "Close"]
forecast_visual.columns = ["Date", "Close"]

combined = pd.concat([rolling_price, forecast_visual], ignore_index=True)
combined = combined.set_index("Date")

st.markdown("## 📈 Historical vs Forecast")

st.plotly_chart(
    Moving_average_forecast(combined.iloc[150:]),
    width="stretch"
)

# ================== ✅ AI BUTTON AT END ==================

st.markdown("## 🤖 AI Investment Insight")

if st.button("🔮 AI Preview"):
    with st.spinner("Analyzing forecast..."):
        tip = get_ai_investment_tip(ticker, forecast)

    st.info(f"💡 {tip}")
