"""Vérifier l'état vide et les filtres via le moteur Streamlit, sans serveur réseau."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from crypto_etl.config import Config
from crypto_etl.demo import synthetic
from crypto_etl.pipeline import run

APP = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


def test_dashboard_empty_and_demo(tmp_path, monkeypatch):
    monkeypatch.setenv("CRYPTO_DATA_DIR", str(tmp_path))
    app = AppTest.from_file(str(APP)).run()
    assert not app.exception
    assert "Initialisez" in app.info[0].value
    config = Config(data_dir=tmp_path)
    assert run(config, synthetic, demo=True)["status"] == "success"
    app.run()
    assert not app.exception
    assert len(app.tabs) == 3
    assert len(app.dataframe) == 4
    app.sidebar.multiselect[0].set_value(["bitcoin"]).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 1
    app.sidebar.multiselect[0].set_value([]).run()
    assert not app.exception
    assert "Sélectionnez" in app.info[0].value
