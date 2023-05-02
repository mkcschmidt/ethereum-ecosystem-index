import os
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import configparser

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

INDEX_FOLDER = config['INDEX']['index_folder']
DATA_DIR = f"{INDEX_FOLDER}/data"
INDEX_SNAPSHOTS_DIR = os.path.join(DATA_DIR, "index_snapshots")
PRICES_DIR = os.path.join(DATA_DIR, "prices")


def get_rebalancing_period_folders():
    folders = sorted([folder for folder in os.listdir(PRICES_DIR) if os.path.isdir(os.path.join(PRICES_DIR, folder))])
    return folders

def get_period_timestamps(period_folder):
    period_path = os.path.join(PRICES_DIR, period_folder)
    price_files = [file for file in os.listdir(period_path) if file.endswith(".csv")]

    if not price_files:
        print(f"Warning: No price files found in {period_folder}")
        return None

    first_price_file = os.path.join(period_path, price_files[0])
    price_data = pd.read_csv(first_price_file)

    start_ts = price_data.loc[0, "timestamp"] // 1000  # Convert to seconds
    end_ts = price_data.loc[len(price_data) - 1, "timestamp"] // 1000  # Convert to seconds

    return start_ts, end_ts

def validate_period_timestamps(period_folder, start_ts, end_ts):
    period_path = os.path.join(PRICES_DIR, period_folder)
    price_files = [file for file in os.listdir(period_path) if file.endswith(".csv")]

    for price_file in price_files:
        price_file_path = os.path.join(period_path, price_file)
        price_data = pd.read_csv(price_file_path)

        if price_data.empty:
            print(f"Warning: Price data is empty for {price_file}")
            continue

        file_start_ts = price_data.iloc[0]["timestamp"] // 1000  # Convert to seconds
        file_end_ts = price_data.iloc[-1]["timestamp"] // 1000  # Convert to seconds

        if file_start_ts != start_ts or file_end_ts != end_ts:
            print(f"Error: Timestamps in {price_file} do not match the period timestamps")
            return False

    return True


def get_snapshot_data(start_date):
    snapshot_file = os.path.join(INDEX_SNAPSHOTS_DIR, f"{start_date}.csv")
    if not os.path.exists(snapshot_file):
        print(f"Error: {snapshot_file} not found")
        return None

    snapshot = pd.read_csv(snapshot_file)
    return snapshot


def get_prices_data(start_date, token_id):
    token_prices_file = os.path.join(PRICES_DIR, start_date, f"{token_id}.csv")
    if not os.path.exists(token_prices_file):
        print(f"Error: {token_prices_file} not found")
        return None

    token_prices = pd.read_csv(token_prices_file)
    return token_prices


def compute_divisor(snapshot, start_date, target_price=None):
    token_count = len(snapshot)
    equal_weight = 1 / token_count

    total_weighted_price_0 = 0
    for index, token in snapshot.iterrows():
        token_id = token["Coingecko ID"]
        token_prices = get_prices_data(start_date, token_id)
        if token_prices is None or token_prices.empty:
            print(f"Warning: No price data for {token_id} in compute_divisor")
            continue
        first_entry_price = token_prices.iloc[0]["price"]
        total_weighted_price_0 += first_entry_price * equal_weight

    if target_price is None:
        divisor = total_weighted_price_0 / 100
    else:
        divisor = total_weighted_price_0 / target_price

    return divisor


def compute_daily_value(snapshot, ts, divisor, start_date):
    if divisor == 0:
        return None
    daily_value = 0
    token_count = len(snapshot)
    equal_weight = 1 / token_count
    for index, token in snapshot.iterrows():
        token_id = token["Coingecko ID"]
        token_prices = get_prices_data(start_date, token_id)
        if token_prices is None or token_prices.empty:
            print(f"Warning: No price data for {token_id} in compute_daily_value")
            continue
        price_data = token_prices[token_prices["timestamp"] == ts * 1000]  # Convert to milliseconds
        if not price_data.empty:
            token_price_t = price_data["price"].values[0]
            daily_value += token_price_t * equal_weight
        else:
            print(f"Warning: No price data for {token_id} at timestamp {ts}")
            continue
    index_value_t = daily_value / divisor
    return index_value_t


def compute_index_history(rebalancing_periods, initial_index_value):
    index_history = []
    target_price = initial_index_value

    def process_rebalancing_period(snapshot, start_ts, end_ts, divisor, is_last_period):
        daily_timestamps = list(range(start_ts, end_ts, 86400))

        for timestamp in daily_timestamps:
            index_value = compute_daily_value(snapshot, timestamp, divisor, start_date)
            if index_value is not None:
                index_history.append({"timestamp": timestamp, "index_value": index_value})

        if not is_last_period:
            target_price = compute_daily_value(snapshot, end_ts, divisor, start_date)
            return target_price

        index_value = compute_daily_value(snapshot, end_ts, divisor, start_date)
        index_history.append({"timestamp": end_ts, "index_value": index_value})
        return None

    total_periods = len(rebalancing_periods)

    for period_index, (start_date, start_ts, end_ts) in enumerate(rebalancing_periods):
        snapshot = get_snapshot_data(start_date)
        if snapshot is None:
            continue

        divisor = compute_divisor(snapshot, start_date, target_price)
        if divisor is None:
            continue

        is_last_period = (period_index == total_periods - 1)
        target_price = process_rebalancing_period(snapshot, start_ts, end_ts, divisor, is_last_period)

    index_history_df = pd.DataFrame(index_history)
    return index_history_df


def save_index_history(index_history_df, filename):
    index_history_df.to_csv(filename, index=False)



rebalancing_period_folders = get_rebalancing_period_folders()
rebalancing_periods = []

for idx, period_folder in enumerate(rebalancing_period_folders):
    timestamps = get_period_timestamps(period_folder)
    if timestamps is None:
        continue

    start_ts, end_ts = timestamps
    if not validate_period_timestamps(period_folder, start_ts, end_ts):
        continue

    rebalancing_periods.append((period_folder, start_ts, end_ts))

progress_bar = tqdm(rebalancing_periods, desc="Calculating index", bar_format="{l_bar}\033[1;32m{bar}\033[0m{r_bar}")
index_value = 100

index_history_df = compute_index_history(progress_bar, index_value)
save_index_history(index_history_df, f"{INDEX_FOLDER}/data/index_history.csv")