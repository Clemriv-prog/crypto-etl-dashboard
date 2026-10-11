# Observatoire crypto : comprendre, expliquer et défendre le projet

Guide technique et préparation aux entretiens - édition du 11 octobre 2026.
Projet Python local : CoinGecko, pandas, SQLite, Streamlit, Plotly et pytest.
État du code étudié : commit 5115172, complété par la documentation de livraison.

Dépôt public : https://github.com/Clemriv-prog/crypto-etl-dashboard . Le code est publié sur la branche main avec son historique local. Le guide décrit l'état vérifié localement ; consulter l'onglet Actions pour les résultats distants les plus récents.

## 1. Lire ce guide et situer le niveau de preuve

Ce document sert à comprendre les décisions du projet, à montrer le code pertinent et à répondre aux objections. Il ne suffit pas de mémoriser des phrases : refaire les exemples, lancer les tests et modifier une fonction constitue une préparation plus solide. Une annexe reproduit le code source avec des numéros de ligne pour travailler sans connexion.

Le projet est un portfolio de traitement de données financières. Il met en œuvre une chaîne de données locale de bout en bout. Il ne constitue ni une plateforme de trading, ni un modèle prédictif, ni une expérience de production à grande échelle. La version livrée possède un client réel CoinGecko, mais aucune collecte réelle authentifiée n'a été validée dans cette session faute de clé API. Les tests utilisent des réponses simulées et la démonstration des prix synthétiques.

La dernière vérification locale a exécuté 22 cas de test avec succès. Ruff et son contrôle de formatage passent également. La matrice GitHub Actions est définie pour Windows/Linux et Python 3.10/3.12 ; sa présence ne prouve pas qu'une exécution distante a déjà réussi. Les 540 lignes de démonstration représentent 180 jours sur trois actifs, pas un volume de production ni une mesure de performance.

Parcours rapide avant entretien : lire les chapitres 2, 3, 8, 11, 15 et 19. Parcours technique : suivre les modules dans l'ordre config, client, transform, quality, storage, pipeline, indicators, trends, dashboard. Parcours de révision : exécuter les exercices et répondre aux questions sans regarder les propositions de réponse.

## 2. Le besoin et la présentation en une minute

Le besoin est de récupérer régulièrement un historique de prix, de contrôler sa qualité, de conserver une base cohérente et de comparer plusieurs actifs. Des appels API directement dans un graphique seraient insuffisants : ils mélangeraient réseau, calcul et affichage, consommeraient le quota à chaque filtre et rendraient les erreurs difficiles à reproduire.

Le périmètre initial comprend Bitcoin, Ethereum et Solana, identifiés par bitcoin, ethereum et solana. La devise est configurable, avec USD par défaut. Chaque collecte récupère les 180 derniers jours et conserve une observation par jour UTC terminé. L'utilisateur peut analyser un actif, comparer les performances et exporter sa sélection.

Proposition de pitch, à adapter après appropriation : « J'ai réalisé avec assistance IA un projet Python qui transforme des réponses CoinGecko en données quotidiennes analysables. Le pipeline contrôle les timestamps et les valeurs, archive les réponses et charge SQLite par upsert. Le dashboard lit uniquement la base locale. J'ai travaillé les cas difficiles : jours manquants, données révisées, limites HTTP et échecs partiels. Des tests hors réseau vérifient les calculs et la non-destruction des données. »

Pour une présentation de trois minutes, consacrer 30 secondes au besoin, 45 secondes au flux de données, 45 secondes à une difficulté réelle, 30 secondes aux tests et 30 secondes aux limites. La difficulté la plus démonstrative est la différence entre sept lignes et sept jours lorsque l'historique contient un trou.

## 3. Architecture et séparation des responsabilités

Le flux logique est : commande CLI -> configuration -> client API -> archives JSON -> transformation/qualité -> SQLite -> indicateurs -> dashboard. Le dashboard ne déclenche pas le pipeline. L'actualisation des données et la consultation sont donc deux opérations indépendantes.

L'extraction récupère un objet JSON décodable. La transformation vérifie sa structure, convertit les séries et applique les règles métier. Le chargement écrit des lignes validées dans SQLite. Les indicateurs sont calculés à la lecture dans le dashboard, et ne sont pas stockés dans des colonnes SQL. Une correction de prix est ainsi répercutée au prochain calcul sans maintenance d'une table d'indicateurs.

L'archive brute et la base ne sont pas deux copies équivalentes : la première conserve la réponse décodable avant nettoyage, la seconde représente l'état courant validé par date. Une archive rend possible un rejeu et une enquête ; la base facilite les requêtes et l'unicité. Le système n'est pas un entrepôt de données historisant toutes les révisions.

config.py contient les paramètres ; client.py traite HTTP ; transform.py normalise ; quality.py résume les anomalies ; storage.py porte SQL ; pipeline.py coordonne ; cli.py expose les commandes ; demo.py fabrique des données ; indicators.py gère le calendrier ; trends.py ajoute les repères descriptifs ; dashboard/app.py présente les résultats.

Cette séparation permet d'injecter une fonction fetch dans le pipeline et une session simulée dans le client. Une fonction de calcul reçoit un tableau, pas une clé API ni un objet Streamlit. Le bénéfice concret est de tester les rendements à partir de trois prix sans serveur ni réseau.

## 4. Installation, packaging et configuration

Le fichier pyproject.toml décrit le paquet crypto-etl-local, les dépendances et le point d'entrée crypto-etl. Les sources se trouvent dans src/crypto_etl. L'installation éditable, python -m pip install -e ".[dev]", rend les modifications locales du paquet accessibles sans reconstruire manuellement une distribution à chaque changement.

Créer un environnement virtuel évite de mélanger les versions de ce projet avec celles d'autres logiciels. Sous PowerShell : python -m venv .venv, puis .venv\Scripts\Activate.ps1. Sous Linux : source .venv/bin/activate. Installer ensuite le paquet et lancer crypto-etl demo, puis streamlit run dashboard/app.py. Si PowerShell refuse l'activation, utiliser directement .venv\Scripts\python.exe et .venv\Scripts\streamlit.exe, sans modifier inutilement une politique globale.

