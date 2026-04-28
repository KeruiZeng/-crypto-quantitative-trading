import numpy as np
import pandas as pd

import requests

def fetch_binance_ohlcv(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    all_data = []

    while start_time < end_time:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000  # Max limit per request
        }
        response = requests.get(url, params=params)
        data = response.json()
        all_data.extend(data)

        if not data:
            break
        start_time = data[-1][0] + 1  # Add 1ms to avoid duplicates
    return all_data


price = pd.DataFrame()
columns = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume",
            "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"]

interval = "1m"  

dates = pd.date_range(start="2017-01-01", end='2025-11-23', freq='D')
date_strings = dates.strftime('%Y-%m-%d').tolist()


from tqdm import tqdm


price_data = pd.DataFrame()


for i,t in enumerate(tqdm(date_strings)):
    if i==0:
        continue
    
    else:
        start_time=int(pd.Timestamp(date_strings[i-1]).timestamp() * 1000)
        end_time = int(pd.Timestamp(date_strings[i]).timestamp() * 1000)

        p = fetch_binance_ohlcv("ETHUSDT", interval, start_time, end_time)
        p = pd.DataFrame(p,columns=columns)
        # p = p[["Open Time", "Close"]]

        price_data = pd.concat([price_data,p], ignore_index=True)


price_data.to_csv('eth_second_price_MIN.csv')

print('finished')
