Ethereum Ecosystem Index
Welcome to the Ethereum Ecosystem Index repository. This repository contains Python scripts for generating and calculating a crypto index based on Ethereum. To retrieve accurate price data, you'll need a Coingecko Pro API key.

If you want to replicate the existing index or create a new one, copy the provided boilerplate folder and rename it as per your requirements.

For a capitalization-weighted index: boilerplate-cw-index
For an equal-weighted index: boilerplate-ew-index



How to Use
Here are the steps you need to follow:

Modify the config.ini file
Before you calculate an index, update the config.ini file with the appropriate information:
index_constituents_number: Specify the number of constituents here.
index_folder: Specify the name of the index folder here.
api_key: Enter your Coingecko Pro API key here.

Run index_snapshot_generator.py
This script handles historical price data for cryptocurrencies and generates index snapshots for the crypto index. It uses the Coingecko API to retrieve token data and filters tokens based on their economic purpose and categories (as defined in classification.csv). The snapshots are saved in the data/index_snapshots folder.

Run fetch_prices.py
This script fetches historical price data for the tokens included in each index snapshot during the rebalancing periods. It retrieves token data using the Coingecko API and saves the price data in the data/prices folder.

Run calculate_index.py
This script calculates the crypto index using the price data fetched by the fetch_prices.py script. It calculates the market capitalization of each token and normalizes the values to create the index.

Optional: Run plot.py
This script generates a plot of the crypto index using the data produced by the calculate_index.py script. It plots the index alongside two popular benchmarks, namely Bitcoin and Ethereum. The plot is saved as a PNG image in the plots folder.




Directory Structure
The common folder contains the classification.csv file and the historical_snapshot files retrieved from CoinMarketCap.

The risk-free-rate folder has the daily risk-free rate retrieved from Yahoo Finance, used for calculating the Sharpe and Sortino ratios.

The statistics folder contains statistical analysis scripts and results for the capitalization-weighted and equal-weighted indices.

The comparison folder contains the statistical comparison between index-cw-30 and popular benchmarks.



Dependencies
To run the scripts, you need to have the following dependencies installed:

requests
tqdm
configparser
datetime
csv
shutil
pathlib
matplotlib
You can install these Python libraries using pip.