Config est une dataclass figée. Ses attributs par défaut comprennent days=180, currency=usd, attempts=4, timeout=30 et l'URL Demo. frozen=True empêche de réassigner un champ après création ; ce n'est pas un mécanisme de chiffrement. Le champ api_key est exclu de repr pour limiter sa présence dans les affichages accidentels.

load_config lit COINGECKO_API_KEY, CRYPTO_CURRENCY, CRYPTO_DAYS et CRYPTO_DATA_DIR. La devise est mise en minuscules. Le nombre de jours doit être compris entre 1 et 365. La validation du code accepte une devise alphabétique, sans vérifier la liste réelle des devises CoinGecko : une devise inexistante sera refusée par l'API. Une chaîne non convertible en entier échoue dès le chargement.

Le fichier .env.example est un exemple documentaire. Il n'est pas chargé automatiquement : copier ce fichier en .env ne suffit donc pas. Dans PowerShell, utiliser $env:COINGECKO_API_KEY="..." ; dans un shell Linux, export COINGECKO_API_KEY='...'. Les chemins relatifs dépendent du dossier d'exécution. Un planificateur doit fixer son dossier de travail ou utiliser CRYPTO_DATA_DIR absolu.

Les versions sont bornées par des plages, et non verrouillées dans un lockfile. Cela facilite les mises à jour compatibles mais ne garantit pas une reproduction binaire exacte. Pour renforcer la reproductibilité, ajouter ultérieurement un verrouillage des versions et une stratégie de mise à jour contrôlée.

## 5. API CoinGecko et contrat de données

Le client appelle GET https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart. Les paramètres sont vs_currency, days et interval=daily. L'authentification Demo utilise l'en-tête x-cg-demo-api-key. Un GET ne signifie pas qu'il est gratuit en quota : chaque requête peut compter selon l'offre du fournisseur.

La réponse attendue contient prices, market_caps et total_volumes. Chaque série est une liste de paires [timestamp_en_millisecondes, valeur]. La présence de ces trois listes et la longueur de chaque paire sont contrôlées par validate_payload. Une liste vide est structurellement acceptable, puis conduit à une absence de données lors du contrôle métier.

Exemple pédagogique : prices=[[1704067200000,100],[1704153600000,105]], market_caps=[[1704067200000,1000]], total_volumes=[[1704153600000,80]]. Le prix du premier jour possède une capitalisation mais pas de volume. Celui du second possède un volume mais pas de capitalisation. Une jointure par position attribuerait des valeurs au mauvais jour.

La fonction fetch renvoie le JSON décodable ; la vérification de structure est exécutée par transform. Le pipeline archive donc aussi un objet JSON mal structuré avant de rejeter la série. Ce choix facilite le diagnostic. Un corps HTTP qui ne peut pas être décodé en JSON n'est pas conservé sous forme d'archive JSON dans cette version.

Un snapshot quotidien agrégé n'est pas une clôture officielle d'une place de marché. Les marchés crypto fonctionnent en continu et les données CoinGecko peuvent être nettoyées ou révisées. Le volume observé couvre les 24 heures associées au snapshot ; additionner plusieurs volumes glissants n'est pas équivalent à une quantité négociée sur une période disjointe.

L'offre Demo et ses limites doivent être vérifiées dans la documentation avant une utilisation réelle. Le projet retient une fenêtre compatible avec la limite de 365 jours documentée lors du développement. Il ne fixe pas un quota par minute comme vérité permanente : les offres commerciales peuvent évoluer.

## 6. Résilience HTTP, délais et erreurs

Client accepte une session HTTP et une fonction sleep injectables. En usage normal, requests.Session réutilise une session ; dans les tests, Mock remplace le réseau et l'attente. Le paramètre timeout=30 est transmis à chaque requête. Avec requests, ce timeout ne constitue pas une borne absolue sur toute la durée du pipeline : les tentatives et les attentes peuvent prolonger l'exécution.

Le code effectue quatre tentatives au maximum. Il réessaie après RequestException, HTTP 429 et les réponses serveur. Avec l'absence de Retry-After, les trois pauses précédant la quatrième tentative sont 1, 2 et 4 secondes. Le compteur attempts désigne le nombre total d'appels, pas le nombre de reprises supplémentaires.

Retry-After peut être un nombre de secondes ou une date HTTP. La fonction retry_delay transforme la valeur en attente positive ; si le parsing échoue, elle utilise le délai exponentiel. La version actuelle respecte une attente longue demandée par le serveur et n'introduit pas de jitter. Elle n'a pas non plus de deadline globale. Ces choix sont acceptables pour un petit outil manuel, mais doivent être discutés pour un service permanent.

HTTP 400, 401 et 403 entraînent un arrêt immédiat pour la crypto concernée. Répéter une clé invalide ne la rendra pas valide. Un JSON illisible échoue également immédiatement. Les autres cryptos continuent à être traitées, car le pipeline isole les erreurs par actif.

Les exceptions externes peuvent contenir des URLs ou des secrets. Le pipeline conserve seulement le type d'erreur et le nom de la crypto dans les logs. Cela réduit le risque de fuite mais rend le diagnostic moins précis. Une évolution serait de définir des exceptions métier avec code HTTP expurgé, tout en conservant l'absence de clé dans les messages.

## 7. Nettoyage : suivre une observation jusqu'à sa date

transform commence par valider la structure. Il détermine le jour UTC courant, puis une borne de départ égale à aujourd'hui moins days. Les tests peuvent fournir now pour rendre cette borne indépendante de l'horloge réelle. Une date sans fuseau fournie à now est interprétée comme UTC ; une date avec fuseau est convertie en UTC.

Chaque série devient un DataFrame contenant source_timestamp et sa valeur métier. Les timestamps sont convertis en nombres, les valeurs non convertibles sont retirées, puis les doublons par timestamp sont résolus en conservant la dernière occurrence de la série. La concaténation sur l'index des timestamps aligne les trois séries par clé exacte.

