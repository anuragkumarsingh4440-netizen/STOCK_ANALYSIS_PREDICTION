import streamlit as st

from pages.utils.model_train import (
    get_data,
    get_rolling_mean,
    get_differencing_order,
    scaling,
    evaluate_model,
    get_forecast,
    inverse_scaling
)

import pandas as pd

from pages.utils.plotly_figure import (
    plotly_table,
    Moving_average_forecast
)


st.set_page_config(

    page_title="Stock Prediction",

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
        font-size: 48px;
        font-weight: 800;
        color: #0b1f33;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-style {
        font-size: 20px;
        color: #4b6584;
        text-align: center;
        margin-bottom: 35px;
    }

    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 18px rgba(0,0,0,0.08);
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="title-style">
        AI Stock Price Prediction Dashboard 📈
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-style">
        Predict future stock prices using ARIMA forecasting models
        and historical stock market trends.
    </div>
    """,
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)

with col1:

    ticker = st.text_input(
        'Stock Ticker',
        'TSLA'
    )


st.subheader(
    'Predicting Next 30 Days Close Price for: ' + ticker
)


# Load stock data
close_price = get_data(ticker)

rolling_price = get_rolling_mean(
    close_price
)


# Find differencing order
differencing_order = get_differencing_order(
    rolling_price
)


# Scaling
scaled_data, scaler = scaling(
    rolling_price
)


# Evaluate model
rmse = evaluate_model(
    scaled_data,
    differencing_order
)


col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Model RMSE Score",
        rmse
    )

with col2:

    st.metric(
        "Forecast Horizon",
        "30 Days"
    )


# Forecast future values
forecast = get_forecast(
    scaled_data,
    differencing_order
)


# Inverse scaling
forecast['Close'] = inverse_scaling(
    scaler,
    forecast['Close']
)


st.markdown("## Forecasted Data")


# Forecast table
fig_tail = plotly_table(

    forecast.sort_index(
        ascending=True
    ).round(3)

)

fig_tail.update_layout(
    height=220
)

st.plotly_chart(
    fig_tail,
    use_container_width=True
)


# Prepare for visualization
rolling_price = rolling_price.copy()

rolling_price.columns = ['Close']

rolling_price.index = pd.to_datetime(
    rolling_price.index
)

forecast.index = pd.to_datetime(
    forecast.index
)


rolling_price = rolling_price.reset_index()

forecast = forecast.reset_index()


rolling_price.columns = [
    'Date',
    'Close'
]

forecast.columns = [
    'Date',
    'Close'
]


forecast = pd.concat(
    [rolling_price, forecast],
    ignore_index=True
)

forecast = forecast.set_index(
    'Date'
)


st.markdown("## Historical vs Forecasted Stock Price")


st.plotly_chart(
    Moving_average_forecast(
        forecast.iloc[150:]
    ),
    use_container_width=True
)