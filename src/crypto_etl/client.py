"""Client HTTP : erreurs expurgées, tentatives bornées, aucune clé dans les logs."""

import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests


def validate_payload(payload):
    if not isinstance(payload, dict):
        raise TypeError("Réponse JSON non objet")
    for key in ("prices", "market_caps", "total_volumes"):
        values = payload.get(key)
        if not isinstance(values, list):
            raise TypeError(f"Série absente ou invalide : {key}")
        if any(not isinstance(p, (list, tuple)) or len(p) != 2 for p in values):
            raise ValueError(f"Paires invalides : {key}")
    return payload


def retry_delay(value, attempt):
    try:
        return max(0, float(value))
    except (TypeError, ValueError):
        try:
            return max(
                0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
            )
        except (TypeError, ValueError, OverflowError):
            return min(2**attempt, 30)


class Client:
    def __init__(self, config, session=None, sleep=time.sleep):
        self.config = config
        self.session = session or requests.Session()
        self.sleep = sleep

    def fetch(self, coin):
        c = self.config
        if not c.api_key:
            raise ValueError("COINGECKO_API_KEY requis pour une collecte réelle")
        for attempt in range(c.attempts):
            delay = min(2**attempt, 30)
            try:
                response = self.session.get(
                    f"{c.base_url}/coins/{coin}/market_chart",
                    params={"vs_currency": c.currency, "days": c.days, "interval": "daily"},
                    headers={"x-cg-demo-api-key": c.api_key},
                    timeout=c.timeout,
                )
            except requests.RequestException:
                pass
            else:
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError:
                        raise ValueError("JSON illisible") from None
                if response.status_code != 429 and response.status_code < 500:
                    raise ValueError(f"HTTP {response.status_code} : requête refusée")
                delay = retry_delay(response.headers.get("Retry-After"), attempt)
            if attempt + 1 < c.attempts:
                self.sleep(delay)
        raise RuntimeError("Échec API après le nombre maximal de tentatives")