pd.to_datetime utilise unit='ms', utc=True et errors='coerce'. Un timestamp non représentable devient une date manquante. Après conversion, le fuseau est retiré pour stocker un jour normalisé sans ambiguïté : le champ s'appelle date_utc et sa convention reste UTC. Retirer le fuseau après conversion n'est pas la même chose que traiter une heure locale comme si elle était UTC.

Les valeurs sont converties en nombres. isfinite exclut NaN et les infinis. Prix strictement positif : sinon rejet de l'observation. Capitalisation et volume non négatifs : sinon valeur manquante conservée. Un volume égal à zéro est autorisé ; un prix égal à zéro ne l'est pas.

La fenêtre est fermée à gauche et ouverte à droite : start <= date < today. Le jour courant, encore incomplet, est exclu. Les lignes sont triées par timestamp source, puis la dernière ligne ayant un prix valide est retenue pour chaque jour. Si le dernier point du jour a un prix invalide, un point antérieur valide peut être retenu. Les autres séries ne sont pas automatiquement reportées depuis un autre timestamp.

L'absence de prix interdit de fabriquer une observation par interpolation. Ce choix évite de créer des rendements artificiellement lisses. Il distingue une information inconnue d'une information égale à zéro, ce qui aura des conséquences directes sur les fenêtres de calcul.

## 8. Bilan qualité et limites de mesure

quality_report construit la liste de toutes les dates attendues dans la fenêtre. La différence entre ce calendrier et les dates observées donne missing_days. La qualité ne se limite pas au nombre total de lignes : deux séries de 180 lignes peuvent couvrir des jours différents ou contenir des doublons.

Le bilan contient accepted, rejected, duplicate_timestamps, excluded_current_or_future, missing_days, missing_market_cap, missing_volume et large_changes. Une variation absolue strictement supérieure à 50 % est signalée sans supprimer le prix. Un événement exceptionnel n'est pas nécessairement une erreur de données.

Les compteurs ne forment pas une partition parfaite de la réponse brute. Les doublons sont comptés séparément dans chaque série et peuvent compter le même timestamp plusieurs fois. Les timestamps non numériques sont retirés avant le calcul de rejected. Les rejets sont évalués avant le filtre temporel ; certaines lignes rejetées peuvent donc être hors de la fenêtre utile. Il faut connaître ces nuances pour ne pas présenter le bilan comme un audit exhaustif de chaque élément JSON.

Le dashboard affiche les rapports de la dernière exécution, pas une agrégation historique complète. Des jours absents d'une collecte peuvent encore exister dans SQLite grâce à une collecte précédente. Le rapport de collecte et l'état global de la base répondent donc à deux questions différentes.

Améliorations possibles : compter séparément les timestamps invalides, les doublons intra-journaliers, les lignes hors fenêtre et les valeurs non finies ; définir un schéma de rapport versionné ; agréger la qualité de toute la base ; comparer les dates de fraîcheur par actif et par devise.

## 9. Modèle SQL, upsert et idempotence

daily_market_data contient coin_id, vs_currency, date_utc, source_timestamp, price, market_cap, volume_24h et collected_at. La clé primaire composite est (coin_id, vs_currency, date_utc). Une date seule n'est pas unique, puisque trois actifs et plusieurs devises peuvent partager le même jour.

source_timestamp conserve la précision du point retenu, tandis que date_utc identifie le jour métier. collected_at enregistre la collecte ayant fourni la version actuelle de la ligne. Les dates UTC sont stockées en texte ISO et les timestamps source en entier millisecondes. Les prix sont des REAL SQLite : adaptés à cette analyse descriptive, mais pas à une comptabilité monétaire exigeant un arrondi décimal exact.

INSERT ... ON CONFLICT ... DO UPDATE insère une ligne nouvelle ou remplace les attributs de la ligne existante. Si le prix d'un jour passe de 100 à 101 dans une collecte ultérieure, la base contient 101. Rejouer la même collecte ne crée pas de doublon. Les métadonnées collected_at changent toutefois : l'idempotence concerne l'état métier et l'unicité, pas l'identité bit à bit de chaque champ.

Le chargement d'une crypto est transactionnel : toutes ses lignes préparées sont exécutées dans le même bloc with db. Un échec SQL annule ce lot. La transaction ne couvre pas les trois actifs ensemble : une réussite Bitcoin est conservée même si Ethereum échoue ensuite. C'est un choix volontaire de disponibilité partielle.

Les valeurs sont liées avec des placeholders SQL, pas interpolées dans une chaîne. Cela évite les erreurs d'échappement et réduit les risques d'injection. Les contraintes CHECK contrôlent prix et valeurs non négatives, mais la validation Python reste importante. Le schéma ne possède pas de contrainte UNIQUE sur source_timestamp : plusieurs jours ne devraient pas partager un timestamp valide, mais la clé métier est la date.

SQLite convient au faible volume local et évite un serveur. La version actuelle ne configure ni WAL, ni stratégie élaborée de concurrence, ni migrations. Le context manager sqlite3 gère commit/rollback ; il ne ferme pas à lui seul explicitement la connexion. Le wrapper actuel ne comporte pas de finally db.close(), point à améliorer pour un usage long ou très fréquent.

## 10. Exécutions, archives et échec partiel

pipeline_runs enregistre run_id, started_at, ended_at, status, rows_processed et details. Un UUID hexadécimal sert de nom de dossier d'archive et d'identifiant de ligne. Le statut initial running est validé avant la collecte. La fin renseigne success, partial ou failed selon le nombre de cryptos chargées avec succès.

Le pipeline crée raw/<run_id>/<coin>.json pour les collectes réelles et raw-demo pour la démonstration. L'archive est écrite avant transformation, ce qui conserve la réponse pour comprendre un rejet. Il n'y a pas de transaction distribuée entre fichiers JSON et SQLite : un fichier peut être présent même si le chargement SQL échoue. Ce n'est pas un défaut caché ; c'est une propriété à documenter.

rows_processed mesure le nombre de lignes validées chargées, y compris les upserts de lignes déjà existantes. Ce n'est pas un compteur de nouvelles lignes insérées. Une exécution de 540 lignes traitées peut ne créer aucune nouvelle ligne si elle met seulement à jour des dates déjà présentes.

