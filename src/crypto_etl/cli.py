"""Commandes manuelles utilisables également par un planificateur local."""

import argparse
import json
import logging

from .config import load_config
from .demo import synthetic
from .pipeline import run


def main():
    parser = argparse.ArgumentParser(description="ETL crypto local")
    parser.add_argument("command", choices=["update", "demo"])
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = load_config()
    if args.command == "update" and not config.api_key:
        parser.error("Définir COINGECKO_API_KEY ou utiliser la commande demo")
    result = run(config, fetch=(lambda coin: synthetic(coin, config.days))
                 if args.command == "demo" else None, demo=args.command == "demo")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
