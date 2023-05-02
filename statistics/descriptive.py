import os
import pandas as pd
import numpy as np

def read_index_history(folder):
    file_path = os.path.join(folder, 'data', 'index_history.csv')
    index_history = pd.read_csv(file_path)
    index_history['timestamp'] = pd.to_datetime(index_history['timestamp'], unit='s')
    index_history.set_index('timestamp', inplace=True)
    return index_history

def read_risk_free_rate_data(file_path):
    risk_free_rate = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
    risk_free_rate['yield'] = risk_free_rate['yield'] / 100  # Convert to decimal
    return risk_free_rate

def align_risk_free_rate(index_history, risk_free_rate):
    aligned_risk_free_rate = risk_free_rate.reindex(index_history.index, method='ffill')
    return aligned_risk_free_rate

def calculate_total_return(index_history):
    initial_value = index_history['index_value'].iloc[0]
    final_value = index_history['index_value'].iloc[-1]
    total_return = (final_value / initial_value) - 1
    return total_return

def calculate_summary_statistics(index_history):
    daily_returns = index_history['index_value'].pct_change().dropna()
    summary_statistics = {
        'mean': daily_returns.mean(),
        'median': daily_returns.median(),
        'std': daily_returns.std(),
    }
    return summary_statistics

def calculate_performance_measures(index_history, risk_free_rate):
    daily_returns = index_history['index_value'].pct_change().dropna()
    daily_risk_free_rate = risk_free_rate.loc[daily_returns.index, 'yield']
    
    # Adjust daily returns for the risk-free rate
    adjusted_daily_returns = daily_returns - daily_risk_free_rate

    sharpe_ratio = adjusted_daily_returns.mean() / adjusted_daily_returns.std()
    sortino_ratio = adjusted_daily_returns.mean() / adjusted_daily_returns[adjusted_daily_returns < 0].std()

    drawdowns = 1 - index_history['index_value'] / index_history['index_value'].cummax()
    max_drawdown = drawdowns.max()

    performance_measures = {
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
    }
    return performance_measures

index_folders = [
    'index-cw-10',
    'index-cw-20',
    'index-cw-30',
    'index-ew-10',
    'index-ew-20',
    'index-ew-30',
]

results = []

# Read risk-free rate data
risk_free_rate_file_path = 'risk-free-rate/risk_free_rate.csv'
risk_free_rate = read_risk_free_rate_data(risk_free_rate_file_path)

for folder in index_folders:
    index_history = read_index_history(folder)
    
    # Align risk-free rate data with index_history
    aligned_risk_free_rate = align_risk_free_rate(index_history, risk_free_rate)
    
    summary_statistics = calculate_summary_statistics(index_history)
    performance_measures = calculate_performance_measures(index_history, aligned_risk_free_rate)
    total_return = calculate_total_return(index_history)

    result = {
        'index': folder,
        'total_return': total_return,
        **summary_statistics,
        **performance_measures,
    }
    results.append(result)

results_df = pd.DataFrame(results)
results_df.to_csv('statistics/descriptive_statistics.csv', index=False)
