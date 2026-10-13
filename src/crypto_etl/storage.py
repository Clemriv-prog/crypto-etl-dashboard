"""Transactions SQLite : une crypto validée est chargée atomiquement."""

import sqlite3
from contextlib import closing, contextmanager

import pandas as pd


@contextmanager
def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS daily_market_data (
            coin_id TEXT NOT NULL, vs_currency TEXT NOT NULL, date_utc TEXT NOT NULL,
            source_timestamp INTEGER NOT NULL, price REAL NOT NULL CHECK(price>0),
            market_cap REAL CHECK(market_cap>=0), volume_24h REAL CHECK(volume_24h>=0),
            collected_at TEXT NOT NULL,
            PRIMARY KEY (coin_id, vs_currency, date_utc));
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, ended_at TEXT,
            status TEXT NOT NULL, rows_processed INTEGER NOT NULL DEFAULT 0,
            details TEXT NOT NULL DEFAULT '{}');
        """)
        yield db


def upsert(db, frame, collected_at):
    rows = []
    for row in frame.to_dict("records"):
        rows.append(
            (
                row["coin_id"],
                row["vs_currency"],
                row["date_utc"].strftime("%Y-%m-%d"),
                int(row["source_timestamp"]),
                float(row["price"]),
                None if pd.isna(row["market_cap"]) else float(row["market_cap"]),
                None if pd.isna(row["volume_24h"]) else float(row["volume_24h"]),
                collected_at,
            )
        )
    with db:
        db.executemany(
            """
        INSERT INTO daily_market_data VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(coin_id, vs_currency, date_utc) DO UPDATE SET
        source_timestamp=excluded.source_timestamp, price=excluded.price,
        market_cap=excluded.market_cap, volume_24h=excluded.volume_24h,
        collected_at=excluded.collected_at
        """,
            rows,
        )


def read_data(path, currency):
    with connect(path) as db:
        return pd.read_sql_query(
            "SELECT * FROM daily_market_data WHERE vs_currency=? ORDER BY date_utc",
            db,
            params=(currency,),
            parse_dates=["date_utc"],
        )


def latest_run(path):
    with connect(path) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 1").fetchone()
        return dict(row) if row else None
