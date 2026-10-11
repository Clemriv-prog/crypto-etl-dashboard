"""Repères descriptifs causaux : aucun signal ne lit les prix futurs."""

import numpy as np
import pandas as pd


def slope_pct(values):
    x = np.arange(len(values), dtype=float)
    slope = np.polyfit(x, values, 1)[0]
    return 100 * slope / np.mean(values)


def fit_score(values):
    x = np.arange(len(values), dtype=float)
    fitted = np.polyval(np.polyfit(x, values, 1), x)
    total = np.sum((values - np.mean(values)) ** 2)
    return 0.0 if total == 0 else float(1 - np.sum((values - fitted) ** 2) / total)


def trend_indicators(price):
    result = pd.DataFrame(index=price.index)
    mean = price.rolling(20, min_periods=20).mean()
    std = price.rolling(20, min_periods=20).std(ddof=1)
    result["bollinger_lower"] = mean - 2 * std
    result["bollinger_upper"] = mean + 2 * std
    change = price.diff()
    gains = change.clip(lower=0).rolling(14, min_periods=14).mean()
    losses = (-change.clip(upper=0)).rolling(14, min_periods=14).mean()
    # RSI à moyennes simples, explicitement distinct du lissage de Wilder.
    result["rsi_14"] = 100 - 100 / (1 + gains / losses)
    result.loc[(losses == 0) & (gains > 0), "rsi_14"] = 100
    result.loc[(losses == 0) & (gains == 0), "rsi_14"] = 50
    result["trend_slope_30d"] = price.rolling(30, min_periods=30).apply(slope_pct, raw=True)
    result["trend_r2_30d"] = price.rolling(30, min_periods=30).apply(fit_score, raw=True)
    result["trend"] = "Indisponible"
    known = result.trend_slope_30d.notna()
    result.loc[known, "trend"] = "Sans tendance linéaire nette"
    coherent = known & (result.trend_r2_30d >= 0.5)
    result.loc[coherent & (result.trend_slope_30d > 0.1), "trend"] = "Haussière"
    result.loc[coherent & (result.trend_slope_30d < -0.1), "trend"] = "Baissière"
    result["support_20d"] = price.shift(1).rolling(20, min_periods=20).min()
    result["resistance_20d"] = price.shift(1).rolling(20, min_periods=20).max()
    result["breakout"] = "Indisponible"
    available = price.notna() & result.support_20d.notna()
    result.loc[available, "breakout"] = "Dans le canal précédent"
    result.loc[available & (price > result.resistance_20d), "breakout"] = "Nouveau sommet 20 j"
    result.loc[available & (price < result.support_20d), "breakout"] = "Nouveau creux 20 j"
    short, long = price.rolling(7).mean(), price.rolling(30).mean()
    difference = short - long
    result["ma_cross"] = "Indisponible"
    valid = difference.notna() & difference.shift(1).notna()
    result.loc[valid, "ma_cross"] = "Aucun croisement"
    result.loc[valid & (difference > 0) & (difference.shift(1) <= 0), "ma_cross"] = (
        "Croisement haussier"
    )
    result.loc[valid & (difference < 0) & (difference.shift(1) >= 0), "ma_cross"] = (
        "Croisement baissier"
    )
    result["momentum_30d"] = (price / price.shift(30) - 1) * 100
    return result
