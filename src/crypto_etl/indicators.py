"""Fenêtres calendaires complètes ; volatilité non annualisée en pourcentage."""

import pandas as pd

from .trends import trend_indicators


def indicators(frame):
    parts = []
    for (coin, currency), group in frame.groupby(["coin_id", "vs_currency"]):
        daily = group.set_index("date_utc").sort_index().asfreq("D")
        daily["coin_id"], daily["vs_currency"] = coin, currency
        price = daily["price"]
        daily["return_1d"] = price.pct_change(fill_method=None) * 100
        daily["return_7d"] = (price / price.shift(7) - 1) * 100
        for window in (7, 30):
            daily[f"ma_{window}"] = price.rolling(window, min_periods=window).mean()
        daily["volatility_30d"] = daily["return_1d"].rolling(30, min_periods=30).std(ddof=1)
        daily = daily.join(trend_indicators(price))
        parts.append(daily.reset_index())
    return pd.concat(parts, ignore_index=True) if parts else frame.copy()


def select_period(frame, start, end):
    selected = frame.loc[frame["date_utc"].between(pd.Timestamp(start), pd.Timestamp(end))].copy()
    if selected.empty:
        return selected
    groups = selected.groupby(["coin_id", "vs_currency"])["price"]
    selected["base_100"] = 100 * selected["price"] / groups.transform("first")
    selected["drawdown"] = (selected["price"] / groups.cummax() - 1) * 100
    return selected