Si Ethereum échoue, ses dernières données valides restent en base. Le statut global devient partial si au moins une autre crypto a réussi. Aucun DELETE n'est exécuté. Une observation devenue invalide ou absente dans une nouvelle réponse ne supprime donc pas automatiquement une ligne antérieure ; seule une nouvelle ligne valide la remplace.

Une interruption brutale peut laisser un run running. Un disque plein peut empêcher l'archive ou le bilan final ; le code ne promet pas une journalisation parfaite malgré la panne du support de stockage. Pour aller plus loin, ajouter expiration des runs inachevés, erreurs métier expurgées, alertes et politique de rétention des archives.

## 11. Calendrier quotidien et calculs fondamentaux

indicators groupe d'abord par coin_id et vs_currency. Il trie les dates et applique asfreq('D') : un jour absent devient une ligne dont le prix est NaN. Les identifiants sont ensuite réattribués pour que les lignes de calendrier restent associées à la bonne série. Les calculs ne mélangent jamais Bitcoin et Ethereum ni USD et EUR.

Variation quotidienne : 100 * (P(t)/P(t-1)-1). Avec 100 puis 105, elle vaut 5 %. Avec 105 puis 100, elle vaut environ -4,7619 %, et non -5 %. Les rendements simples ne s'additionnent pas exactement : deux hausses de 10 % produisent 21 % de performance, car 1,1 * 1,1 = 1,21.

Variation hebdomadaire : 100 * (P(t)/P(t-7)-1). Sur un calendrier quotidien, shift(7) pointe vers la date exacte sept jours avant. Si le prix de cette date manque, le résultat reste NaN. Un trou intermédiaire n'invalide pas nécessairement ce rendement de point à point si les deux prix extrêmes existent ; il invalide en revanche les fenêtres exigeant tous les points.

Moyenne mobile n jours : somme des n prix divisée par n, avec min_periods=n. Les prix 100,101,102,103,104,105,106 donnent une MM7 de 103 au septième jour. Les six premiers jours restent indisponibles. Une seule valeur manquante dans une fenêtre empêche sa moyenne complète.

La moyenne mobile est calculée avant le filtre d'affichage. Si l'utilisateur sélectionne une période commençant en juin et que mai est disponible, la MM30 du début juin peut utiliser les derniers jours de mai. Filtrer d'abord créerait artificiellement 29 résultats indisponibles au début de chaque sélection.

La performance de sélection et la base 100 sont calculées après le filtre. Le premier prix disponible devient 100 ; un dernier prix de 120 comparé à un premier de 100 donne une base finale 120 et une performance de 20 %. Si un actif commence plus tard faute de données, il possède une date de référence différente : la comparaison n'est alors pas parfaitement synchronisée.

## 12. Risque : volatilité et drawdown

La volatilité sur 30 jours est l'écart-type des 30 derniers rendements quotidiens exprimés en pourcentage. L'écart-type échantillonnal utilise ddof=1 : somme des écarts au rendement moyen au carré, divisée par n-1, puis racine carrée. Il nécessite donc 31 prix consécutifs pour produire 30 rendements valides.

Exemple court pour comprendre ddof : pour les rendements 1 %, 2 %, 3 %, la moyenne est 2 %. Les écarts sont -1,0,1 point de pourcentage ; leur somme des carrés est 2. En divisant par 3-1, puis en prenant la racine, l'écart-type vaut 1 point de pourcentage. Avec ddof=0, il serait environ 0,8165.

La volatilité de ce projet n'est pas annualisée. Multiplier par racine(365) serait une convention supplémentaire avec des hypothèses sur les rendements ; ce n'est pas appliqué ici. Volatilité élevée ne signifie pas automatiquement baisse : une série en forte hausse peut aussi être volatile. Faible volatilité ne prouve pas l'absence de risque extrême.

Le drawdown vaut 100 * (prix / maximum cumulé - 1). Pour 100,120,90, les drawdowns sont 0 %,0 %,-25 %. Pour revenir de 90 à 120 après cette perte, il faut une hausse de 33,333 %, et non de 25 %. La valeur présentée à la fin est le drawdown courant ; ce n'est pas le maximum drawdown de toute la période.

Le maximum est recalculé sur la période sélectionnée. Un sommet avant le début choisi n'est pas utilisé. Sur des dates de prix manquant, le résultat est manquant ; lorsque les prix reprennent, le maximum cumulé des observations disponibles reste la référence. Le projet n'estime pas de VaR, de CVaR, de bêta ni de risque de portefeuille.

## 13. Régression de tendance, pente et R²

Sur 30 prix quotidiens consécutifs, trends.py ajuste une droite prix = a + b*x où x vaut 0,1,...,29. numpy.polyfit calcule les coefficients au moindre carré. La pente b représente une variation de prix par jour dans la devise de la série.

Pour comparer les actifs, la pente est divisée par le prix moyen de la fenêtre puis multipliée par 100. Une pente de 1 USD/jour sur un prix moyen de 144,5 USD correspond à environ 0,692 % du prix moyen par jour. Ce n'est ni un rendement composé quotidien ni une prévision : c'est une pente normalisée de l'ajustement historique.

R² = 1 - SSE/SST, où SSE est la somme des résidus au carré et SST la somme des écarts au prix moyen au carré. Une droite parfaite non constante produit R²=1. Un prix constant produit SST=0 ; le code retourne conventionnellement R²=0 afin d'éviter une division par zéro. Un R² élevé ne signifie pas que la prochaine observation suivra la droite.

La classe haussière exige une pente normalisée strictement supérieure à 0,1 %/jour et R² au moins égal à 0,5. La classe baissière exige une pente strictement inférieure à -0,1 et le même R² minimal. Sinon le libellé est « Sans tendance linéaire nette ». Moins de 30 prix consécutifs donne « Indisponible ».

Ces seuils sont des choix explicites de présentation, sans optimisation ni validation statistique de rentabilité. « Sans tendance linéaire nette » ne prouve pas l'absence de cycles, de rupture ou de structure non linéaire. Une évolution possible serait une régression sur logarithmes, une analyse de sensibilité des seuils et une validation hors échantillon, chacune clairement distinguée du code actuel.

