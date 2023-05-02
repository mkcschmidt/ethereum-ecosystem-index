import csv
import os
import requests
import configparser
from pathlib import Path
from tqdm import tqdm

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

index_constituents_number = config.getint('INDEX', 'index_constituents_number')
index_folder = config.get('INDEX', 'index_folder')
historical_snapshots_folder = "common/historical_snapshots"
classification_file = "common/classification.csv"
index_snapshots_folder = f"{index_folder}/data/index_snapshots"

# Create index_snapshots folder if it doesn't exist
Path(index_snapshots_folder).mkdir(parents=True, exist_ok=True)

API_URL = "https://pro-api.coingecko.com/api/v3/coins/"
API_KEY = config.get('COINGECKO', 'api_key')

def get_ethereum_ecosystem_tokens(coingecko_id):
    url = f"{API_URL}{coingecko_id}"
    response = requests.get(url, params={'x_cg_pro_api_key': API_KEY})
    
    if response.status_code != 200:
        return False
    
    data = response.json()
    if isinstance(data, list):
        print(f"\033[1;91m\nNo categories found for token {row['Name']}\033[0m")
        return False
    categories = data.get("categories", [])
    
    return "Ethereum Ecosystem" in categories

def get_classification_data(classification_file):
    classification_data = {}
    with open(classification_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            coingecko_id = row["Coingecko ID"]
            economic_purpose = row["Economic Purpose"]
            classification_data[coingecko_id] = economic_purpose
    return classification_data

classification_data = get_classification_data(classification_file)

files = os.listdir(historical_snapshots_folder)
progress_bar = tqdm(files, desc="Processing files", bar_format="{l_bar}\033[1;31m{bar}\033[0m{r_bar}")

for file in progress_bar:
    input_file = os.path.join(historical_snapshots_folder, file)
    output_file = os.path.join(index_snapshots_folder, file)
    
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        index_count = 0

        for row in reader:
            coingecko_id = row["Coingecko ID"]
            if coingecko_id == "empty":
                print(f"\033[1;91m\nToken with empty Coingecko ID: {row['Name']}\033[0m")
                continue

            if index_count >= index_constituents_number:
                break

            if get_ethereum_ecosystem_tokens(coingecko_id) and coingecko_id in classification_data:
                economic_purpose = classification_data[coingecko_id]
                if economic_purpose == "":
                    print(f"\033[1;91m\nEconomic purpose is empty for token {row['Name']}\033[0m")
                    continue
                
                if economic_purpose == "EEP22NT02" or economic_purpose == "EEP22TU03" or economic_purpose == "EEP22NT03":
                    writer.writerow(row)
                    index_count += 1

    progress_bar.bar_format = "{l_bar}\033[1;32m{bar}\033[0m{r_bar}"
    progress_bar
