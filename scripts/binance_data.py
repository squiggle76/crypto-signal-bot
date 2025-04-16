# binance_data.py
import requests

def get_recent_price_changes(pair="BTCUSDT", interval="1m", limit=60):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": pair,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)
    data = response.json()

    price_changes = []
    volumes = []

    for i in range(1, len(data)):
        prev_close = float(data[i - 1][4])
        current_close = float(data[i][4])
        change = abs(current_close - prev_close) / prev_close
        price_changes.append(change)

        volume = float(data[i][5])
        volumes.append(volume)

    return price_changes, volumes