## 14. RSI, bandes, momentum et motifs

Le RSI 14 utilise 14 variations quotidiennes : gain = max(diff,0), perte = max(-diff,0), puis leurs moyennes arithmétiques. RSI = 100 - 100/(1 + gain_moyen/perte_moyenne). Il faut 15 prix consécutifs. Cette implémentation utilise des moyennes simples ; elle ne reproduit pas le lissage récursif du RSI de Wilder fréquemment affiché ailleurs.

Si toutes les variations sont positives, le RSI vaut 100 ; si elles sont négatives, 0 ; si elles sont toutes nulles, 50. Avec un gain moyen de 2 et une perte moyenne de 1, le ratio vaut 2 et le RSI environ 66,667. Les lignes 30 et 70 servent de repères visuels et ne déclenchent aucun achat ni vente. Un RSI élevé peut rester élevé pendant une tendance longue.

Les bandes de Bollinger utilisent moyenne 20 jours plus ou moins deux écarts-types échantillonnaux des prix. Il s'agit de dispersion des niveaux de prix, contrairement à la volatilité calculée sur les rendements. Sortir d'une bande n'implique pas un retour certain à la moyenne. Les bandes ne sont pas des intervalles de confiance garantis à 95 %.

Le momentum 30 jours est un rendement de point à point entre les prix des dates t et t-30. Il exige les deux extrémités ; les trous intermédiaires ne le rendent pas nécessairement nul. Une pente de régression et ce momentum peuvent diverger : la première utilise tous les prix d'une fenêtre et le second seulement deux prix.

Le canal est le minimum et le maximum des 20 prix quotidiens précédents, calculés avec shift(1), puis rolling(20). Exclure le jour courant est essentiel : sinon le prix ne pourrait pas dépasser strictement un maximum qui l'inclut. Un nouveau sommet signifie prix > maximum précédent ; l'égalité n'est pas une cassure. Un nouveau creux suit la règle symétrique.

Un croisement haussier est détecté lorsque MM7-MM30 passe de <=0 à >0. Un croisement baissier passe de >=0 à <0. C'est un événement ponctuel : le jour suivant un croisement, rester au-dessus ne produit pas un nouveau croisement. Le calcul exige les moyennes actuelles et celles du jour précédent.

Ces motifs sont causaux : ils utilisent seulement des données présentes ou passées. Le test de préfixe vérifie que calculer 45 jours seuls donne les mêmes résultats que prendre les 45 premiers jours d'un calcul de 60 jours. Cela ne transforme pas les motifs en stratégie validée. Aucun double sommet, tête-épaules ou chandelier OHLC n'est reconnu dans cette version.

## 15. Dashboard, lecture et export

Streamlit exécute le script lors des interactions. Il lit SQLite, calcule les indicateurs, filtre la période et construit les graphiques Plotly. La version actuelle n'utilise pas de cache Streamlit : c'est simple et acceptable pour quelques centaines ou milliers de lignes, mais les lectures et calculs sont répétés. Aucune interaction n'appelle CoinGecko.

Le mode synthétique est activé par défaut, avec une bannière explicite. La base demo.db est distincte de market.db et les exports portent crypto-demo.csv ou crypto-coingecko.csv. Le choix d'une devise différente nécessite de collecter ou générer des lignes correspondant à cette devise ; le dashboard ne fait pas une conversion de change à la volée.

La vue d'ensemble présente les dernières observations disponibles dans la sélection, leurs dates, variations et performances. La vue d'analyse affiche une synthèse de tendance, prix et moyennes, bandes/canal, RSI, événements, volume, volatilité et drawdown. La comparaison trace les prix normalisés et un tableau par actif.

Les valeurs manquantes doivent rester visibles ou provoquer des interruptions de courbe, sans connexion artificielle de points éloignés. Un message indique les fenêtres insuffisantes. Il peut apparaître sur une période longue pourtant complète parce que ses premiers jours n'ont pas encore 30 rendements historiques. Il faut lire ce message comme un état de certains points, pas comme l'échec de toute la série.

L'export porte sur le tableau sélectionné, avec les indicateurs calculés et les éventuelles lignes calendaires manquantes. Il est destiné à l'analyse dans un autre outil. Il ne contient pas de clé API. Un filtre sur une crypto n'efface pas ses voisines de SQLite ; il ne fait que limiter le tableau en mémoire.

La capture historique du README montre la démonstration, pas des prix réels. L'interface utilise encore certains paramètres Streamlit dépréciés, notamment use_container_width. Ils fonctionnent dans l'environnement vérifié mais justifient une future mise à jour API avant une suppression par le fournisseur.

## 16. Démonstration, tests et niveau de confiance

demo.py crée une série déterministe combinant progression et sinusoïde. Des prix de base différents servent à illustrer l'intérêt de la normalisation. La date de fin suit le dernier jour UTC terminé, donc deux exécutions à des dates différentes ne produisent pas le même calendrier. Aucun appel HTTP ni secret n'est nécessaire.

tests/test_core.py vérifie quatre réponses mal formées, une réponse vide, l'alignement, les doublons, le dernier point valide du jour, les valeurs invalides, les données du jour, les calculs à la main, la révision et les reprises HTTP. Les tests paramétrés comptent plusieurs cas : 22 cas exécutés ne signifie pas 22 fonctions distinctes.

Le test d'upsert charge deux fois le même tableau, modifie un prix puis recharge. Il vérifie trois lignes finales et la nouvelle valeur. Le test d'échec partiel effectue une première collecte valide puis fait échouer Ethereum ; il vérifie que son ancien prix reste en place et que Bitcoin est actualisé.

tests/test_trends.py couvre séries croissantes et décroissantes, série constante, bandes, RSI extrêmes, trous, causalité et caractère ponctuel du croisement. Les exemples contrôlés sont indispensables : un graphique visuellement plausible peut masquer un décalage de sept dates ou un calcul sur la mauvaise unité.

