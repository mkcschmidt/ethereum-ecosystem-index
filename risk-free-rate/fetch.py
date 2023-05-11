import yfinance as yf
import pandas as pd
import datetime

# Define start and end timestamps
start_ts = 1609632000
end_ts = 1680393600

# Convert timestamps to date strings
start_date = datetime.datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d")
end_date = datetime.datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d")

# Check if the start_date is a weekend and adjust to the next weekday
start_date_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
if start_date_dt.weekday() > 4:  # 0: Monday, 1: Tuesday, ..., 6: Sunday
    start_date_dt = start_date_dt + datetime.timedelta(days=(7 - start_date_dt.weekday()))
    start_date = start_date_dt.strftime("%Y-%m-%d")

# Query Yahoo Finance API with ticker symbol ^IRX
df = yf.download("^IRX", start=start_date, end=end_date)

# Select only the yield column
df = df[["Close"]]

# Rename column to yield
df = df.rename(columns={"Close": "yield"})

# Fill any missing values with previous valid value
df = df.fillna(method="ffill")

# Save dataframe to a csv file
df.to_csv("risk-free-rate/risk_free_rate.csv", sep=",", header=True, index=True, date_format="%Y-%m-%d")
