import os
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# List of index folders
index_folders = ['index-cw-10', 'index-cw-20', 'index-cw-30', 'index-ew-10', 'index-ew-20', 'index-ew-30']

# Function to load index history
def load_index_history(folder):
    file_path = os.path.join(folder, 'data', 'index_history.csv')
    index_history = pd.read_csv(file_path)
    index_history["timestamp"] = pd.to_datetime(index_history["timestamp"], unit="s")
    index_history.set_index("timestamp", inplace=True)
    return index_history['index_value']

# Load index histories
index_histories = {folder: load_index_history(folder) for folder in index_folders}

# Combine index histories into a single DataFrame
index_data = pd.concat(index_histories, axis=1)
index_data.columns = index_folders

# Calculate Pearson correlation and p-values
pearson_corr = index_data.corr(method='pearson')
p_values = index_data.corr(method=lambda x, y: pearsonr(x, y)[1])  # Calculate p-values using scipy.stats.pearsonr()

print("Pearson Correlation:\n", pearson_corr)
print("\nP-values:\n", p_values)

# Save Pearson correlation and p-values to CSV files
pearson_corr.to_csv('statistics/pearson_correlations.csv')
p_values.to_csv('statistics/p_values.csv')

# Calculate average pairwise correlation
average_pairwise_corr = pearson_corr.mean().mean()
print("\nAverage Pairwise Correlation:", average_pairwise_corr)

# Save average pairwise correlation to a CSV file
pd.DataFrame([average_pairwise_corr], index=['Average Pairwise Correlation'], columns=['Value']).to_csv('statistics/average_pairwise_correlation.csv')

print("\nCorrelation matrix, p-values, and average pairwise correlation saved to CSV files.")
