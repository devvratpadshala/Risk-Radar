import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("📊 Fully Dynamic Indian Sector & Portfolio Analyzer with Recommendations")

st.markdown("""
Upload your **portfolio CSV** file with two columns:  
- **Ticker** (Yahoo Finance format e.g. RELIANCE.NS)  
- **Weight** (portfolio weight, sum need not be exactly 1)  

The app will:  
1. Dynamically analyze Indian sector performance via sector ETFs  
2. Dynamically fetch sector info for your portfolio stocks  
3. Analyze your portfolio returns and sector exposure  
4. Recommend replacements for underperforming stocks from top sectors
""")

uploaded_file = st.file_uploader("Upload your Portfolio CSV (Ticker,Weight)", type=["csv"])

# Minimal known NSE Sector ETFs (proxy for sectors)
# You can expand this list if new ETFs launch
INDIAN_SECTOR_ETFS = {
    "Banking": "NSEBANK.NS",
    "IT": "NSEIT.NS",
    "Pharma": "NSEPHARMA.NS",
    "Energy": "NSEOIL.NS",
    "FMCG": "NSEFMCG.NS",
    "Infrastructure": "NSEINFRA.NS",
    "Auto": "NSEAUTO.NS",
    "Metal": "NSEMETAL.NS",
    "Finance": "NSEFIN.NS",
}


def get_sector_etf_performance(etfs, start, end):
    perf = {}
    data = yf.download(list(etfs.values()), start=start, end=end, auto_adjust=True, progress=False)['Close']
    for sector, ticker in etfs.items():
        if ticker not in data.columns:
            perf[sector] = np.nan
            continue
        prices = data[ticker].dropna()
        if len(prices) < 2:
            perf[sector] = np.nan
            continue
        returns = prices.pct_change().dropna()
        cum_ret = (1 + returns).cumprod()
        years = (prices.index[-1] - prices.index[0]).days / 365.25
        cagr = cum_ret[-1] ** (1 / years) - 1
        perf[sector] = cagr
    return perf


def get_sector_of_stock(ticker):
    try:
        info = yf.Ticker(ticker).info
        sector = info.get('sector', 'Unknown')
        if sector is None or sector.strip() == "":
            return 'Unknown'
        return sector
    except Exception:
        return 'Unknown'


def portfolio_sector_weights(tickers, weights):
    sector_wts = defaultdict(float)
    for t, w in zip(tickers, weights):
        sector = get_sector_of_stock(t)
        sector_wts[sector] += w
    return dict(sector_wts)


def download_portfolio_prices(tickers, start, end):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        group_by='ticker',
        auto_adjust=True,
        threads=True,
        progress=False
    )
    return data


def calculate_cagr(adj_close):
    daily_returns = adj_close.pct_change().dropna()
    cumulative_returns = (1 + daily_returns).cumprod()
    total_years = (adj_close.index[-1] - adj_close.index[0]).days / 365.25
    cagr = cumulative_returns[-1] ** (1 / total_years) - 1
    return cagr


def recommend_replacements(underperformers, sector_perf, portfolio_sector_wts, portfolio_tickers, etf_map):
    recommendations = {}
    # Sort sectors by CAGR descending, ignoring NaNs
    valid_sectors = {k: v for k, v in sector_perf.items() if not np.isnan(v)}
    sorted_sectors = sorted(valid_sectors.items(), key=lambda x: x[1], reverse=True)
    top_sectors = [s for s, _ in sorted_sectors[:3]]  # top 3 sectors

    for under_ticker, _ in underperformers:
        # Get sector of underperformer stock
        under_sector = get_sector_of_stock(under_ticker)

        # Find first top performing sector different from underperformer's sector
        replacement_sector = None
        for sector in top_sectors:
            # Recommend sector not already heavily represented in portfolio (<30% weight)
            if sector != under_sector and portfolio_sector_wts.get(sector, 0) < 0.3:
                replacement_sector = sector
                break

        if replacement_sector is None and top_sectors:
            replacement_sector = top_sectors[0]

        # Recommend corresponding sector ETF ticker if not already in portfolio (fallback)
        rec_ticker = etf_map.get(replacement_sector, None)
        # If sector ETF in portfolio, recommend it anyway (this can be customized)

        recommendations[under_ticker] = (replacement_sector, rec_ticker)
    return recommendations