tests/test_dashboard.py utilise AppTest de Streamlit. Il vérifie l'état vide, les trois onglets, l'absence d'exception et les filtres d'actifs. Ce n'est pas un test exhaustif de tous les navigateurs ni de l'esthétique. Même sans réseau extérieur, Streamlit utilise une boucle asyncio et des sockets locales ; elles étaient bloquées dans le sandbox de la session et le test a été exécuté hors de ce sandbox.

Des tests supplémentaires seraient utiles sur Retry-After en date HTTP, erreurs 5xx, jours multi-devises, rollback SQL et incidents de stockage. La couverture existante réduit des risques précis ; elle ne permet pas d'affirmer zéro bug, ni un pourcentage de couverture non mesuré.

## 17. Git, GitHub, CI et secrets

Git versionne le projet local ; GitHub héberge un dépôt distant. Un commit local ne publie rien. git add prépare le contenu du prochain commit ; git commit crée un jalon ; git status montre l'écart du dossier de travail ; git log affiche les jalons ; git push transmet des commits au dépôt distant configuré.

L'historique du projet comporte l'initialisation, le pipeline, le dashboard et les tests, la validation, l'ajout des tendances et la correction de surveillance Streamlit. Les commits ont reçu une identité explicitement passée via git -c, sans modifier la configuration globale. Une adresse d'auteur figure dans les commits Git : un dépôt public expose normalement ces métadonnées.

.gitignore exclut .env, .venv, data, bases SQLite, logs et caches. Il n'efface pas un secret déjà commité : dans ce cas, il faut révoquer le secret et nettoyer l'historique avec une procédure adaptée. Un scan de motifs courants réduit le risque sans garantir mathématiquement l'absence de tout secret arbitraire.

Le workflow GitHub Actions s'exécute sur push et pull_request. Sa matrice prévoit quatre combinaisons : deux systèmes et deux versions Python. Chaque job installe le projet, exécute Ruff, vérifie le formatage et lance pytest. Il n'utilise aucune clé CoinGecko et ne collecte pas de données.

Une CI verte signifie que les vérifications définies passent dans les environnements exécutés. Elle ne prouve pas l'exactitude économique d'une stratégie, ni la disponibilité de l'API réelle, ni le bon fonctionnement de toutes les versions futures. Une collecte planifiée GitHub nécessiterait une gestion de stockage persistant distincte ; elle n'est pas incluse.

## 18. Exploitation, incidents et sécurité pratique

La commande crypto-etl update renvoie 0 si toutes les cryptos réussissent, 1 si le pipeline est partiel ou échoué ; argparse peut renvoyer 2 en cas d'usage ou de clé manquante. Un ordonnanceur doit traiter ces codes au lieu de se fier seulement à un fichier qui existe.

Sous Windows, configurer le Planificateur de tâches avec le chemin absolu du Python du venv, les arguments -m crypto_etl.cli update et un dossier de démarrage stable. Sous Linux, un wrapper privé peut charger la clé depuis un fichier protégé puis être lancé par cron et flock. Choisir une heure après la disponibilité du snapshot et préciser le fuseau de l'ordonnanceur.

Éviter deux collectes simultanées. SQLite peut refuser une écriture concurrente. Sauvegarder une base avec l'API Connection.backup plutôt que copier à l'aveugle un fichier en cours d'écriture. Prévoir rotation des logs et rétention des archives. Ces procédures sont documentées ; aucune tâche quotidienne n'a été créée automatiquement pendant le développement.

Incident réel : KeyError 'trend'. L'interface mise à jour attendait une colonne produite par le nouveau module, alors que le serveur gardait l'ancien module en mémoire. Un processus neuf produisait la colonne. Le correctif a été de redémarrer Streamlit et de surveiller src via .streamlit/config.toml. Cette configuration aide le rechargement ; elle ne remplace pas un redémarrage contrôlé lors d'un déploiement.

Incident d'environnement : l'installation pip échouait sur la chaîne de certificats. La solution a transmis les autorités de certification Windows à pip, y compris ses sous-processus, au lieu de désactiver la vérification TLS. Ce point distingue la résolution d'un problème local de l'introduction d'une faiblesse de sécurité.

## 19. Formulations CV et présentation honnête du travail

Titre possible : « Projet personnel - pipeline ETL crypto et dashboard analytique Python ». Ligne synthétique : « Mise en œuvre d'une chaîne CoinGecko -> pandas -> SQLite -> Streamlit/Plotly, avec chargements idempotents, contrôles qualité et 22 cas de test hors réseau. »

Pour un profil data engineer : « Structuration d'un pipeline local avec archives brutes, normalisation UTC, clé composite SQL, upserts transactionnels et suivi des échecs partiels ; configuration d'une CI Windows/Linux. » Pour un profil data analyst : « Calcul et visualisation de rendements, volatilité, drawdown et tendances descriptives ; comparaison base 100 et gestion explicite des données manquantes. »

Ajouter seulement ce que vous êtes capable d'expliquer. Ne pas écrire « prédiction du marché », « plateforme haute disponibilité », « millions de lignes traitées », « stratégie rentable » ou « production cloud » : ces éléments ne sont pas réalisés. Dire « CI configurée » si son exécution distante n'est pas encore vérifiée ; dire « client API implémenté » plutôt que « collecte réelle validée » tant qu'une clé n'a pas été testée.

L'assistance IA a servi à produire du code, des tests et la documentation. Vous pouvez dire : « J'ai utilisé un assistant pour accélérer l'implémentation, puis j'ai étudié les décisions, exécuté les tests et vérifié les cas limites. Je peux montrer les fonctions et expliquer leur comportement. » Ne présentez pas comme personnellement maîtrisée une partie que vous n'avez pas encore étudiée.

Pour montrer votre appropriation, préparez une modification simple en direct : ajouter une devise de test, changer le seuil de forte variation ou écrire un test sur un jour manquant. Expliquer pourquoi la modification est sûre a plus de valeur que réciter une liste de bibliothèques.

## 20. Démonstration d'entretien en dix minutes

Minute 0-1 : expliquer le besoin, le périmètre et l'état synthétique des données. Minute 1-2 : montrer le schéma du flux et l'indépendance du dashboard. Minute 2-3 : afficher la vue d'ensemble et comparer les bases 100. Minute 3-4 : montrer tendance, RSI et canal en distinguant observation et prévision.

