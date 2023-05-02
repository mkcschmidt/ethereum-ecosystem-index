import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set font family and size for the plot
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 12

INDEX_FOLDER = "index-cw-30"
COMPARISON_FOLDER = "comparison"
COMPARISON_FILES = [
    "bitcoin_prices.csv",
    "dpi_prices.csv",
    "ethereum_prices.csv",
    "crix_prices.csv",
]

def load_index_data(folder):
    filepath = os.path.join(folder, "data", "index_history.csv")
    data = pd.read_csv(filepath, index_col="timestamp", parse_dates=True)
    data.index = pd.to_datetime(data.index, unit="s")
    data.columns = [folder]
    return data

def load_comparison_data(folder, filename):
    filepath = os.path.join(folder, "data", filename)
    
    if filename == "crix_prices.csv":
        data = pd.read_csv(filepath, index_col="Effective date", parse_dates=True, dayfirst=True, sep=",", decimal=",")
        data.columns = ["Royalton CRIX Crypto Index"]
    else:
        data = pd.read_csv(filepath, index_col="timestamp", parse_dates=True)
        data.index = pd.to_datetime(data.index, unit="s")
        data.columns = [filename.split("_")[0]]
    
    return data


def normalize(data):
    data = data.astype(float)  # Ensure the data is numeric
    first_non_missing_value = data.dropna().iloc[0]
    return data / first_non_missing_value

# Load index data
index_data = load_index_data(INDEX_FOLDER)

# Load comparison data
comparison_data = [load_comparison_data(COMPARISON_FOLDER, filename) for filename in COMPARISON_FILES]

# Merge all data into a single DataFrame
all_data = pd.concat([index_data] + comparison_data, axis=1)

# Normalize data
normalized_data = all_data.apply(normalize, axis=0)

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)

# Plot data
colors = ['blue', 'orange', 'green', 'purple', 'red']
for i, column in enumerate(normalized_data.columns):
    data_to_plot = normalized_data[[column]].dropna()
    ax.plot(data_to_plot.index, data_to_plot[column], label=column, color=colors[i % len(colors)])

    print(f"{column}: {colors[i]}")

ax.set_xlabel("Date")
ax.set_ylabel("Normalised Prices")

# Set xticks every other week
xticks = pd.date_range(start=normalized_data.index.min(), end=normalized_data.index.max(), freq='18W')
ax.set_xticks(xticks)
ax.set_xticklabels([d.date().strftime('%m/%d/%Y') if isinstance(d, pd.Timestamp) else '' for d in xticks])

output_filename = os.path.join("charts", "comparison_normalized.png")
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
