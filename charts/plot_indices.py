import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set font family and size for the plot
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 12

INDEX_FOLDERS = [
    "index-cw-10",
    "index-cw-20",
    "index-cw-30",
    "index-ew-10",
    "index-ew-20",
    "index-ew-30",
]

def load_index_data(folder):
    filepath = os.path.join(folder, "data", "index_history.csv")
    data = pd.read_csv(filepath, index_col="timestamp", parse_dates=True)
    data.index = pd.to_datetime(data.index, unit="s")
    data.columns = [folder]
    return data

# Load index data
index_data = [load_index_data(folder) for folder in INDEX_FOLDERS]

# Merge all index data into a single DataFrame
all_indices_data = pd.concat(index_data, axis=1)

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)

# Plot index data
colors = ['green', 'orange', 'blue', 'red', 'purple', 'brown']
for i, column in enumerate(all_indices_data.columns):
    if 'cw' in column:
        ax.plot(all_indices_data.index, all_indices_data[column], label=column, color=colors[i%3])
    else:
        ax.plot(all_indices_data.index, all_indices_data[column], label=column, color=colors[i%3+3])

    print(f"{column}: {colors[i]}")

ax.set_xlabel("Date")
ax.set_ylabel("Index Value")

# Set xticks every other week
xticks = pd.date_range(start=all_indices_data.index.min(), end=all_indices_data.index.max(), freq='18W')
ax.set_xticks(xticks)
ax.set_xticklabels([d.date().strftime('%m/%d/%Y') if isinstance(d, pd.Timestamp) else '' for d in xticks])

output_filename = os.path.join("charts", "indices.png")
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
