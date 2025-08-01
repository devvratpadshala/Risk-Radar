import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# Streamlit UI
st.title("📊 Portfolio Analyzer")

uploaded_file = st.file_uploader("Upload your portfolio CSV (ticker, weight)", type=["csv"])
if uploaded_file:
    try:
        portfolio = pd.read_csv(uploaded_file)

        if 'ticker' not in portfolio.columns or 'weight' not in portfolio.columns:
            st.error("CSV must contain 'ticker' and 'weight' columns.")
            st.stop()

        # Clean and validate
        portfolio['ticker'] = portfolio['ticker'].str.upper()
        portfolio['weight'] = pd.to_numeric(portfolio['weight'], errors='coerce')
        portfolio.dropna(inplace=True)

        if abs(portfolio['weight'].sum() - 1.0) > 0.01:
            st.warning("Weights should sum to 1.0 for proper analysis. Normalizing them.")
            portfolio['weight'] /= portfolio['weight'].sum()

        tickers = portfolio['ticker'].tolist()
        weights = portfolio['weight'].tolist()

        start_date = st.date_input("Start Date", datetime(2020, 1, 1))
        end_date = st.date_input("End Date", datetime.today())

        if st.button("Analyze Portfolio"):
            st.info("Fetching market data...")
            data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker', auto_adjust=False, progress=False)

            # Handle multi or single index format
            if isinstance(data.columns, pd.MultiIndex):
                try:
                    price_data = pd.DataFrame({ticker: data[ticker]['Adj Close'] for ticker in tickers})
                except KeyError as e:
                    st.error(f"Adjusted Close data not available for: {e}")
                    st.stop()
            else:
                if 'Adj Close' in data.columns:
                    price_data = data[['Adj Close']]
                    price_data.columns = tickers[:1]  # single column
                else:
                    st.error("Adjusted Close data not available.")
                    st.stop()

            price_data.dropna(inplace=True)

            # Normalize & calculate portfolio value
            norm = price_data / price_data.iloc[0]
            weighted = norm.multiply(weights, axis=1)
            portfolio_value = weighted.sum(axis=1)

            # Plotting
            st.subheader("📈 Portfolio Value Over Time")
            fig, ax = plt.subplots()
            portfolio_value.plot(ax=ax, title="Portfolio Performance")
            ax.set_ylabel("Portfolio Value (Normalized)")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
