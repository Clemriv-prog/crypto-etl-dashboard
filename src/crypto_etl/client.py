"""Un appel manuel par actif, timeout et messages sans secret."""

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


class Client:
    def __init__(self, config, session=None):
        self.config = config
        self.session = session or requests.Session()

    def fetch(self, coin):
        c = self.config
        if not c.api_key:
            raise ValueError("COINGECKO_API_KEY requis pour une collecte réelle")
        try:
            response = self.session.get(
                f"{c.base_url}/coins/{coin}/market_chart",
                params={"vs_currency": c.currency, "days": c.days, "interval": "daily"},
                headers={"x-cg-demo-api-key": c.api_key},
                timeout=c.timeout,
            )
        except requests.RequestException:
            raise RuntimeError("Erreur réseau : relancer la collecte plus tard") from None
        if response.status_code != 200:
            raise ValueError(f"HTTP {response.status_code} : collecte refusée")
        try:
            return response.json()
        except ValueError:
            raise ValueError("JSON illisible") from None
