import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def fetch_historical_data(tickers, start='2022-01-01', end='2023-12-31'):
    df = pd.DataFrame()
    for ticker in tickers:
        data = yf.download(ticker, start=start, end=end)['Adj Close']
        df[ticker] = data
    return df

def show_correlation_heatmap(data):
    corr = data.pct_change().dropna().corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    st.pyplot(plt.gcf())
    plt.clf()

def show_cumulative_returns(data, weights):
    returns = data.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    cumulative = (1 + portfolio_returns).cumprod()
    cumulative.plot(figsize=(10, 4), title='Cumulative Portfolio Returns')
    st.pyplot(plt.gcf())
    plt.clf()
