# Key Crypto - V1 : pipeline ETL et dashboard

Projet étudiant : collecter, nettoyer, stocker et comparer les données de Bitcoin,
Ethereum et Solana. La V1 privilégie une chaîne simple à comprendre et à défendre
en entretien : **CoinGecko → pandas → SQLite → Streamlit / Plotly**.

## Périmètre

- Collecte manuelle de 90 jours par défaut, en USD (configurable).
- Dates UTC, prix contrôlés, jours manquants signalés sans interpolation.
- Stockage SQLite et mises à jour sans doublons par upsert.
- Une page : derniers prix, comparaison base 100, prix/MM7, volatilité 30 jours.
- Filtres par actif et dates ; export CSV de la sélection.
- Démonstration synthétique sans clé et tests sans appel réseau.

Pas de prédiction, RSI, régression, bandes de Bollinger, corrélations ou détection
de motifs dans cette V1. Pas de planification automatique ni de reprise HTTP automatique.

## Installation et démonstration

Python 3.10 ou supérieur. Depuis le dossier du dépôt, sous PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
crypto-etl demo
streamlit run dashboard/app.py
```

Sous Linux : `source .venv/bin/activate`, puis les mêmes commandes.
L'installation nécessite Internet ; les tests et la démo fonctionnent sans API.
Le dashboard démarre en mode **démonstration synthétique**, avec une bannière explicite.
Une base neuve contient 270 observations synthétiques (90 jours × 3 actifs).
Les anciennes lignes ne sont pas supprimées : une base déjà utilisée peut en contenir plus.

## Collecte réelle

Créer une clé Demo chez [CoinGecko](https://www.coingecko.com/en/api), puis :

```powershell
$env:COINGECKO_API_KEY="votre_cle"
crypto-etl update
```

Sous Linux : `export COINGECKO_API_KEY='votre_cle'`.
Désactiver « Démonstration synthétique » dans le dashboard pour lire les données réelles.
La collecte authentifiée reste à valider avec une vraie clé ; la démo n'est pas une preuve
de collecte réelle. Les données synthétiques ne doivent pas être présentées comme réelles.

| Variable | Valeur par défaut |
|---|---|
| COINGECKO_API_KEY | vide ; obligatoire pour update |
| CRYPTO_CURRENCY | usd |
| CRYPTO_DAYS | 90 (1 à 365) |
| CRYPTO_DATA_DIR | data |

`.env.example` décrit les variables mais `.env` n'est pas chargé automatiquement.
Les chemins sont relatifs au dossier d'exécution ; utiliser toujours le même dossier.
Les bases sont séparées : `data/demo.db` et `data/market.db`.

## Fonctionnement et règles

1. Le client appelle `/coins/{id}/market_chart` avec `interval=daily`, un timeout de 30 s
   et la clé dans l'en-tête `x-cg-demo-api-key`. Une tentative par actif. En cas de panne
   ou HTTP 429, attendre puis relancer manuellement. Aucun secret dans les erreurs affichées.
2. Le pipeline archive les JSON décodables, aligne prix/capitalisations/volumes par timestamp
   exact et retient le dernier prix valide de chaque jour UTC terminé. Le jour courant est exclu.
3. Un prix doit être positif et fini ; sinon le point est rejeté. Volume/capitalisation
   négatifs ou non finis deviennent NULL. Les jours absents ne sont pas interpolés.
4. SQLite utilise la clé `(coin_id, vs_currency, date_utc)`. L'upsert insère une date nouvelle
   ou actualise une date existante. Une crypto en échec conserve ses anciennes données.
5. Le dashboard lit uniquement SQLite et recalcule les indicateurs ; aucun appel API au filtrage.

`pipeline_runs` conserve un statut success/partial/failed et le nombre de lignes traitées,
y compris celles actualisées. Les archives JSON restent locales et ne sont pas publiées.

## Les quatre indicateurs

| Indicateur | Formule / règle |
|---|---|
| Variation quotidienne (%) | `100 × (prix / prix du jour précédent − 1)` |
| Moyenne mobile 7 jours | moyenne de 7 prix consécutifs, fenêtre complète |
| Volatilité 30 jours (%) | écart-type de 30 rendements quotidiens, `ddof=1`, non annualisé |
| Base 100 | `100 × prix / premier prix disponible de la sélection` |

Un calendrier quotidien matérialise les jours absents. Les calculs sont séparés par actif
et devise. La MM7 et la volatilité sont calculées avant le filtre de dates ; la base 100
est recalculée sur la sélection. La volatilité exige 31 prix pour 30 rendements.
Les premières valeurs indisponibles restent vides. Si un actif commence plus tard,
sa base 100 repose sur une date différente : vérifier les périodes avant de comparer.

## Choix techniques et limites

Python regroupe extraction et analyse ; pandas suffit pour les calculs. NumPy est une
dépendance indirecte de pandas, sans import direct dans le projet. SQLite évite un serveur
pour ce petit volume local. Streamlit et Plotly permettent une interface simple en Python.

Les snapshots CoinGecko ne sont pas des clôtures officielles. Le volume observé sur 24 h
ne doit pas être additionné entre snapshots. Les valeurs peuvent manquer ou être révisées.
Les indicateurs décrivent le passé et ne prédisent pas les prix. Aucun backtest ou ordre de trading.
Pas d'authentification multi-utilisateur, de cache, de déploiement cloud ou de gestion avancée
des accès concurrents. Le tableau est calculé en mémoire. Dépendances bornées, sans lockfile.

Documentation CoinGecko consultée pour le client :
[historique](https://www.coingecko.com/learn/download-bitcoin-historical-data) et
[authentification](https://support.coingecko.com/hc/en-us/articles/4538879945625-API-key-can-I-store-the-key-in-my-headers).
Les limites de l'offre doivent être revérifiées avant utilisation réelle.

## Tests et apprentissage

```text
pytest
ruff check .
ruff format --check .
```

Les tests couvrent nettoyage, jours absents, calculs simples, upserts, erreurs HTTP et
conservation des données lors d'un échec partiel. Le test Streamlit couvre l'état vide
et les filtres. La CI exécute les contrôles sous Windows/Linux, Python 3.10/3.12.
Elle ne collecte aucune donnée. Voir [le parcours en quatre semaines](docs/developpement.md).

## Présentation CV (après appropriation du projet)

**Key Crypto - Pipeline de données et dashboard crypto**
Python · pandas · API REST · SQLite · Streamlit · Plotly

- Collecte et nettoyage des données quotidiennes de trois cryptomonnaies.
- Stockage SQL avec mises à jour sans doublons et tests des traitements essentiels.
- Dashboard interactif de comparaison des performances et de la volatilité.

Le code a été construit avec assistance IA ; comprendre et savoir modifier ses fonctions
fait partie du travail personnel d'apprentissage. Aucun volume de données réelles non mesuré
n'est revendiqué sur le CV.

## Historique

La version avancée reste accessible via le tag `version-avancee-archive`.
Son ancien guide PDF est dans [docs/archive](docs/archive/README.md) et **ne décrit pas cette V1**.
Secrets, bases, archives brutes et environnement virtuel sont exclus de Git.