if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if not set(['Ticker', 'Weight']).issubset(df.columns):
            st.error("CSV must contain 'Ticker' and 'Weight' columns")
            st.stop()

        df = df.dropna(subset=['Ticker', 'Weight'])
        tickers = df['Ticker'].astype(str).str.upper().tolist()
        weights = df['Weight'].astype(float).tolist()
        weights = np.array(weights)
        weights /= weights.sum()  # Normalize weights

        st.sidebar.header("Portfolio Summary")
        st.sidebar.write(f"Tickers: {tickers}")
        st.sidebar.write(f"Weights: {weights}")

        # Define date range (last 5 years)
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365 * 5)

        st.header("🏛️ Indian Sector ETF Performance (Last 5 Years CAGR)")
        with st.spinner("Downloading sector ETF data..."):
            sector_perf = get_sector_etf_performance(INDIAN_SECTOR_ETFS, start_date, end_date)
        sector_perf_df = pd.DataFrame.from_dict(sector_perf, orient='index', columns=['CAGR']).dropna().sort_values(
            'CAGR', ascending=False)
        st.table(sector_perf_df.style.format({'CAGR': "{:.2%}"}))

        if sector_perf_df.empty:
            st.warning("Failed to fetch Indian sector ETF performance. Try later or check internet connection.")


        # Fetch sector info for portfolio stocks (cache this lookup to improve speed)
        @st.cache_data(show_spinner=False)
        def cached_get_sector(ticker):
            return get_sector_of_stock(ticker)


        st.header("Fetching Sector Info for Portfolio Stocks (may take some seconds)...")
        portfolio_sector_map = {}
        for tkr in tickers:
            portfolio_sector_map[tkr] = cached_get_sector(tkr)

        # Calculate portfolio sector weights
        port_sector_wts_dict = defaultdict(float)
        for tkr, w in zip(tickers, weights):
            sec = portfolio_sector_map.get(tkr, 'Unknown')
            port_sector_wts_dict[sec] += w
        port_sector_wts_df = pd.DataFrame.from_dict(port_sector_wts_dict, orient='index',
                                                    columns=['Weight']).sort_values('Weight', ascending=False)
        st.subheader("Portfolio Sector Weight Distribution")
        st.bar_chart(port_sector_wts_df)

        # Download portfolio prices & calculate portfolio performance
        st.header("📊 Portfolio Performance Analysis")

        data = download_portfolio_prices(tickers, start_date, end_date)

        adj_close = pd.DataFrame()
        for t in tickers:
            try:
                if t in data.columns.levels[0]:
                    adj_close[t] = data[t]['Close']
                else:
                    st.warning(f"No data found for {t}, skipping.")
            except Exception as e:
                st.warning(f"Error processing {t}: {e}")
        adj_close.dropna(how='any', inplace=True)

        if adj_close.empty or len(adj_close) < 2:
            st.error("Not enough data available after cleaning. Check your tickers or date range.")
            st.stop()

        # Filter weights to match available tickers
        final_tickers = adj_close.columns.tolist()
        weights_matched = []
        for tkr in final_tickers:
            idx = tickers.index(tkr)
            weights_matched.append(weights[idx])
        weights_matched = np.array(weights_matched)
        weights_matched /= weights_matched.sum()

        st.write(f"Analyzing tickers: {final_tickers}")
        st.write(f"Adjusted weights: {weights_matched}")

        daily_returns = adj_close.pct_change().dropna()
        portfolio_daily_returns = (daily_returns * weights_matched).sum(axis=1)
        cumulative_returns = (1 + portfolio_daily_returns).cumprod()
        total_years = (adj_close.index[-1] - adj_close.index[0]).days / 365.25
        port_cagr = cumulative_returns[-1] ** (1 / total_years) - 1
        port_volatility = portfolio_daily_returns.std() * np.sqrt(252)
        port_sharpe = port_cagr / port_volatility if port_volatility > 0 else np.nan

        st.subheader("Portfolio Overall Metrics")
        st.write(f"**CAGR:** {port_cagr:.2%}")
        st.write(f"**Volatility:** {port_volatility:.2%}")
        st.write(f"**Sharpe Ratio:** {port_sharpe:.2f}")

        st.subheader("Portfolio Growth Over Time")
        st.line_chart(cumulative_returns)

        # Identify underperforming stocks (<30% portfolio CAGR)
        st.header("🔍 Underperforming Stocks")

        underperformers = []
        for t in final_tickers:
            stock_cagr = calculate_cagr(adj_close[t])
            if stock_cagr < 0.3 * port_cagr:
                underperformers.append((t, stock_cagr))

        if underperformers:
            for tkr, cagr_val in underperformers:
                st.warning(f"🔻 {tkr}: CAGR {cagr_val:.2%} (<30% of portfolio CAGR {port_cagr:.2%})")
        else:
            st.success("🎉 No underperforming stocks detected!")

        # Recommend replacements for underperformers
        if underperformers:
            st.header("💡 Stock Replacement Recommendations")

            recommendations = recommend_replacements(
                underperformers,
                sector_perf,
                port_sector_wts_dict,
                final_tickers,
                INDIAN_SECTOR_ETFS
            )

            for under_tkr, (rec_sector, rec_ticker) in recommendations.items():
                if rec_ticker is not None:
                    st.write(f"Replace **{under_tkr}** with sector ETF **{rec_ticker}** from sector **{rec_sector}**")
                else:
                    st.write(f"No suitable recommendation available to replace **{under_tkr}**")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

else:
    st.info("Please upload your portfolio CSV file to start analysis.")
