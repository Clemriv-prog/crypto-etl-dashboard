"""Bilan sérialisable, sans interpolation."""

import pandas as pd


def quality_report(frame, rejected, duplicates, excluded, start, end):
    expected = pd.date_range(start, end, freq="D")
    observed = pd.DatetimeIndex(frame["date_utc"])
    prices = frame.set_index("date_utc")["price"].reindex(expected)
    returns = prices.pct_change(fill_method=None)
    return {
        "accepted": len(frame),
        "rejected": rejected,
        "duplicate_timestamps": duplicates,
        "excluded_current_or_future": excluded,
        "missing_days": expected.difference(observed).strftime("%Y-%m-%d").tolist(),
        "missing_market_cap": int(frame["market_cap"].isna().sum()),
        "missing_volume": int(frame["volume_24h"].isna().sum()),
        "large_changes": returns[returns.abs() > 0.5].index.strftime("%Y-%m-%d").tolist(),
    }
