import csv
import os
import configparser

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

# Define start and end timestamps
start_timestamp = 1609632000
end_timestamp = 1680393600

# Define timestamp interval
interval = 24 * 60 * 60  # 24 hours in seconds

# Generate timestamps
index_timestamps = list(range(start_timestamp, end_timestamp+1, interval))

# Read in index_history.csv
with open(os.path.join(config['INDEX']['index_folder'], 'data', 'index_history.csv'), 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header row
    history_timestamps = [int(row[0]) for row in reader]
    history_values = [float(row[1]) for row in reader]

# Check if timestamps and values are the same, in the same order, and have the same length
if len(index_timestamps) == len(history_timestamps) and index_timestamps == history_timestamps:
    print("\033[92m \u2713 The two CSV files have the same timestamps in the same order and length. \033[0m")
else:
    print("\033[91m \u2717 The two CSV files do not have the same timestamps in the same order and length. \033[0m")

# Check if all values are the same
if all(value == 100.0 for value in history_values):
    print("\033[92m \u2713 All values in the CSV file are the same. \033[0m")
else:
    print("\033[91m \u2717 Some values in the CSV file are different. \033[0m")

# Check if timestamps are in 24-hour intervals from the start timestamp
if all((t - start_timestamp) % interval == 0 for t in history_timestamps):
    print("\033[92m \u2713 The timestamps in the CSV file are in 24-hour intervals from the start timestamp. \033[0m")
else:
    print("\033[91m \u2717 The timestamps in the CSV file are not in 24-hour intervals from the start timestamp. \033[0m")
