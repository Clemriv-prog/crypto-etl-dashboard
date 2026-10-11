import numpy as np
import pandas as pd
import pytest

from crypto_etl.trends import trend_indicators


def test_linear_rising_and_falling():
    rising = trend_indicators(pd.Series(np.arange(100.0, 160.0)))
    last = rising.iloc[-1]
    assert last.trend == "Haussière"
    assert last.trend_r2_30d == pytest.approx(1)
    assert last.trend_slope_30d == pytest.approx(100 / np.mean(np.arange(130.0, 160.0)))
    assert last.rsi_14 == 100
    assert last.breakout == "Nouveau sommet 20 j"
    assert last.resistance_20d == 158
    falling = trend_indicators(pd.Series(np.arange(160.0, 100.0, -1))).iloc[-1]
    assert falling.trend == "Baissière" and falling.rsi_14 == 0
    assert falling.breakout == "Nouveau creux 20 j"


def test_flat_and_bands():
    result = trend_indicators(pd.Series([100.0] * 40))
    assert result.iloc[-1].trend == "Sans tendance linéaire nette"
    assert result.iloc[-1].rsi_14 == 50
    assert result.iloc[-1].bollinger_lower == 100
    assert result.iloc[-1].bollinger_upper == 100
    assert pd.isna(result.rsi_14.iloc[13])


def test_missing_values_and_no_future_leakage():
    price = pd.Series(np.arange(100.0, 160.0))
    full = trend_indicators(price)
    prefix = trend_indicators(price.iloc[:45])
    pd.testing.assert_frame_equal(full.iloc[:45], prefix)
    price.iloc[40] = np.nan
    missing = trend_indicators(price)
    assert pd.isna(missing.iloc[41].rsi_14)
    assert missing.iloc[41].trend == "Indisponible"
    assert missing.iloc[41].breakout == "Indisponible"


def test_crossing_is_an_event():
    price = pd.Series([100.0] * 35 + list(np.arange(101.0, 131.0)))
    result = trend_indicators(price)
    assert result.ma_cross.iloc[35] == "Croisement haussier"
    assert result.ma_cross.iloc[36] == "Aucun croisement"
