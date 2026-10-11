# Observatoire crypto — ETL Python local

[Dépôt GitHub](https://github.com/Clemriv-prog/crypto-etl-dashboard) · [Guide technique et préparation aux entretiens (PDF)](docs/Guide_entretien_crypto_etl.pdf)

Bitcoin, Ethereum et Solana : API CoinGecko → pandas → SQLite → indicateurs → Streamlit/Plotly.
Le dashboard lit exclusivement SQLite. Une collecte manuelle fusionne les 180 derniers jours.
Le projet est destiné à l'analyse descriptive et à la présentation d'une chaîne de données.

## Installation (Python 3.10 ou supérieur)

Depuis le dossier du projet, sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
crypto-etl demo
streamlit run dashboard/app.py
```

Sous Linux : remplacer l'activation par `source .venv/bin/activate`.
Le téléchargement des dépendances nécessite Internet. Les tests et la démonstration n'en ont pas besoin.
Le dashboard démarre en mode **démonstration synthétique**, explicitement signalé.
Ses valeurs sont déterministes et fabriquées ; elles ne représentent pas des cours réels.
La base `data/demo.db` et les archives `data/raw-demo/` sont distinctes des données réelles.

![Dashboard en mode démonstration synthétique](docs/dashboard-demo.png)

Validation locale : 22 tests réussis, Ruff et formatage validés ; démonstration chargée
avec 540 observations (180 jours × 3 actifs). Les interactions ont aussi été vérifiées
dans le navigateur. Aucune collecte réelle effectuée sans clé API.

## Collecte réelle et configuration

Créer une clé Demo depuis [CoinGecko](https://www.coingecko.com/en/api).
Ne jamais mettre la clé dans le code, une URL ou un commit.

```powershell
$env:COINGECKO_API_KEY="votre_cle"
$env:CRYPTO_CURRENCY="usd"
$env:CRYPTO_DAYS="180"
crypto-etl update
streamlit run dashboard/app.py
```

Linux : `export COINGECKO_API_KEY='votre_cle'`, puis les mêmes commandes.
Dans le dashboard, désactiver « Démonstration synthétique » pour lire `data/market.db`.
`.env.example` décrit les variables ; aucun fichier `.env` n'est chargé automatiquement.
`CRYPTO_DATA_DIR` configure le dossier local (par défaut `data`, relatif au dossier d'exécution).
Toujours exécuter les commandes depuis le même dossier ou définir un chemin absolu.

## Données et garanties

`GET /coins/{id}/market_chart`, paramètres `vs_currency`, `days`, `interval=daily` ;
clé dans `x-cg-demo-api-key`, timeout 30 s, quatre tentatives au maximum sur erreur réseau,
429 ou serveur. `Retry-After` numérique ou date HTTP est respecté ; sinon délai exponentiel.
Les erreurs de requête/authentification sont immédiates. Les messages externes ne sont pas
recopiés dans les logs afin d'éviter de divulguer une clé.

Chaque réponse JSON décodable est archivée avant transformation dans un dossier identifié
par l'exécution. Une réponse illisible ne peut pas être archivée comme JSON.
Pour rejouer une archive : charger le fichier avec `json.loads`, appeler `transform(payload,
coin, currency, days, now=...)` avec la date UTC de collecte d'origine, puis `upsert`.

Les trois séries sont jointes par timestamp exact, jamais par position. À timestamp dupliqué,
la dernière occurrence de chaque série gagne. Pour chaque jour, le dernier snapshot ayant un
prix valide est conservé, sans reprendre le volume d'un autre timestamp. Le jour UTC courant
et les dates futures sont exclus. La fenêtre conservée couvre les `days` jours terminés.
Prix non fini, nul ou négatif : rejet. Volume/capitalisation invalide : SQL NULL signalé.
Aucune interpolation. Les jours manquants, valeurs manquantes et variations absolues > 50 %
sont comptabilisés ; une forte variation reste dans la base.

La clé primaire `(coin_id, vs_currency, date_utc)` permet un upsert transactionnel par crypto.
Relancer une collecte ne duplique pas les lignes et corrige les prix révisés. Une crypto en
échec conserve ses données précédentes ; `pipeline_runs` indique success, partial ou failed.
Une interruption brutale peut laisser un run « running » : vérifier les logs puis relancer.
Les anciennes lignes hors fenêtre ne sont pas supprimées : l'historique local s'enrichit.

CoinGecko fournit des observations agrégées, pas une clôture officielle de marché.
Le volume sur 24 h est un snapshot et ne doit pas être additionné entre observations.
L'offre Demo limite l'historique accessible à 365 jours (documentation vérifiée le 11/10/2026).
Sources : [historique](https://www.coingecko.com/learn/download-bitcoin-historical-data),
[authentification](https://support.coingecko.com/hc/en-us/articles/4538879945625-API-key-can-I-store-the-key-in-my-headers),
[snapshots et OHLC](https://support.coingecko.com/hc/en-us/articles/23126953719321-Why-is-there-a-discrepancy-between-the-close-price-of-a-token-on-the-coins-id-market-chart-interval-daily-endpoint-and-the-OHLC-prices-for-the-same-token).

## Indicateurs

Chaque crypto/devise utilise un calendrier quotidien explicite, avec trous conservés.

| Mesure | Formule / règle |
|---|---|
| Variation 1 jour (%) | `100 × (P(t)/P(t−1)−1)` |
| Variation 7 jours (%) | `100 × (P(t)/P(t−7)−1)`, date exacte |
| Moyennes 7/30 jours | moyenne, fenêtre complète sans prix manquant |
| Volatilité 30 jours (%) | écart-type des 30 rendements 1 jour en %, `ddof=1`, non annualisé |
| Base 100 | `100 × P / premier prix disponible de la sélection` |
| Performance sélection (%) | `base_100 final − 100` |
| Drawdown (%) | `100 × (P / maximum cumulé de la sélection − 1)` |

Les indicateurs historiques sont calculés avant le filtre de dates ; base 100 et drawdown
sont recalculés après filtrage. Les résultats indisponibles restent nuls. La volatilité
nécessite 31 prix consécutifs. Le tableau indique la date du dernier prix de chaque actif ;
si leurs dates diffèrent, les performances couvrent des observations différentes.

## Tendances et motifs descriptifs

La vue « Analyse d’une crypto » ajoute :

| Mesure | Définition |
|---|---|
| Tendance 30 jours | régression linéaire du prix sur 30 dates consécutives |
| Pente (%/jour) | `100 × pente / prix moyen de la fenêtre` |
| R² | `1 − somme des résidus² / somme des écarts à la moyenne²` ; 0 pour prix constant |
| Classe de tendance | haussière si pente > 0,1 %/jour et R² ≥ 0,5 ; baissière si pente < −0,1 et R² ≥ 0,5 ; sinon sans tendance linéaire nette |
| RSI 14 | `100 − 100/(1 + gain moyen / perte moyenne)`, moyennes **simples** de 14 variations ; différent du RSI de Wilder |
| Bandes de Bollinger | moyenne 20 jours ± 2 écarts-types des prix (`ddof=1`) |
| Momentum 30 jours | `100 × (prix / prix à la date exacte 30 jours avant − 1)` |
| Canal précédent | minimum et maximum des 20 prix quotidiens précédents, jour courant exclu |
| Cassure | prix strictement supérieur/inférieur au canal précédent |
| Croisement | différence MM7−MM30 passant de ≤0 à >0, ou de ≥0 à <0 |

RSI = 100 si seuls des gains existent, 0 si seules des pertes existent, 50 si tous les
prix de la fenêtre sont constants. Les premières fenêtres et celles comportant des trous
restent indisponibles. Un croisement est un événement ponctuel, pas un état permanent.
Le canal porte sur les snapshots quotidiens, pas sur les extrêmes intrajournaliers.

Ces calculs utilisent seulement les données présentes et passées ; un test vérifie que
l'ajout de prix futurs ne change pas les résultats antérieurs. Les seuils de tendance,
RSI 30/70 et cassures sont des repères descriptifs, sans backtest ni probabilité de réussite.
Un R² élevé décrit un ajustement passé ; il ne prouve pas la poursuite d'une tendance.
Il n'y a pas de reconnaissance de chandeliers, doubles sommets ou tête-épaules dans cette
version. Les courbes synthétiques de démonstration ont été fabriquées avec une sinusoïde :
leurs motifs ne constituent pas une observation de marché.

## Vérification

```text
ruff check .
ruff format --check .
pytest
crypto-etl demo
```

Les tests injectent des réponses HTTP simulées et utilisent des bases temporaires ; aucune
clé ni réseau. La CI GitHub Actions vérifie Python 3.10/3.12 sous Windows/Linux ; elle ne
collecte aucune donnée. Voir [le parcours pédagogique](docs/developpement.md) et
[la procédure de planification](docs/planification.md).

## Git et publication

Le dépôt est initialisé localement. `git add` prépare les fichiers, `git commit` crée un
jalon ; `git status` vérifie les modifications et `git log --oneline` montre les étapes.
L'identité d'auteur est passée aux commits avec `git -c user.name=... -c user.email=...` ;
aucune configuration globale n'est modifiée. `.gitignore` exclut clés, données, bases,
logs et environnement virtuel. Le code a été publié sur accord explicite dans le dépôt
public `Clemriv-prog/crypto-etl-dashboard`, branche `main`.
Pour contribuer : cloner le dépôt, installer le projet et créer une branche dédiée.
Vérifier `git diff --cached`, `git ls-files` et l'absence de secret avant chaque publication.
Le guide PDF contient les explications, les formules, les limites, les exercices et une
annexe des sources ; ses résultats de tests sont datés et ne remplacent pas l'onglet Actions.