Minute 4-5 : ouvrir transform.py et expliquer la jointure par timestamp. Minute 5-6 : ouvrir storage.py et montrer la clé composite ainsi que ON CONFLICT. Minute 6-7 : montrer le test de révision historique et celui d'échec partiel. Minute 7-8 : lancer pytest et Ruff dans l'environnement préparé.

Minute 8-9 : montrer une limite réelle, par exemple les fenêtres incomplètes ou l'absence de lockfile. Minute 9-10 : proposer l'amélioration suivante avec un critère de réussite : collecte réelle expurgée, fermeture explicite des connexions, tests supplémentaires, puis stockage plus robuste si le volume justifie cette évolution.

Avant la réunion : générer la démo, lancer le serveur, ouvrir les fichiers et vérifier les commandes. Prévoir le PDF et une capture si le navigateur ou le réseau échoue. Ne pas afficher une clé en partage d'écran, ne pas dépendre d'un appel CoinGecko pour démontrer les transformations, et ne pas masquer les données synthétiques.

## 21. Questions d'entretien : réponses argumentées

### Pourquoi SQLite plutôt que PostgreSQL ?
Pour un outil local mono-utilisateur et quelques centaines de points par collecte, SQLite réduit l'installation et permet de démontrer SQL, contraintes et transactions. PostgreSQL devient intéressant si plusieurs services écrivent simultanément, si les accès doivent être administrés ou si le volume et les requêtes dépassent ce cadre. Le choix dépend des besoins mesurés, pas du prestige d'un outil.

### Pourquoi ne pas tout garder en CSV ?
Un CSV est simple pour l'échange, mais ne garantit pas lui-même une clé unique ni un upsert transactionnel. SQLite fournit des contraintes et des requêtes paramétrées. Le CSV reste utile comme export de sélection, tandis que JSON conserve les réponses avant transformation.

### Quelle est la différence entre ETL et ELT ici ?
Les données sont nettoyées en Python avant le chargement dans la table d'analyse : le chemin principal est ETL. L'archive brute est néanmoins conservée. Dans un ELT, on chargerait généralement les données brutes dans un stockage analytique avant transformation ; le fait d'avoir une archive de fichiers ne transforme pas automatiquement cette application en architecture ELT complète.

### Comment garantissez-vous l'absence de doublons ?
La clé primaire composite est la garantie finale. La transformation résout aussi les timestamps dupliqués et les multiples observations journalières. L'upsert traite le conflit sans ajouter une seconde ligne. Les tests chargent deux fois la même série et contrôlent le nombre de lignes.

### Si l'API corrige un prix vieux de dix jours ?
La fenêtre de 180 jours est recollectée. La ligne corrigée remplace la ligne existante par upsert. Les indicateurs sont recalculés au prochain affichage, donc leurs fenêtres sont actualisées. La base n'historise pas les anciennes versions de cette ligne ; les archives de collecte peuvent aider à les retrouver.

### Pourquoi sept lignes ne suffisent pas pour sept jours ?
Une série peut manquer un jour. Un décalage de sept lignes saute alors huit jours calendaires. Reconstituer un index quotidien avec asfreq('D') fait du shift(7) un décalage de sept dates. Si une extrémité manque, le rendement reste indisponible au lieu d'utiliser une autre date.

### Pourquoi ne pas remplir les prix manquants ?
Un remplissage peut créer des rendements nuls artificiels et réduire la volatilité estimée. L'application préfère conserver l'incertitude. Une méthode d'imputation pourrait être pertinente pour un autre usage, mais elle devrait être explicite, évaluée et séparée des données observées.

### Le prix du jour est-il vraiment une clôture ?
Non. C'est un snapshot CoinGecko, agrégé et daté en UTC. La règle du projet retient le dernier point valide du jour terminé. L'interface ne l'appelle pas clôture officielle, et les figures de chandeliers ne sont pas calculées à partir de ces seules données.

### Que signifie 22 tests réussis ?
Cela signifie 22 cas exécutés localement, y compris des paramètres de tests. Ils couvrent des risques définis, pas toutes les entrées possibles. Je peux citer les cas d'alignement, d'upsert, d'erreur partielle et de causalité. Je ne revendique pas un taux de couverture qui n'a pas été mesuré.

### Les indicateurs donnent-ils un signal d'achat ?
Ils donnent des repères descriptifs. Aucun ordre n'est envoyé, aucune performance de stratégie n'est évaluée, et les seuils ne sont pas optimisés. Avant toute revendication prédictive, il faudrait un protocole hors échantillon avec coûts, liquidité, biais et comparaison à une référence.

### Comment évitez-vous d'utiliser le futur ?
Les fenêtres de calcul se terminent au jour observé, le canal précédent décale le prix d'un jour et aucun rolling centré n'est utilisé. Un test compare les résultats sur un préfixe seul à ceux du même préfixe extrait d'une série plus longue. Les filtrages de période pour base 100 sont des transformations d'affichage, pas des signaux de trading testés.

### Comment gérez-vous les secrets ?
La clé provient d'une variable d'environnement et passe dans un en-tête. Elle est exclue de repr, des logs et des fichiers versionnés. Les messages d'exception externes ne sont pas recopiés. Ces mesures ne chiffrent pas l'environnement ; elles réduisent l'exposition accidentelle dans le cadre local.

### Que feriez-vous à dix millions de lignes ?
Je mesurerais d'abord les lectures, le temps de calcul et la concurrence. Ensuite : collecte incrémentale avec fenêtre de recouvrement, ingestion par lots, index adaptés, PostgreSQL ou stockage colonnaire selon les accès, cache invalidé sur version de données et calculs préagrégés. Je ne migrerais pas sans besoin mesuré.

### Pourquoi la CI n'actualise-t-elle pas les prix ?
Les tests doivent rester déterministes et sans secret. Une collecte planifiée aurait un autre objectif et exigerait des identifiants, du stockage persistant et des alertes. Séparer les deux évite de confondre qualité du code et disponibilité de la source externe.

