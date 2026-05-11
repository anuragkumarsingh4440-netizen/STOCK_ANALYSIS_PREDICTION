import plotly.graph_objects as go
import dateutil
import pandas_ta as pta
import yfinance as yf
import datetime as dt


def plotly_table(dataframe):

    headerColor = '#0078ff'
    rowEvenColor = '#f8f9fd'
    rowOddColor = '#edf4ff'

    fig = go.Figure(data=[go.Table(

        header=dict(

            values=[
                "<b>" + str(i)[:10] + "</b>"
                for i in dataframe.columns
            ],

            line_color='#0078ff',

            fill_color='#0078ff',

            align='center',

            font=dict(
                color='white',
                size=15
            ),

            height=38
        ),

        cells=dict(

            values=[
                ["<b>" + str(i) + "</b>" for i in dataframe.index]
            ] + [
                dataframe[i] for i in dataframe.columns
            ],

            fill_color=[
                [rowOddColor, rowEvenColor]
            ],

            align='left',

            line_color='white',

            font=dict(
                color='black',
                size=14
            ),

            height=32
        )

    )])

    fig.update_layout(

        height=400,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        paper_bgcolor='white'

    )

    return fig


def filter_data(dataframe, num_period):

    if num_period == '1mo':

        date = dataframe.index[-1] + \
            dateutil.relativedelta.relativedelta(months=-1)

    elif num_period == '5d':

        date = dataframe.index[-1] + \
            dateutil.relativedelta.relativedelta(days=-5)

    elif num_period == '6mo':

        date = dataframe.index[-1] + \
            dateutil.relativedelta.relativedelta(months=-6)

    elif num_period == '1y':

        date = dataframe.index[-1] + \
            dateutil.relativedelta.relativedelta(years=-1)

    elif num_period == '5y':

        date = dataframe.index[-1] + \
            dateutil.relativedelta.relativedelta(years=-5)

    elif num_period == 'ytd':

        date = dt.datetime(
            dataframe.index[-1].year,
            1,
            1
        ).strftime('%Y-%m-%d')

    else:

        date = dataframe.index[0]

    return dataframe.reset_index()[
        dataframe.reset_index()['Date'] > date
    ]


def close_chart(dataframe, num_period=False):

    if num_period:

        dataframe = filter_data(
            dataframe,
            num_period
        )

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['Open'],

        mode='lines',

        name='Open',

        line=dict(
            width=2,
            color='#4dabf7'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['Close'],

        mode='lines',

        name='Close',

        line=dict(
            width=2,
            color='#111111'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['High'],

        mode='lines',

        name='High',

        line=dict(
            width=2,
            color='#0077ff'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['Low'],

        mode='lines',

        name='Low',

        line=dict(
            width=2,
            color='#ff4d4f'
        )

    ))

    fig.update_xaxes(
        rangeslider_visible=True
    )

    fig.update_layout(

        height=520,

        margin=dict(
            l=0,
            r=10,
            t=20,
            b=0
        ),

        plot_bgcolor='white',

        paper_bgcolor='white',

        hovermode='x unified',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )

    )

    return fig


def candlestick(dataframe, num_period):

    dataframe = filter_data(
        dataframe,
        num_period
    )

    fig = go.Figure()

    fig.add_trace(go.Candlestick(

        x=dataframe['Date'],

        open=dataframe['Open'],

        high=dataframe['High'],

        low=dataframe['Low'],

        close=dataframe['Close'],

        increasing_line_color='#00c853',

        decreasing_line_color='#ff3d00'

    ))

    fig.update_layout(

        showlegend=False,

        height=520,

        margin=dict(
            l=0,
            r=10,
            t=20,
            b=0
        ),

        plot_bgcolor='white',

        paper_bgcolor='white',

        xaxis_rangeslider_visible=True

    )

    return fig


def RSI(dataframe, num_period):

    dataframe['RSI'] = pta.rsi(
        dataframe['Close']
    )

    dataframe = filter_data(
        dataframe,
        num_period
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['RSI'],

        name='RSI',

        mode='lines',

        line=dict(
            width=2,
            color='#ff9800'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=[70] * len(dataframe),

        name='Overbought',

        mode='lines',

        line=dict(
            width=2,
            color='red',
            dash='dash'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=[30] * len(dataframe),

        fill='tonexty',

        name='Oversold',

        mode='lines',

        line=dict(
            width=2,
            color='#00c853',
            dash='dash'
        )

    ))

    fig.update_layout(

        yaxis_range=[0, 100],

        height=240,

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),

        plot_bgcolor='white',

        paper_bgcolor='white',

        hovermode='x unified',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )

    )

    return fig


def Moving_average(dataframe, num_period):

    dataframe['SMA_50'] = pta.sma(
        dataframe['Close'],
        50
    )

    dataframe = filter_data(
        dataframe,
        num_period
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['Close'],

        mode='lines',

        name='Close Price',

        line=dict(
            width=2,
            color='black'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['SMA_50'],

        mode='lines',

        name='50 Days SMA',

        line=dict(
            width=2,
            color='#9c27b0'
        )

    ))

    fig.update_xaxes(
        rangeslider_visible=True
    )

    fig.update_layout(

        height=520,

        margin=dict(
            l=0,
            r=10,
            t=20,
            b=0
        ),

        plot_bgcolor='white',

        paper_bgcolor='white',

        hovermode='x unified',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )

    )

    return fig


def MACD(dataframe, num_period):

    macd_df = pta.macd(
        dataframe['Close']
    )

    dataframe['MACD'] = macd_df.iloc[:, 0]

    dataframe['MACD Signal'] = macd_df.iloc[:, 1]

    dataframe['MACD Hist'] = macd_df.iloc[:, 2]

    dataframe = filter_data(
        dataframe,
        num_period
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['MACD'],

        name='MACD',

        mode='lines',

        line=dict(
            width=2,
            color='#ff9800'
        )

    ))

    fig.add_trace(go.Scatter(

        x=dataframe['Date'],

        y=dataframe['MACD Signal'],

        name='Signal',

        mode='lines',

        line=dict(
            width=2,
            color='red',
            dash='dash'
        )

    ))

    colors = [

        'red'
        if value < 0
        else 'green'

        for value in dataframe['MACD Hist']

    ]

    fig.add_trace(go.Bar(

        x=dataframe['Date'],

        y=dataframe['MACD Hist'],

        marker_color=colors,

        name='Histogram'

    ))

    fig.update_layout(

        height=250,

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),

        plot_bgcolor='white',

        paper_bgcolor='white',

        hovermode='x unified',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )

    )

    return fig


def Moving_average_forecast(forecast):

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=forecast.index[:-30],

        y=forecast['Close'].iloc[:-30],

        mode='lines',

        name='Historical Price',

        line=dict(
            width=2,
            color='black'
        )

    ))

    fig.add_trace(go.Scatter(

        x=forecast.index[-31:],

        y=forecast['Close'].iloc[-31:],

        mode='lines',

        name='Forecast Price',

        line=dict(
            width=3,
            color='red'
        )

    ))

    fig.update_xaxes(
        rangeslider_visible=True
    )

    fig.update_layout(

        height=520,

        margin=dict(
            l=0,
            r=10,
            t=20,
            b=0
        ),

        plot_bgcolor='white',

        paper_bgcolor='white',

        hovermode='x unified',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )

    )

    return fig