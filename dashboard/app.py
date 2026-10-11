"""Interface exclusivement locale : aucun appel API à l'interaction."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from crypto_etl.config import load_config
from crypto_etl.indicators import indicators, select_period
from crypto_etl.storage import latest_run, read_data

st.set_page_config(page_title="Observatoire crypto", page_icon="📈", layout="wide")
st.title("Observatoire crypto")
config = load_config()
demo = st.sidebar.toggle("Démonstration synthétique", value=True)
if demo:
    st.warning("DÉMONSTRATION — données synthétiques, sans valeur de marché réelle.")
path = config.db_path(demo)
st.caption(f"Devise : {config.currency.upper()} · snapshots quotidiens UTC · base : {path}")
if not path.exists():
    st.info("Initialisez les données depuis le dossier du projet :")
    st.code("crypto-etl demo" if demo else "crypto-etl update")
    st.stop()
data = read_data(path, config.currency)
if data.empty:
    st.info("Base vide pour cette devise. Lancez crypto-etl demo ou crypto-etl update.")
    st.stop()
run = latest_run(path)
if run:
    st.caption(f"Dernière collecte : {run['ended_at']} · statut : {run['status']}")
    if run["status"] != "success":
        st.warning("Mise à jour partielle ou échouée : les dernières données valides sont conservées.")
    reports = json.loads(run["details"])
    if any(v.get("quality", {}).get("missing_days") or
           v.get("quality", {}).get("missing_market_cap") or
           v.get("quality", {}).get("missing_volume") or
           v.get("quality", {}).get("rejected") for v in reports.values()):
        st.warning("Données incomplètes ou rejetées : consultez le bilan qualité.")
    with st.expander("Bilan de la dernière collecte"):
        st.json(reports)
today = pd.Timestamp.now(tz="UTC").normalize().tz_localize(None)
latest = data.groupby("coin_id")["date_utc"].max()
if (latest < today - pd.Timedelta(days=1)).any():
    st.warning("Certaines données sont anciennes : relancez la collecte manuellement.")
coins = st.sidebar.multiselect("Cryptomonnaies", config.coins, default=list(config.coins))
dates = st.sidebar.date_input("Période", value=(data.date_utc.min().date(),
                                             data.date_utc.max().date()),
                              min_value=data.date_utc.min().date(),
                              max_value=data.date_utc.max().date())
show_ma = st.sidebar.checkbox("Moyennes mobiles", value=True)
if len(dates) != 2 or not coins:
    st.info("Sélectionnez des cryptomonnaies et une période complète.")
    st.stop()
calculated = indicators(data[data.coin_id.isin(coins)])
selected = select_period(calculated, *dates)
observed = selected.dropna(subset=["price"])
if observed.empty:
    st.info("Aucun prix disponible sur cette période.")
    st.stop()
if selected["price"].isna().any():
    st.warning("Des jours sont manquants ; les graphiques ne comblent pas les intervalles.")
if selected["volatility_30d"].isna().any():
    st.info("Certains indicateurs sont indisponibles : historique insuffisant ou jours manquants.")
overview, analysis, comparison = st.tabs(["Vue d’ensemble", "Analyse d’une crypto", "Comparaison"])
summary = observed.groupby("coin_id").tail(1).copy()
summary["performance_pct"] = summary["base_100"] - 100
columns = ["coin_id", "date_utc", "price", "return_1d", "return_7d", "performance_pct"]
with overview:
    st.dataframe(summary[columns], hide_index=True, use_container_width=True)
with analysis:
    coin = st.selectbox("Actif", coins)
    subset = selected[selected.coin_id == coin]
    values = ["price", "ma_7", "ma_30"] if show_ma else ["price"]
    st.plotly_chart(px.line(subset, x="date_utc", y=values, title="Prix et moyennes mobiles"),
                    use_container_width=True)
    st.plotly_chart(px.bar(subset, x="date_utc", y="volume_24h", title="Volume observé sur 24 h"),
                    use_container_width=True)
    for name in ("volatility_30d", "drawdown"):
        st.plotly_chart(px.line(subset, x="date_utc", y=name, title=f"{name} (%)"),
                        use_container_width=True)
with comparison:
    st.plotly_chart(px.line(selected, x="date_utc", y="base_100", color="coin_id",
                            title="Performance sur la sélection — base 100"),
                    use_container_width=True)
    st.dataframe(summary[columns + ["volatility_30d", "drawdown"]], hide_index=True)
st.download_button("Exporter la sélection CSV", selected.to_csv(index=False).encode("utf-8"),
                   file_name="crypto-demo.csv" if demo else "crypto-coingecko.csv", mime="text/csv")
st.caption("Prix observés, sans clôture officielle. Volume 24 h non cumulable. "
           "Source des collectes réelles : [CoinGecko](https://www.coingecko.com/).")
