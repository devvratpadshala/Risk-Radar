import pandas as pd

def run_stress_test(price_data, weights, scenario):
    returns = price_data.pct_change().dropna()
    base_returns = (returns * weights).sum(axis=1)

    if scenario == "Market Crash -10%":
        shocked_returns = base_returns - 0.10
    elif scenario == "Interest Rate Hike +2%":
        shocked_returns = base_returns - 0.02
    else:
        shocked_returns = base_returns

    summary = {
        "Original Avg Return": base_returns.mean(),
        "Shocked Avg Return": shocked_returns.mean(),
        "Impact": shocked_returns.mean() - base_returns.mean()
    }

    return pd.DataFrame.from_dict(summary, orient='index', columns=['Value'])