### Quel bug réel avez-vous rencontré ?
L'interface demandait trend, absent du module encore chargé en mémoire par Streamlit. La colonne existait dans un processus neuf. Le diagnostic a distingué données et cycle de chargement du code ; le correctif a redémarré le serveur puis ajouté la surveillance de src. Le test neuf seul n'aurait pas révélé cet état d'un serveur ancien.

### Quel compromis changeriez-vous en premier ?
Je fermerais explicitement les connexions SQLite, enrichirais les erreurs métier expurgées et validerais une collecte réelle. Puis j'ajouterais les tests manquants sur Retry-After et rollback. Ces améliorations renforcent la fiabilité avant d'ajouter davantage de graphiques.

## 22. Exercices avec résultats attendus

Exercice 1 : prix 100 puis 105 puis 110. Le premier rendement est indisponible, le deuxième vaut 5 %, le troisième environ 4,7619 %. La performance totale vaut 10 %, pas 9,7619 %. Vérifier en multipliant les facteurs de rendement.

Exercice 2 : prix 100,120,90. Base 100 : 100,120,90. Drawdown : 0,0,-25 %. Performance finale : -10 %. Expliquer pourquoi le drawdown final et la performance finale sont différents : ils n'ont pas le même prix de référence.

Exercice 3 : supprimer le quatrième jour d'une série de 40 prix. Attendre une ligne de calendrier manquante, des rendements quotidiens indisponibles autour du trou et des moyennes complètes interrompues. Le rendement à sept jours manque seulement si l'une de ses deux extrémités manque.

Exercice 4 : série constante à 100 pendant 40 jours. Attendre RSI=50 après initialisation, bandes égales à 100, volatilité=0 après 30 rendements, R² conventionnel=0 et absence de cassure. Les résultats initiaux restent manquants malgré la simplicité de la série.

Exercice 5 : série croissante de 100 à 159 par pas de 1. Sur la dernière fenêtre de 30 jours, le prix moyen est 144,5, la pente brute 1, la pente normalisée environ 0,692 %, R²=1, RSI=100 et résistance précédente=158. Le dernier prix 159 dépasse la résistance et donne un nouveau sommet 20 jours.

Exercice 6 : charger deux fois trois lignes, puis corriger la première. Attendre trois lignes en base, avec le prix corrigé. Comparer aussi collected_at : il est actualisé. Rédiger un test qui vérifie le résultat métier, pas uniquement le retour de la fonction.

Exercice 7 : simuler 429 puis 200 avec Retry-After=3. Attendre deux appels et une seule pause de trois secondes. Simuler quatre réponses 429 : attendre quatre appels, trois pauses et un échec. Simuler 401 : attendre un appel sans pause.

Exercice 8 : rendre une crypto indisponible après une collecte réussie. Attendre partial, conservation de son ancien prix et actualisation des autres actifs. Expliquer ce qui se passe si les trois échouent et ce que montre la fraîcheur des observations.

## 23. Feuille de route réaliste

Priorité 1, fiabilité : valider le client sur une vraie clé, ajouter fermeture explicite des connexions, deadline et erreurs métier expurgées, tester dates Retry-After, serveur 5xx et rollback. Critère : résultats attendus documentés, tests reproductibles, aucun secret dans les sorties.

Priorité 2, audit : préciser les compteurs qualité, stocker une version du contrat de transformation, gérer les exécutions abandonnées, organiser la rétention des archives et la sauvegarde. Critère : relier une ligne courante à une collecte et expliquer chaque rejet de façon non ambiguë.

Priorité 3, expérience : libellés français et unités homogènes dans les tableaux, cache invalidé sur la dernière collecte, comparaison sur dates communes optionnelle, renouvellement des paramètres Streamlit dépréciés. Critère : chargement mesuré et absence de valeurs périmées après mise à jour.

Priorité 4, analyse : corrélations de rendements sur jours communs, maximum drawdown, rendements logarithmiques et diagnostics de sensibilité. Pour une étude prédictive, créer un projet séparé avec protocole de validation, référence naïve et coûts de transaction. Ne pas faire passer un nouvel indicateur descriptif pour une preuve de prévision.

Priorité 5, industrialisation selon besoin : incrémental avec recouvrement, scheduler surveillé, packaging verrouillé, migrations, base serveur et déploiement authentifié. Docker reste une option future, pas une exigence satisfaite par ce dépôt actuel.

## 24. Glossaire et sources pour continuer

API : contrat d'échange entre logiciels. Endpoint : URL d'une ressource API. JSON : format de données textuelles. Timestamp : instant numérique référencé à une origine. UTC : référence temporelle commune. Snapshot : observation à un instant. ETL : extraire, transformer, charger.

DataFrame : tableau pandas avec index et colonnes. NaN : valeur numérique manquante en mémoire. NULL : valeur absente en SQL. Upsert : insertion ou mise à jour sur conflit. Transaction : groupe d'écritures validé ou annulé. Idempotence : répéter une opération conserve le même état métier visé.

Rendement : variation relative d'un prix. Volatilité : dispersion des rendements selon une définition donnée. Drawdown : baisse relative depuis un sommet. Régression : ajustement d'une relation. R² : part de variation expliquée par l'ajustement dans son échantillon. Causalité temporelle du calcul : absence d'accès aux observations futures ; ce n'est pas la preuve d'une relation causale économique.

Sources primaires pour le contrat externe : https://www.coingecko.com/learn/download-bitcoin-historical-data ; https://support.coingecko.com/hc/en-us/articles/4538879945625-API-key-can-I-store-the-key-in-my-headers ; https://support.coingecko.com/hc/en-us/articles/23126953719321-Why-is-there-a-discrepancy-between-the-close-price-of-a-token-on-the-coins-id-market-chart-interval-daily-endpoint-and-the-OHLC-prices-for-the-same-token .

Le code livré, les tests, le README et pyproject.toml constituent la référence pour le comportement de cette version. Les annexes suivantes en donnent une copie de travail. Les numéros de ligne de cette copie sont indicatifs pour l'édition du guide et peuvent changer après de futurs commits.
