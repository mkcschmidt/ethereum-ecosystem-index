import os
import pandas as pd
import numpy as np

def read_asset_history(file_path, index_column, date_format=None, unit=None):
    asset_history = pd.read_csv(file_path)
    asset_history[index_column] = pd.to_datetime(asset_history[index_column], format=date_format, unit=unit)
    asset_history.set_index(index_column, inplace=True)
    return asset_history

def align_risk_free_rate(asset_history, risk_free_rate):
    aligned_risk_free_rate = risk_free_rate.reindex(asset_history.index, method='ffill')
    return aligned_risk_free_rate

def calculate_summary_statistics(asset_history, aligned_risk_free_rate):
    daily_returns = asset_history.pct_change().dropna()
    adjusted_daily_returns = daily_returns.subtract(aligned_risk_free_rate['yield'], axis=0)

    summary_statistics = {
        'total_return': (asset_history.iloc[-1] / asset_history.iloc[0] - 1).iloc[0],
        'mean': daily_returns.mean().iloc[0],
        'median': daily_returns.median().iloc[0],
        'std': daily_returns.std().iloc[0],
        'sharpe_ratio': adjusted_daily_returns.mean().iloc[0] / adjusted_daily_returns.std().iloc[0],
        'sortino_ratio': adjusted_daily_returns.mean().iloc[0] / adjusted_daily_returns[adjusted_daily_returns < 0].std().iloc[0],
        'max_drawdown': (1 - asset_history / asset_history.cummax()).max().iloc[0],
    }
    return summary_statistics

# Read risk-free rate data
risk_free_rate_file_path = 'risk-free-rate/risk_free_rate.csv'
risk_free_rate = pd.read_csv(risk_free_rate_file_path, parse_dates=['Date'], index_col='Date')
risk_free_rate['yield'] = risk_free_rate['yield'] / 100  # Convert to decimal

# Read asset data
index_history = read_asset_history('index-cw-30/data/index_history.csv', 'timestamp', unit='s')
bitcoin_history = read_asset_history('comparison/data/bitcoin_prices.csv', 'timestamp', unit='s')
ethereum_history = read_asset_history('comparison/data/ethereum_prices.csv', 'timestamp', unit='s')
dpi_history = read_asset_history('comparison/data/dpi_prices.csv', 'timestamp', unit='s')
crix_history = read_asset_history('comparison/data/crix_prices.csv', 'Effective date', date_format='%d.%m.%y')

def normalize_prices(asset_history):
    return asset_history / asset_history.iloc[0]

# Calculate summary statistics for each asset
results = []
assets = {'index-cw-30': index_history, 'bitcoin': bitcoin_history, 'ethereum': ethereum_history, 'dpi': dpi_history, 'crix': crix_history}

for asset, asset_history in assets.items():
    asset_history = asset_history.dropna()
    asset_history = normalize_prices(asset_history)
    aligned_risk_free_rate = align_risk_free_rate(asset_history, risk_free_rate)
    summary_statistics = calculate_summary_statistics(asset_history, aligned_risk_free_rate)
    result = {'index': asset, **summary_statistics}
    results.append(result)

# Save the results in a dataframe and export to a CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('comparison/descriptive_statistics.csv', index=False)
