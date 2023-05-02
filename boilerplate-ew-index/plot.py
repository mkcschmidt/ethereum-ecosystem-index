import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from configparser import ConfigParser

config = ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

INDEX_HISTORY_FILE = os.path.join(config.get('INDEX', 'index_folder'), 'data', 'index_history.csv')
API_KEY = config.get('COINGECKO', 'api_key')
API_URL = 'https://pro-api.coingecko.com/api/v3'

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
    return response.json()

start_timestamp = 1609632000
end_timestamp = 1680393600

ethereum_data = fetch_token_data('ethereum', start_timestamp, end_timestamp)
ethereum_prices = pd.DataFrame(ethereum_data['prices'], columns=['timestamp', 'price'])
ethereum_prices["timestamp"] = pd.to_datetime(ethereum_prices["timestamp"], unit="ms")
ethereum_prices.set_index("timestamp", inplace=True)
ethereum_prices["normalized_price"] = 100 * ethereum_prices["price"] / ethereum_prices.iloc[0]["price"]

bitcoin_data = fetch_token_data('bitcoin', start_timestamp, end_timestamp)
bitcoin_prices = pd.DataFrame(bitcoin_data['prices'], columns=['timestamp', 'price'])
bitcoin_prices["timestamp"] = pd.to_datetime(bitcoin_prices["timestamp"], unit="ms")
bitcoin_prices.set_index("timestamp", inplace=True)
bitcoin_prices["normalized_price"] = 100 * bitcoin_prices["price"] / bitcoin_prices.iloc[0]["price"]

index_history = pd.read_csv(INDEX_HISTORY_FILE)
index_history["timestamp"] = pd.to_datetime(index_history["timestamp"], unit="s")
index_history.set_index("timestamp", inplace=True)

fig, ax = plt.subplots(figsize=(16, 9), dpi=200)

ax.plot(index_history.index, index_history["index_value"], color='blue', label="Crypto Index")
ax.plot(ethereum_prices.index, ethereum_prices["normalized_price"], color='black', label="Normalized Ethereum Price")
ax.plot(bitcoin_prices.index, bitcoin_prices["normalized_price"], color='red', label="Normalized Bitcoin Price")

ax.set_title("Crypto Index, Normalized Ethereum Price, and Normalized Bitcoin Price")
ax.set_xlabel("Date")
ax.set_ylabel("Index Value")
ax.legend()

output_filename = config.get('INDEX', 'index_folder') + '_chart.png'
plt.savefig(os.path.join(config.get('INDEX', 'index_folder'), f"{config.get('INDEX', 'index_folder')}_chart.png"), dpi=300, bbox_inches='tight')
