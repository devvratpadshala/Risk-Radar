import numpy as np
import pandas as pd

def calculate_risk_metrics(price_data, weights):
    returns = price_data.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    volatility = np.std(portfolio_returns) * np.sqrt(252)
    var_95 = np.percentile(portfolio_returns, 5)
    sharpe_ratio = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252)

    beta = None
    if 'SPY' in price_data.columns:
        market_returns = price_data['SPY'].pct_change().dropna()
        beta = np.cov(portfolio_returns, market_returns)[0][1] / np.var(market_returns)

    return pd.DataFrame({
        "Metric": ["Annualized Volatility", "95% VaR", "Sharpe Ratio", "Beta (vs SPY)"],
        "Value": [volatility, var_95, sharpe_ratio, beta]
    })
