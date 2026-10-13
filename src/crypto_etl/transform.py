"""Alignement exact des timestamps puis dernier snapshot valide du jour UTC."""

import math

import pandas as pd

from .client import validate_payload
from .quality import quality_report


def transform(payload, coin, currency, days=90, now=None):
    validate_payload(payload)
    today = pd.Timestamp(now or pd.Timestamp.now(tz="UTC"))
    today = today.tz_localize("UTC") if today.tzinfo is None else today.tz_convert("UTC")
    today = today.normalize().tz_localize(None)
    start = today - pd.Timedelta(days=days)
    series = []
    duplicates = 0
    for key, name in (
        ("prices", "price"),
        ("market_caps", "market_cap"),
        ("total_volumes", "volume_24h"),
    ):
        part = pd.DataFrame(payload[key], columns=["source_timestamp", name])
        part["source_timestamp"] = pd.to_numeric(part["source_timestamp"], errors="coerce")
        part = part.dropna(subset=["source_timestamp"])
        duplicates += int(part.duplicated("source_timestamp").sum())
        part = part.drop_duplicates("source_timestamp", keep="last")
        series.append(part.set_index("source_timestamp"))
    frame = pd.concat(series, axis=1).reset_index()
    frame["date_utc"] = (
        pd.to_datetime(frame["source_timestamp"], unit="ms", utc=True, errors="coerce")
        .dt.tz_localize(None)
        .dt.normalize()
    )
    for column in ("price", "market_cap", "volume_24h"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        valid = frame[column].map(math.isfinite) & (frame[column] >= 0)
        frame.loc[~valid, column] = float("nan")
    invalid = frame["price"].isna() | (frame["price"] <= 0) | frame["date_utc"].isna()
    rejected = int(invalid.sum())
    excluded = int((frame["date_utc"] >= today).sum())
    frame = frame.loc[~invalid & frame["date_utc"].between(start, today, inclusive="left")]
    frame = frame.sort_values("source_timestamp").drop_duplicates("date_utc", keep="last")
    frame = frame.sort_values("date_utc").reset_index(drop=True)
    report = quality_report(
        frame, rejected, duplicates, excluded, start, today - pd.Timedelta(days=1)
    )
    frame["coin_id"] = coin
    frame["vs_currency"] = currency
    return frame, report
