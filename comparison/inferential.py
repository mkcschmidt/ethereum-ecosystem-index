import os
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def read_asset_history(file_path, index_column, date_format=None, unit=None):
    asset_history = pd.read_csv(file_path)
    asset_history[index_column] = pd.to_datetime(asset_history[index_column], format=date_format, unit=unit)
    asset_history.set_index(index_column, inplace=True)
    return asset_history

# Read benchmark data
index_cw_30_history = read_asset_history('index-cw-30/data/index_history.csv', 'timestamp', unit='s')
bitcoin_history = read_asset_history('comparison/data/bitcoin_prices.csv', 'timestamp', unit='s')
ethereum_history = read_asset_history('comparison/data/ethereum_prices.csv', 'timestamp', unit='s')
dpi_history = read_asset_history('comparison/data/dpi_prices.csv', 'timestamp', unit='s')
crix_history = read_asset_history('comparison/data/crix_prices.csv', 'Effective date', date_format='%d.%m.%y')

# Rename columns
index_cw_30_history.columns = ['index-cw-30']
bitcoin_history.columns = ['bitcoin']
ethereum_history.columns = ['ethereum']
dpi_history.columns = ['dpi']
crix_history.columns = ['crix']

# Concatenate index and benchmark data into a single dataframe
combined_history = pd.concat([index_cw_30_history, bitcoin_history, ethereum_history, dpi_history, crix_history], axis=1).dropna()

# Calculate Pearson correlation of the index with all other assets and their p-values
index_corr_and_p_values = {col: pearsonr(combined_history['index-cw-30'], combined_history[col]) for col in combined_history.columns if col != 'index-cw-30'}

# Separate correlation and p-values into two dictionaries
index_corr = {col: corr_and_p_value[0] for col, corr_and_p_value in index_corr_and_p_values.items()}
index_p_values = {col: corr_and_p_value[1] for col, corr_and_p_value in index_corr_and_p_values.items()}

print("Pearson Correlation of index-cw-30 with other assets:\n", index_corr)
print("\nP-values of index-cw-30 with other assets:\n", index_p_values)

# Save Pearson correlation to a CSV file
pd.Series(index_corr).to_csv('comparison/pearson_correlations.csv', header=['Correlation'])
pd.Series(index_p_values).to_csv('comparison/p_values.csv', header=['P-value'])

print("\nCorrelation and p-values of index-cw-30 with other assets saved to CSV files.")
