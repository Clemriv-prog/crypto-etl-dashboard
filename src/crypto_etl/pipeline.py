"""Orchestration, archives brutes et suivi des échecs par crypto."""

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

from .client import Client
from .storage import connect, upsert
from .transform import transform

logger = logging.getLogger(__name__)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run(config, fetch=None, demo=False):
    fetch = fetch or Client(config).fetch
    run_id, started = uuid4().hex, utc_now()
    raw_dir = config.data_dir / ("raw-demo" if demo else "raw") / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    details, rows, successes = {}, 0, 0
    with connect(config.db_path(demo)) as db:
        with db:
            db.execute(
                "INSERT INTO pipeline_runs(run_id,started_at,status) VALUES (?,?,?)",
                (run_id, started, "running"),
            )
        for coin in config.coins:
            try:
                payload = fetch(coin)
                (raw_dir / f"{coin}.json").write_text(json.dumps(payload), encoding="utf-8")
                frame, report = transform(payload, coin, config.currency, config.days)
                if frame.empty:
                    raise ValueError("Aucune observation valide")
                upsert(db, frame, utc_now())
                details[coin] = {"status": "success", "quality": report}
                rows += len(frame)
                successes += 1
            except Exception as error:  # noqa: BLE001 — isoler chaque crypto dans le pipeline
                # Les exceptions externes peuvent contenir des secrets : ne pas les sérialiser.
                details[coin] = {"status": "failed", "error_type": type(error).__name__}
                logger.error("Collecte échouée pour %s (%s)", coin, type(error).__name__)
        status = (
            "success" if successes == len(config.coins) else "partial" if successes else "failed"
        )
        with db:
            db.execute(
                """UPDATE pipeline_runs SET ended_at=?, status=?, rows_processed=?,
                       details=? WHERE run_id=?""",
                (utc_now(), status, rows, json.dumps(details), run_id),
            )
    return {"run_id": run_id, "status": status, "rows": rows, "details": details}
