"""Données déterministes synthétiques, sans requête HTTP."""

import math

import pandas as pd


def synthetic(coin, days=180):
    base = {"bitcoin": 50000, "ethereum": 2500, "solana": 100}[coin]
    dates = pd.date_range(end=pd.Timestamp.now(tz="UTC").normalize()-pd.Timedelta(days=1),
                          periods=days, freq="D")
    payload = {"prices": [], "market_caps": [], "total_volumes": []}
    for i, date in enumerate(dates):
        timestamp = int(date.timestamp() * 1000)
        price = base * (1 + i / 1000 + 0.08 * math.sin(i / 12 + base % 7))
        for key, value in (("prices", price), ("market_caps", price * 1e7),
                           ("total_volumes", price * 1e5 * (1 + 0.2 * math.cos(i)))):
            payload[key].append([timestamp, value])
    return payload
