"""Configuration commune à la CLI et au dashboard."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    api_key: str = field(default="", repr=False)
    currency: str = "usd"
    days: int = 90
    data_dir: Path = Path("data")
    coins: tuple[str, ...] = ("bitcoin", "ethereum", "solana")
    timeout: float = 30
    base_url: str = "https://api.coingecko.com/api/v3"

    def __post_init__(self):
        if not 1 <= self.days <= 365:
            raise ValueError("CRYPTO_DAYS doit être compris entre 1 et 365")
        if not self.currency.isalpha() or self.timeout <= 0:
            raise ValueError("Configuration invalide")

    def db_path(self, demo=False):
        return self.data_dir / ("demo.db" if demo else "market.db")


def load_config():
    return Config(
        api_key=os.getenv("COINGECKO_API_KEY", ""),
        currency=os.getenv("CRYPTO_CURRENCY", "usd").lower(),
        days=int(os.getenv("CRYPTO_DAYS", "90")),
        data_dir=Path(os.getenv("CRYPTO_DATA_DIR", "data")),
    )
