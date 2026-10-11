"""Tests des risques métier, entièrement hors réseau."""

from unittest.mock import Mock

import pandas as pd
import pytest
import requests

from crypto_etl.client import Client, validate_payload
from crypto_etl.config import Config
from crypto_etl.indicators import indicators, select_period
from crypto_etl.pipeline import run
from crypto_etl.storage import connect, read_data, upsert
from crypto_etl.transform import transform


def payload(prices=(100, 105, 110), start="2024-01-01"):
    dates = pd.date_range(start, periods=len(prices), tz="UTC")
    pairs = [[int(d.timestamp()*1000), p] for d, p in zip(dates, prices)]
    return {"prices": pairs, "market_caps": [[t, 10] for t, _ in pairs],
            "total_volumes": [[t, 20] for t, _ in pairs]}


@pytest.mark.parametrize("value", [None, [], {}, {"prices": [1]}])
def test_bad_payload(value):
    with pytest.raises(ValueError):
        validate_payload(value)


def test_empty():
    frame, quality = transform(payload(()), "bitcoin", "usd", 3, "2024-01-04")
    assert frame.empty and len(quality["missing_days"]) == 3


def test_alignment_duplicates_invalid_and_today():
    raw = payload((100, 105, -2, 120))
    raw["prices"] = raw["prices"][::-1] + [raw["prices"][0]]
    raw["market_caps"] = raw["market_caps"][1:]
    raw["total_volumes"][1][1] = float("inf")
    frame, quality = transform(raw, "bitcoin", "usd", 4, "2024-01-04")
    assert frame.price.tolist() == [100, 105]
    assert pd.isna(frame.iloc[0].market_cap)
    assert pd.isna(frame.iloc[1].volume_24h)
    assert quality["rejected"] == 1
    assert quality["duplicate_timestamps"] == 1
    assert quality["excluded_current_or_future"] == 1
    assert "2024-01-03" in quality["missing_days"]


def test_alignment_is_not_positional():
    raw = payload()
    raw["market_caps"] = [[raw["prices"][2][0], 30], [raw["prices"][0][0], 10]]
    frame, _ = transform(raw, "bitcoin", "usd", 3, "2024-01-04")
    assert frame.market_cap.iloc[0] == 10
    assert pd.isna(frame.market_cap.iloc[1])
    assert frame.market_cap.iloc[2] == 30


def test_daily_last_valid():
    raw = payload((100,))
    raw["prices"].append([raw["prices"][0][0] + 3600000, 110])
    frame, _ = transform(raw, "bitcoin", "usd", 1, "2024-01-02")
    assert frame.price.tolist() == [110]


def test_indicators_and_exact_calendar():
    frame, _ = transform(payload(tuple(range(100, 140))), "bitcoin", "usd", 40, "2024-02-10")
    result = indicators(frame)
    assert result.return_1d.iloc[1] == pytest.approx(1)
    assert result.ma_7.iloc[6] == 103
    assert result.return_7d.iloc[7] == pytest.approx(7)
    assert result.ma_30.iloc[29] == 114.5
    assert result.volatility_30d.iloc[30] == pytest.approx(result.return_1d.iloc[1:31].std(ddof=1))
    assert pd.isna(result.volatility_30d.iloc[29])
    selection = select_period(result, "2024-01-05", "2024-01-10")
    assert selection.base_100.iloc[0] == 100
    assert selection.ma_7.iloc[-1] == 106
    missing = indicators(frame.drop(index=3))
    assert pd.isna(missing.return_1d.iloc[4])
    assert pd.isna(missing.ma_7.iloc[6])
    assert pd.isna(missing.return_7d.iloc[10])


def test_drawdown():
    frame, _ = transform(payload((100, 120, 90)), "bitcoin", "usd", 3, "2024-01-04")
    result = select_period(indicators(frame), "2024-01-01", "2024-01-03")
    assert result.drawdown.iloc[-1] == -25
    assert result.base_100.iloc[-1] == 90


def test_upsert_and_revision(tmp_path):
    path = tmp_path / "test.db"
    frame, _ = transform(payload(), "bitcoin", "usd", 3, "2024-01-04")
    with connect(path) as db:
        upsert(db, frame, "first")
        upsert(db, frame, "second")
        frame.loc[0, "price"] = 200
        upsert(db, frame, "third")
    stored = read_data(path, "usd")
    assert len(stored) == 3 and stored.price.iloc[0] == 200


def test_client_retry_and_auth():
    response = Mock(status_code=429, headers={"Retry-After": "3"})
    good = Mock(status_code=200)
    good.json.return_value = payload()
    session, sleep = Mock(), Mock()
    session.get.side_effect = [response, good]
    client = Client(Config(api_key="secret"), session, sleep)
    assert client.fetch("bitcoin") == payload()
    sleep.assert_called_once_with(3)
    assert session.get.call_args.kwargs["headers"] == {"x-cg-demo-api-key": "secret"}
    session.get.side_effect = None
    session.get.return_value = response
    with pytest.raises(RuntimeError):
        client.fetch("bitcoin")
    assert session.get.call_count == 6


@pytest.mark.parametrize("status", [400, 401, 403])
def test_no_retry_for_bad_request(status):
    session = Mock()
    session.get.return_value = Mock(status_code=status)
    with pytest.raises(ValueError):
        Client(Config(api_key="secret"), session, Mock()).fetch("bitcoin")
    assert session.get.call_count == 1


def test_network_retry_and_invalid_json():
    session = Mock()
    session.get.side_effect = requests.ConnectionError("secret")
    with pytest.raises(RuntimeError, match="maximal"):
        Client(Config(api_key="secret", attempts=2), session, Mock()).fetch("bitcoin")
    assert session.get.call_count == 2
    session.get.side_effect = None
    session.get.return_value = Mock(status_code=200)
    session.get.return_value.json.side_effect = ValueError("secret")
    with pytest.raises(ValueError, match="JSON illisible"):
        Client(Config(api_key="secret"), session, Mock()).fetch("bitcoin")


def test_partial_pipeline_preserves_data(tmp_path):
    config = Config(data_dir=tmp_path)
    yesterday = (pd.Timestamp.now(tz="UTC").normalize()-pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    first = run(config, lambda _: payload((100,), yesterday))
    assert first["status"] == "success"

    def fetch(coin):
        if coin == "ethereum":
            raise RuntimeError("secret")
        return payload((200,), yesterday)

    second = run(config, fetch)
    assert second["status"] == "partial"
    data = read_data(config.db_path(), "usd").set_index("coin_id")
    assert data.loc["ethereum", "price"] == 100
    assert data.loc["bitcoin", "price"] == 200
    assert "secret" not in str(second)
    assert len(list((tmp_path / "raw").glob("*/*.json"))) == 5
