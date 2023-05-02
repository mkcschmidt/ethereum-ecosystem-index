import os
import csv
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
import shutil
import configparser

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

API_KEY = config['COINGECKO']['api_key']
API_URL = 'https://pro-api.coingecko.com/api/v3'
INDEX_FOLDER = config['INDEX']['index_folder']
INDEX_SNAPSHOT_DIR = os.path.join(INDEX_FOLDER, 'data/index_snapshots')
PRICES_DIR = os.path.join(INDEX_FOLDER, 'data/prices')

# Delete the prices folder if it exists
if os.path.exists(PRICES_DIR):
    shutil.rmtree(PRICES_DIR)

# Create the prices folder
os.makedirs(PRICES_DIR, exist_ok=True)

# Function to print text in red
def print_error(text):
    print(f"\033[1;31m{text}\033[0m\n")

# Function to fetch historical data for a token
def fetch_token_data(token_id, from_timestamp, to_timestamp):
    url = f'{API_URL}/coins/{token_id}/market_chart/range'
    params = {
        'vs_currency': 'usd',
        'from': from_timestamp,
        'to': to_timestamp,
        'interval': 'daily',
        'x_cg_pro_api_key': API_KEY
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {token_id}: {response.status_code}")
        return None

# Hardcoded timestamps for the rebalancing periods
rebalancing_periods = [
    ('2021-01-03', 1609632000, 1617494400),
    ('2021-04-04', 1617494400, 1625356800),
    ('2021-07-04', 1625356800, 1633219200),
    ('2021-10-03', 1633219200, 1641081600),
    ('2022-01-02', 1641081600, 1648944000),
    ('2022-04-03', 1648944000, 1656806400),
    ('2022-07-03', 1656806400, 1664668800),
    ('2022-10-02', 1664668800, 1672531200),
    ('2023-01-01', 1672531200, 1680393600)
]

progress_bar = tqdm(rebalancing_periods, desc="Fetching prices", bar_format="{l_bar}\033[1;32m{bar}\033[0m{r_bar}")

for period_start, from_timestamp, to_timestamp in progress_bar:
    snapshot_file = f'{period_start}.csv'
    
    snapshot_folder = os.path.join(PRICES_DIR, snapshot_file[:-4])
    os.makedirs(snapshot_folder, exist_ok=True)

    with open(os.path.join(INDEX_SNAPSHOT_DIR, snapshot_file), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            token_id = row['Coingecko ID']

            # Check if the token's price data file already exists in the snapshot_folder
            token_file = os.path.join(snapshot_folder, f"{token_id}.csv")
            if os.path.exists(token_file):
                continue

            token_data = fetch_token_data(token_id, from_timestamp, to_timestamp)

            if token_data and token_data['prices']:
                with open(token_file, 'w', newline='') as token_csv:
                    writer = csv.writer(token_csv)
                    writer.writerow(['timestamp', 'price', 'market_cap'])

                    for data_point in token_data['prices']:
                        timestamp, price = data_point
                        market_cap = [x[1] for x in token_data['market_caps'] if x[0] == timestamp][0]
                        writer.writerow([timestamp, price, market_cap])
            else:
                print_error(f"\nWarning: No price data for {token_id}")