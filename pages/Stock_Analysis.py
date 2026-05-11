import streamlit as st
import yfinance as yf

@st.cache_data(ttl=600)
def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    return stock.info

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


st.set_page_config(
    page_title="AIML Stock Analysis",
    page_icon="📈",
    layout="wide",
)


st.markdown(
    """
    <style>

    .main {
        background-color: #f5f9ff;
    }

    .title-style {
        font-size: 52px;
        font-weight: 800;
        color: #0b1f33;
        text-align: center;
        margin-bottom: 10px;
    }

    .sub-style {
        font-size: 20px;
        color: #4b6584;
        text-align: center;
        margin-bottom: 35px;
    }

    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0px 4px 18px rgba(0,0,0,0.08);
    }

    div[data-baseweb="select"] {
        background-color: white;
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="title-style">
        AIML Based Stock Prices Analysis & Prediction 📈
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-style">
        Analyze stock performance, financial indicators,
        technical trends, and AI-powered market insights.
    </div>
    """,
    unsafe_allow_html=True
)


# Inputs
col1, col2, col3 = st.columns(3)

today = dt.date.today()

with col1:

    ticker = st.text_input(
        "Stock Ticker",
        "TSLA"
    )

with col2:

    start_date = st.date_input(
        "Choose Start Date",
        dt.date(
            today.year - 1,
            today.month,
            today.day
        ),
    )

with col3:

    end_date = st.date_input(
        "Choose End Date",
        today
    )


st.markdown("---")


# Fetch stock info
stock = yf.Ticker(ticker)

info = stock.info if stock.info else {}


st.subheader(f"{ticker} Company Overview")


st.write(
    info.get(
        "longBusinessSummary",
        "No description available"
    )
)


# Company Metrics
col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Sector",
        info.get("sector", "N/A")
    )

with col2:

    st.metric(
        "Employees",
        info.get("fullTimeEmployees", "N/A")
    )

with col3:

    st.metric(
        "Website",
        info.get("website", "N/A")
    )


st.markdown("## Financial Information")


# Financial tables
col1, col2 = st.columns(2)

with col1:

    df1 = pd.DataFrame(
        index=[
            "Market Cap",
            "Beta",
            "EPS",
            "PE Ratio"
        ]
    )

    df1["Value"] = [

        info.get("marketCap"),

        info.get("beta"),

        info.get("trailingEps"),

        info.get("trailingPE"),
    ]

    st.plotly_chart(
        plotly_table(df1),
        use_container_width=True
    )

with col2:

    df2 = pd.DataFrame(
        index=[
            "Quick Ratio",
            "Revenue per Share",
            "Profit Margins",
            "Debt to Equity",
            "Return on Equity",
        ]
    )

    df2["Value"] = [

        info.get("quickRatio"),

        info.get("revenuePerShare"),

        info.get("profitMargins"),

        info.get("debtToEquity"),

        info.get("returnOnEquity"),
    ]

    st.plotly_chart(
        plotly_table(df2),
        use_container_width=True
    )


st.markdown("## Historical Market Data")


# Download stock data
data = yf.download(
    ticker,
    start=start_date,
    end=end_date
)


# Fix MultiIndex issue
if isinstance(data.columns, pd.MultiIndex):

    data.columns = data.columns.get_level_values(0)


# Metrics
col1, col2, col3 = st.columns(3)

if not data.empty and len(data) >= 2:

    latest_close = float(
        data["Close"].iloc[-1]
    )

    prev_close = float(
        data["Close"].iloc[-2]
    )

    daily_change = latest_close - prev_close

    highest_price = float(
        data['High'].max()
    )

    lowest_price = float(
        data['Low'].min()
    )

    col1.metric(
        "Latest Close Price",
        f"{latest_close:.2f}",
        f"{daily_change:.2f}"
    )

    col2.metric(
        "Highest Price",
        f"{highest_price:.2f}"
    )

    col3.metric(
        "Lowest Price",
        f"{lowest_price:.2f}"
    )

else:

    st.warning(
        "Not enough data to calculate metrics"
    )


# Historical table
last_10_df = data.tail(10) \
                 .sort_index(ascending=False) \
                 .round(3)

fig_df = plotly_table(
    last_10_df
)

st.write("### Historical Data (Last 10 Days)")

st.plotly_chart(
    fig_df,
    use_container_width=True
)


st.markdown("## Technical Analysis")


# Time period buttons
(
    col1,
    col2,
    col3,
    col4,
    col5,
    col6,
    col7
) = st.columns(7)

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


# Chart selection
col1, col2 = st.columns([1, 1])

with col1:

    chart_type = st.selectbox(
        "Chart Type",
        ("Candle", "Line")
    )

with col2:

    if chart_type == "Candle":

        indicators = st.selectbox(
            "Technical Indicator",
            ("RSI", "MACD")
        )

    else:

        indicators = st.selectbox(
            "Technical Indicator",
            ("RSI", "Moving Average", "MACD")
        )


# Historical stock data
ticker_data = yf.Ticker(ticker)

new_df = ticker_data.history(
    period="max"
)

if isinstance(new_df.columns, pd.MultiIndex):

    new_df.columns = new_df.columns.get_level_values(0)


data1 = ticker_data.history(
    period="max"
)

if isinstance(data1.columns, pd.MultiIndex):

    data1.columns = data1.columns.get_level_values(0)


# Chart rendering
if num_period == "1mo":

    if chart_type == "Candle" and indicators == "RSI":

        st.plotly_chart(
            candlestick(data1, "1y"),
            use_container_width=True
        )

        st.plotly_chart(
            RSI(data1, "1y"),
            use_container_width=True
        )

    if chart_type == "Candle" and indicators == "MACD":

        st.plotly_chart(
            candlestick(data1, "1y"),
            use_container_width=True
        )

        st.plotly_chart(
            MACD(data1, "1y"),
            use_container_width=True
        )

    if chart_type == "Line" and indicators == "RSI":

        st.plotly_chart(
            close_chart(data1, "1y"),
            use_container_width=True
        )

        st.plotly_chart(
            RSI(data1, "1y"),
            use_container_width=True
        )

    if chart_type == "Line" and indicators == "Moving Average":

        st.plotly_chart(
            Moving_average(data1, "1y"),
            use_container_width=True
        )

    if chart_type == "Line" and indicators == "MACD":

        st.plotly_chart(
            close_chart(data1, "1y"),
            use_container_width=True
        )

        st.plotly_chart(
            MACD(data1, "1y"),
            use_container_width=True
        )

else:

    if chart_type == "Candle" and indicators == "RSI":

        st.plotly_chart(
            candlestick(new_df, num_period),
            use_container_width=True
        )

        st.plotly_chart(
            RSI(new_df, num_period),
            use_container_width=True
        )

    if chart_type == "Candle" and indicators == "MACD":

        st.plotly_chart(
            candlestick(new_df, num_period),
            use_container_width=True
        )

        st.plotly_chart(
            MACD(new_df, num_period),
            use_container_width=True
        )

    if chart_type == "Line" and indicators == "RSI":

        st.plotly_chart(
            close_chart(new_df, num_period),
            use_container_width=True
        )

        st.plotly_chart(
            RSI(new_df, num_period),
            use_container_width=True
        )

    if chart_type == "Line" and indicators == "Moving Average":

        st.plotly_chart(
            Moving_average(new_df, num_period),
            use_container_width=True
        )

    if chart_type == "Line" and indicators == "MACD":

        st.plotly_chart(
            close_chart(new_df, num_period),
            use_container_width=True
        )

        st.plotly_chart(
            MACD(new_df, num_period),
            use_container_width=True
        )
