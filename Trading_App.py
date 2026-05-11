import streamlit as st

st.set_page_config(
    page_title="Trading App",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #020617, #0f172a);
}

.main-title {
    text-align: center;
    color: white;
    font-size: 60px;
    font-weight: 800;
    margin-top: 20px;
}

.sub-title {
    text-align: center;
    color: #cbd5e1;
    font-size: 22px;
    margin-bottom: 40px;
}

.hero-box {
    background: linear-gradient(to right, #001233, #001845);
    padding: 45px;
    border-radius: 20px;
    margin-bottom: 40px;
    border: 1px solid #2563eb;
}

.hero-title {
    color: white;
    text-align: center;
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 15px;
}

.hero-text {
    color: #dbeafe;
    text-align: center;
    font-size: 20px;
    line-height: 1.8;
}

.service-heading {
    color: white;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 25px;
}

.card {
    background-color: white;
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 25px;
    min-height: 280px;
}

.card-title {
    color: #0077b6;
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 20px;
}

.card-text {
    color: #1e293b;
    font-size: 18px;
    line-height: 1.8;
}

.footer {
    text-align: center;
    color: #cbd5e1;
    font-size: 18px;
    margin-top: 40px;
    padding: 25px;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    "<h1 class='main-title'>AIML Based Trading Guide App 📈</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='sub-title'>AI Powered Stock Market Analysis, Forecasting, Technical Indicators and Financial Intelligence Platform</p>",
    unsafe_allow_html=True
)

st.markdown("""
<div class="hero-box">

<div class="hero-title">
Smart Stock Market Intelligence System
</div>

<div class="hero-text">
Analyze historical market trends, visualize technical indicators,
predict future stock prices using AIML forecasting models,
and gain financial insights in one platform.
</div>

</div>
""", unsafe_allow_html=True)


st.image(
    "i1.jpg",
    use_container_width=True
)

st.markdown(
    "<h1 class='service-heading'>Our Services</h1>",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
    <div class="card">

    <div class="card-title">
    1️⃣ Stock Information
    </div>

    <div class="card-text">
    • Company Details<br>
    • Historical Stock Prices<br>
    • Financial Statements<br>
    • Technical Indicators<br>
    • Market Trend Analysis<br>
    • Stock Insights & Analytics
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">

    <div class="card-title">
    2️⃣ Stock Prediction
    </div>

    <div class="card-text">
    • AI/ML Forecasting Models<br>
    • ARIMA Predictions<br>
    • Time Series Forecasting<br>
    • Future Price Visualization<br>
    • Intelligent Forecast Charts<br>
    • Trend Based Predictions
    </div>

    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="card">

    <div class="card-title">
    3️⃣ CAPM Return
    </div>

    <div class="card-text">
    • CAPM Financial Model<br>
    • Expected Return Estimation<br>
    • Market Benchmark Comparison<br>
    • Portfolio Analysis<br>
    • Investment Insights<br>
    • Risk vs Reward Evaluation
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">

    <div class="card-title">
    4️⃣ CAPM Beta
    </div>

    <div class="card-text">
    • Beta Calculation<br>
    • Volatility Analysis<br>
    • Market Correlation<br>
    • Financial Risk Intelligence<br>
    • Stock Stability Insights<br>
    • Risk Assessment Metrics
    </div>

    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">

Built with Streamlit • AI/ML • Forecasting • Financial Analytics

<br><br>

Developed By Anurag Kumar Singh

</div>
""", unsafe_allow_html=True)