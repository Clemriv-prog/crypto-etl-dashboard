"""Une page d'analyse ; les filtres consultent seulement SQLite."""

import pandas as pd
import plotly.express as px
import streamlit as st

from crypto_etl.config import load_config
from crypto_etl.indicators import indicators, select_period
from crypto_etl.storage import latest_run, read_data

st.set_page_config(page_title="Key Crypto - V1", page_icon="📈", layout="wide")
st.title("Key Crypto - V1")
st.caption("Bitcoin, Ethereum et Solana : collecte, stockage et analyse quotidienne.")
config = load_config()
demo = st.sidebar.toggle("Démonstration synthétique", value=True)
if demo:
    st.warning("DÉMONSTRATION : données synthétiques, sans valeur de marché réelle.")
path = config.db_path(demo)
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
        st.warning("Collecte incomplète : les anciennes données valides sont conservées.")
today = pd.Timestamp.now(tz="UTC").normalize().tz_localize(None)
if (data.groupby("coin_id").date_utc.max() < today - pd.Timedelta(days=1)).any():
    st.warning("Certaines données sont anciennes : relancez la collecte manuellement.")
coins = st.sidebar.multiselect("Cryptomonnaies", config.coins, default=list(config.coins))
dates = st.sidebar.date_input(
    "Période",
    value=(data.date_utc.min().date(), data.date_utc.max().date()),
    min_value=data.date_utc.min().date(),
    max_value=data.date_utc.max().date(),
)
if not coins or len(dates) != 2:
    st.info("Sélectionnez des cryptomonnaies et une période complète.")
    st.stop()
selected = select_period(indicators(data[data.coin_id.isin(coins)]), *dates)
observed = selected.dropna(subset=["price"])
if observed.empty:
    st.info("Aucun prix sur cette période.")
    st.stop()
if selected.price.isna().any():
    st.warning("Des jours sont manquants : les prix ne sont pas interpolés.")
st.caption(f"Devise : {config.currency.upper()} · dates UTC · collecte : {config.days} jours")
st.subheader("Dernières observations de la sélection")
summary = observed.groupby("coin_id").tail(1)
st.dataframe(
    summary[["coin_id", "date_utc", "price", "return_1d", "volatility_30d"]],
    hide_index=True,
    width="stretch",
)
st.subheader("Comparaison des performances")
st.plotly_chart(
    px.line(
        selected,
        x="date_utc",
        y="base_100",
        color="coin_id",
        title="Base 100 au premier prix disponible de la sélection",
    ),
    width="stretch",
)
coin = st.selectbox("Actif à analyser", coins)
subset = selected[selected.coin_id == coin]
st.plotly_chart(
    px.line(
        subset, x="date_utc", y=["price", "ma_7"], title="Prix observé et moyenne mobile 7 jours"
    ),
    width="stretch",
)
st.plotly_chart(
    px.line(
        subset, x="date_utc", y="volatility_30d", title="Volatilité 30 jours - non annualisée (%)"
    ),
    width="stretch",
)
st.caption(
    "La moyenne exige 7 prix consécutifs ; la volatilité exige 31 prix pour 30 rendements. "
    "Les premiers résultats indisponibles restent vides. Les indicateurs décrivent le passé."
)
st.download_button(
    "Exporter la sélection CSV",
    selected.to_csv(index=False).encode("utf-8"),
    file_name="crypto-demo.csv" if demo else "crypto-coingecko.csv",
    mime="text/csv",
)
st.caption(
    "Prix observés, sans clôture officielle. "
    "Source des collectes réelles : [CoinGecko](https://www.coingecko.com/)."
)
