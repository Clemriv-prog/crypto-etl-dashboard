# Key Crypto V1 - Guide technique, apprentissage et CV

Édition du 13 octobre 2026. Code de référence : 0485a01. Ce guide remplace, pour la V1, le guide de l'ancienne version avancée. Dépôt : https://github.com/Clemriv-prog/crypto-etl-dashboard .

## 1. Ce que tu construis et ce que tu dois apprendre

Key Crypto V1 est un projet étudiant de traitement de données. Il récupère des observations de Bitcoin, Ethereum et Solana, les nettoie, les conserve dans SQLite et les affiche dans une page Streamlit. Son objectif est de rendre une chaîne de données compréhensible, vérifiable et présentable en entretien.

Le périmètre par défaut est de 90 jours, une observation par jour UTC terminé, en USD. Une collecte manuelle fait trois requêtes, une par actif. Quatre indicateurs sont retenus : variation quotidienne, moyenne mobile 7 jours, volatilité 30 jours et prix normalisé en base 100. L'utilisateur filtre les actifs et la période, puis peut exporter un CSV.

Le code existe déjà et a été construit avec assistance IA. Ton travail personnel consiste à comprendre chaque étape, la réexécuter et savoir faire une petite modification. Présenter le projet comme maîtrisé demande davantage que télécharger le dépôt : tu dois relier une règle métier à une fonction et à un test.

La dernière validation locale de la V1 comprend 18 cas de test réussis, Ruff et son contrôle de formatage. Une démonstration neuve contient 270 observations synthétiques. Aucun volume réel de 50 000 observations n'est démontré par cette version. La collecte authentifiée reste à valider avec une vraie clé CoinGecko. Les résultats de CI distants sont à consulter dans l'onglet Actions ; ce guide ne présume pas leur état actuel.

Pour lire efficacement : commence par le besoin, le schéma du flux et les quatre calculs. Étudie ensuite les modules avec l'annexe de code. Termine par les exercices, les questions d'entretien et les formulations CV correspondant à ton niveau réel d'avancement.

## 2. Le besoin et la valeur du projet

Le besoin est de comparer des actifs dont les prix sont très différents tout en conservant une base locale propre. Un prix Bitcoin et un prix Solana ne se comparent pas directement en valeur absolue : la base 100 permet d'observer leur évolution relative depuis un point de départ.

La valeur technique ne vient pas du nombre de graphiques. Elle vient de trois garanties : relancer une collecte sans dupliquer les dates, ne pas inventer de prix manquant et conserver des données valides lorsqu'une source échoue. Ce sont des problèmes concrets rencontrés dans beaucoup de traitements de données, pas seulement en finance.

Une application qui appelle l'API à chaque filtre dépend du réseau et consomme du quota. Dans cette V1, le pipeline actualise SQLite manuellement et le dashboard lit cette base. On peut donc consulter les données déjà disponibles sans refaire une collecte.

Le projet démontre Python, pandas, une API REST, les clés et transactions SQL, la visualisation et des tests ciblés. Il ne démontre pas une stratégie d'investissement rentable, une architecture distribuée ou une application de production à grande échelle. Cette distinction rend sa présentation plus crédible.

## 3. Architecture : suivre une ligne de bout en bout

Le chemin d'exécution est : commande CLI, configuration, client CoinGecko, archive JSON, transformation et qualité, chargement SQLite. Le dashboard suit un second chemin : SQLite, calendrier quotidien, calcul des indicateurs, filtres, graphiques et export.

Extract signifie extraire : recevoir les données de l'API. Transform signifie transformer : convertir les dates, aligner les séries et contrôler les valeurs. Load signifie charger : enregistrer le résultat validé en SQL. Le nom ETL correspond à cet ordre. L'archive brute est un support de diagnostic, pas la table utilisée par les graphiques.

Exemple : l'API fournit un timestamp et un prix de 100. La transformation détermine sa date UTC, vérifie que le prix est positif et fini, puis décide s'il s'agit du dernier point valide de ce jour. Le stockage insère ou met à jour la ligne identifiée par l'actif, la devise et la date. À la lecture, pandas calcule sa variation si le jour précédent est disponible.

Les indicateurs ne sont pas stockés en SQL. Ils sont recalculés au moment de l'affichage, ce qui évite de maintenir une seconde table dérivée. Si un prix historique est corrigé, les fenêtres concernées sont recalculées à la prochaine lecture.

Les fonctions sont séparées par responsabilité. config.py charge les paramètres ; client.py parle HTTP ; transform.py nettoie ; quality.py décrit les anomalies ; storage.py porte SQL ; pipeline.py orchestre ; cli.py expose les commandes ; demo.py génère la démonstration ; indicators.py calcule ; dashboard/app.py affiche.

## 4. Pourquoi ces technologies et leurs alternatives

Python permet de traiter les appels HTTP, les données et l'interface dans un même langage. Cela limite les outils à apprendre pour un premier projet. Il faut cependant éviter de conclure que Python serait toujours le meilleur choix : ici, il convient au faible volume local et à l'objectif pédagogique.

requests rend visibles l'URL, les paramètres, l'en-tête et le timeout. Un SDK fournisseur aurait pu masquer une partie du contrat HTTP. La V1 utilise un client synchrone et un seul appel par actif ; elle n'a ni concurrence réseau ni reprise automatique.

pandas sert aux tableaux, aux jointures sur timestamp, aux calendriers et aux fenêtres glissantes. NumPy reste une dépendance indirecte de pandas mais n'est pas importé dans le projet. La bibliothèque standard math suffit au contrôle des valeurs finies. À gros volume, le chargement en mémoire et les calculs répétés demanderaient des mesures de performance.

SQLite fournit une base SQL sans serveur à administrer. Une clé primaire et un upsert sont plus adaptés aux mises à jour fiables qu'une accumulation de CSV. PostgreSQL serait à envisager pour plusieurs services écrivant simultanément ou une application partagée. Il n'est pas nécessaire pour démontrer les fondamentaux sur trois séries quotidiennes.

Streamlit permet de produire une interface analytique en Python. Plotly ajoute survol et zoom. Matplotlib conviendrait à des figures statiques, mais n'est pas utilisé dans cette V1. Une application web dédiée offrirait davantage de personnalisation au prix d'un périmètre plus large.

pytest vérifie les comportements et les résultats attendus. Ruff contrôle certains défauts de code et son formatage. GitHub Actions relance les contrôles sur plusieurs environnements. Aucun de ces outils ne prouve à lui seul la qualité économique d'une analyse ou l'absence de tous les bugs.

## 5. Installation et première exécution

Depuis le dossier du dépôt, créer un environnement avec python -m venv .venv. Sous PowerShell, activer avec .venv\Scripts\Activate.ps1 ; sous Linux, utiliser source .venv/bin/activate. Installer ensuite avec python -m pip install -e ".[dev]". L'installation éditable relie le paquet au code local ; les dépendances de développement ajoutent pytest et Ruff.

Lancer crypto-etl demo, puis streamlit run dashboard/app.py. Le premier programme écrit la base synthétique ; le second démarre un serveur web local. Le dashboard commence en mode démonstration, avec une bannière visible. Ces prix sont fabriqués et ne représentent pas le marché.

Si l'activation PowerShell ne fonctionne pas, appeler directement .venv\Scripts\python.exe -m crypto_etl.cli demo et .venv\Scripts\python.exe -m streamlit run dashboard/app.py. Cela évite de modifier une politique globale uniquement pour activer un environnement.

Pour une collecte réelle, charger COINGECKO_API_KEY dans le terminal, puis lancer crypto-etl update. Sous PowerShell : $env:COINGECKO_API_KEY="votre_cle". Sous Linux : export COINGECKO_API_KEY='votre_cle'. Désactiver le mode synthétique dans l'interface pour lire market.db. Ne jamais copier une vraie clé dans un document, une capture ou un commit.

Les tests et la démonstration n'ont besoin d'aucune API extérieure. Le téléchargement initial des dépendances nécessite Internet. Le moteur de test Streamlit utilise néanmoins des mécanismes locaux asyncio ; un environnement très restreint peut bloquer ses sockets locales sans que cela indique un défaut du dashboard.

## 6. Configuration centralisée

Config est une dataclass figée. Elle contient la clé, la devise, la durée, le dossier de données, les actifs, le timeout et l'URL. frozen=True empêche la réaffectation ordinaire des champs après construction. api_key utilise repr=False pour éviter d'apparaître dans la représentation de l'objet ; ce n'est pas un chiffrement du secret.

load_config lit quatre variables : COINGECKO_API_KEY, CRYPTO_CURRENCY, CRYPTO_DAYS et CRYPTO_DATA_DIR. Les valeurs par défaut sont clé vide, usd, 90 et data. .env.example est une documentation, pas un chargeur automatique : un fichier .env n'est pas lu par ce programme.

La durée est validée entre 1 et 365 jours. La devise doit être alphabétique mais n'est pas comparée à la liste des devises acceptées par CoinGecko. Une valeur alphabétique inexistante peut donc passer la validation locale puis échouer côté API. Une durée non convertible en entier échoue pendant le chargement de configuration.

db_path choisit demo.db ou market.db. Les bases et archives de démonstration sont séparées des données réelles. Un chemin relatif dépend du dossier de lancement : toujours lancer depuis le dépôt ou définir un chemin absolu pour CRYPTO_DATA_DIR.

La liste des actifs et le timeout sont des champs du code, pas des variables d'environnement documentées dans cette version. Modifier la liste demande aussi de vérifier la démonstration, qui possède des valeurs de base seulement pour les trois actifs prévus.

## 7. Client REST et erreurs compréhensibles

Client.fetch construit GET /coins/{coin_id}/market_chart avec vs_currency, days et interval=daily. La clé est transmise dans x-cg-demo-api-key. Les observations attendues arrivent dans prices, market_caps et total_volumes sous forme de paires timestamp/valeur.

Une session HTTP est injectable : en usage normal, requests.Session réalise l'appel ; dans un test, Mock renvoie une réponse fabriquée. Le timeout de 30 secondes limite les attentes réseau selon les mécanismes de requests. Il ne s'agit pas d'une garantie de durée maximale absolue de toute la collecte.

La V1 fait une tentative par actif. Une erreur réseau produit un message générique. Une réponse autre que 200 produit une erreur contenant le statut HTTP. Un JSON illisible est refusé. Il n'existe pas de boucle de reprise, de backoff ni de traitement Retry-After automatique : en cas de 429, attendre puis relancer manuellement.

validate_payload vérifie la présence des trois listes et la longueur des paires. Cette validation est appelée par transform après archivage du JSON décodable. Un objet JSON mal structuré peut ainsi être conservé pour diagnostic puis rejeté. Un corps non décodable en JSON n'est pas archivé comme réponse JSON dans cette version.

Le pipeline ne recopie pas les textes d'exceptions externes dans son bilan : il garde le type de l'erreur. Cela réduit le risque de fuite, mais limite les détails de diagnostic. Pour apprendre, commencer par les codes HTTP : 400 indique une requête refusée, 401 une authentification refusée, 429 une limitation et 500 une erreur serveur. Les causes exactes restent dépendantes du fournisseur.

## 8. Nettoyage et alignement des données

transform reçoit un objet JSON, un actif, une devise, une durée et éventuellement une date now pour les tests. Elle détermine le jour courant UTC et la fenêtre des jours terminés. Le jour UTC en cours et les dates futures sont exclus, car ils ne constituent pas encore une observation quotidienne complète.

Les trois séries sont converties en DataFrames séparés. Le timestamp devient numérique ; les timestamps non convertibles sont retirés. Les doublons exacts de timestamp sont résolus en gardant la dernière occurrence de chaque série. Les tableaux sont ensuite alignés sur cette clé avec concat, pas sur la position des lignes.

Exemple : les prix existent pour le 1er et le 2 janvier, mais la capitalisation seulement pour le 2 janvier. La capitalisation doit être manquante au 1er janvier, et présente au 2. Associer les premiers éléments des deux listes ferait une erreur silencieuse. C'est pourquoi la jointure doit utiliser une clé explicite.

pd.to_datetime convertit les millisecondes avec utc=True et errors='coerce'. Après conversion en UTC, le fuseau est retiré et l'heure normalisée afin de conserver une date quotidienne. Le nom date_utc garde cette convention. Un timestamp non représentable devient une date manquante.

Chaque valeur devient numérique. math.isfinite exclut infinis et NaN. Un prix doit être strictement positif : zéro, négatif ou manquant entraîne un rejet. Volume et capitalisation peuvent être nuls ; s'ils sont invalides, leur valeur est absente sans rejeter un prix valide.

Les lignes valides dans la fenêtre sont triées par timestamp, puis la dernière observation valide de chaque jour est conservée. Il n'y a pas de remplissage d'une autre série depuis un timestamp voisin. Il n'y a pas d'interpolation des prix. Le résultat est trié par date et porte l'actif et la devise.

## 9. Qualité : ce qui est signalé et ce qui ne l'est pas

quality_report construit les dates attendues de la fenêtre et compare aux dates retenues. missing_days liste les jours absents. Le bilan contient aussi accepted, rejected, duplicate_timestamps, excluded_current_or_future, missing_market_cap, missing_volume et large_changes.

Une variation absolue supérieure à 50 % est signalée, sans suppression arbitraire. Une variation importante peut être réelle. Le bilan est conservé avec l'exécution dans pipeline_runs ; la page simplifiée n'affiche pas une vue détaillée de tous ces compteurs.

Les compteurs ne sont pas une partition parfaite de tous les éléments bruts. Les doublons sont comptés par série, les timestamps non numériques sont retirés avant rejected et les rejets sont évalués avant le filtre temporel. Connaître ces limites évite d'affirmer que le bilan explique exhaustivement chaque point reçu.

Un jour absent de la nouvelle réponse peut déjà exister dans SQLite grâce à une ancienne collecte. La qualité d'une collecte et la qualité de toute la base sont donc différentes. Les données anciennes restent jusqu'à l'arrivée d'une nouvelle valeur valide ; la V1 n'efface pas automatiquement une ligne parce qu'elle manque dans une nouvelle réponse.

Dans le dashboard, les trous du calendrier sélectionné sont signalés. La fraîcheur est contrôlée par actif ; une donnée antérieure à la veille UTC donne un avertissement. Ce contrôle ne certifie pas que les chiffres sont économiquement exacts, mais rend visible un retard de collecte.

## 10. SQLite, clé primaire et upsert

daily_market_data contient actif, devise, date UTC, timestamp source, prix, capitalisation, volume 24 h et date de collecte. La clé primaire (coin_id, vs_currency, date_utc) définit l'unicité métier. La date seule ne suffit pas puisque plusieurs actifs et devises partagent le même jour.

INSERT ... ON CONFLICT ... DO UPDATE permet d'insérer une date nouvelle ou d'actualiser une ligne existante. Si la même réponse est chargée deux fois, le nombre de dates ne double pas. Si un prix historique est révisé, il est remplacé par la nouvelle valeur valide.

L'idempotence porte sur l'état métier attendu : absence de doublons et conservation du prix fourni. collected_at est actualisé à chaque chargement, donc rejouer un lot n'est pas nécessairement une opération identique bit à bit sur toutes les métadonnées.

Les écritures sont liées avec des placeholders SQL. Cela évite de concaténer des valeurs dans une requête. Les contraintes CHECK contrôlent les valeurs positives ou non négatives. Python convertit ses valeurs manquantes en None pour stocker SQL NULL, ce qui n'est pas la même chose que zéro.

La transaction couvre un actif. Si son lot échoue, ses écritures sont annulées ; les actifs déjà validés restent disponibles. Le context manager utilise closing pour fermer explicitement la connexion et le contexte sqlite3 pour commit/rollback. SQLite est adapté à l'usage local, sans gestion avancée de plusieurs collectes simultanées.

La base conserve la version actuelle d'une ligne, pas toutes ses révisions. Les archives JSON peuvent aider à enquêter. REAL SQLite représente les nombres en virgule flottante : ce choix convient à cette analyse descriptive, pas à une comptabilité financière exigeant un calcul décimal exact.

## 11. Orchestration, traces et collecte partielle

run crée un identifiant UUID et enregistre running dans pipeline_runs. Pour chaque actif : obtenir le JSON, l'archiver, transformer, vérifier qu'il existe au moins une ligne valide, puis faire l'upsert. Une erreur est isolée pour permettre aux autres actifs de continuer.

Le statut final est success si tous réussissent, partial si certains réussissent, failed si aucun ne réussit. rows_processed compte toutes les lignes traitées avec succès, y compris les lignes actualisées. Ce n'est pas le nombre de nouvelles insertions.

Exemple : une première collecte réussit pour les trois actifs. À la suivante, Ethereum échoue tandis que Bitcoin et Solana réussissent. Leurs nouvelles données sont chargées ; celles d'Ethereum restent anciennes ; le statut devient partial et le dashboard avertit de l'incomplétude et éventuellement de la fraîcheur.

Les archives se trouvent dans raw ou raw-demo, avec un sous-dossier par identifiant d'exécution. Il n'existe pas de transaction unique entre le système de fichiers et SQLite : une archive peut exister alors qu'un chargement a échoué. Une interruption brutale peut laisser running ; aucune récupération automatique de ce statut n'est implémentée.

La CLI expose demo et update. La commande renvoie 0 pour un succès complet, 1 pour une collecte partielle ou échouée, et argparse peut renvoyer 2 pour un usage invalide ou une clé manquante. Un incident de stockage avant le traitement peut encore faire échouer la commande directement.

## 12. Calcul 1 : variation quotidienne

La formule est 100 × (P(t)/P(t-1) - 1). Pour 100 puis 105, le rendement est 5 %. Pour 105 puis 100, il vaut environ -4,7619 %, pas -5 %. Le prix de référence est différent dans les deux sens.

Dans le code : price.pct_change(fill_method=None) * 100. fill_method=None évite de reporter automatiquement le dernier prix connu à un jour manquant. Les résultats sont en pourcentage : la valeur 5 signifie 5 %, pas 0,05 %.

indicators groupe par actif et devise puis applique asfreq('D'). Un jour absent apparaît comme NaN. Sans calendrier explicite, la ligne précédente pourrait dater de plusieurs jours et le résultat serait présenté à tort comme quotidien. Au premier jour, le rendement est indisponible car aucun prix précédent n'est présent.

Les rendements simples se composent. Deux hausses de 10 % donnent 1,1 × 1,1 = 1,21, donc 21 % au total. Additionner naïvement les rendements donne une approximation, pas une performance exacte. La V1 n'ajoute pas de rendement logarithmique.

## 13. Calcul 2 : moyenne mobile 7 jours

La MM7 est la moyenne des sept derniers prix quotidiens, jour observé inclus. Les prix 100, 101, 102, 103, 104, 105, 106 donnent 721/7 = 103. Le code utilise rolling(7, min_periods=7).mean(). Les six premiers résultats restent manquants.

Une moyenne mobile lisse les fluctuations. Elle est retardée par construction et ne prédit pas le prochain prix. Le fait qu'un prix soit au-dessus de sa moyenne ne prouve pas une hausse future et ne déclenche aucun achat dans cette application.

Une fenêtre exige sept prix valides. Si l'un des jours manque, la moyenne reste indisponible tant que cette date se trouve dans la fenêtre. La V1 ne remplace pas le prix absent par une valeur interpolée ou le prix précédent.

La MM7 est calculée avant le filtre d'affichage. Si la sélection commence le 10 juin mais que les données depuis le 4 juin existent, la moyenne du 10 juin peut utiliser ces jours. Filtrer d'abord provoquerait artificiellement six valeurs manquantes au début de chaque sélection.

## 14. Calcul 3 : volatilité 30 jours

La volatilité retenue est l'écart-type échantillonnal de 30 rendements quotidiens exprimés en pourcentage. Dans le code : return_1d.rolling(30, min_periods=30).std(ddof=1). Il faut 31 prix consécutifs pour obtenir 30 rendements valides.

Calcul pédagogique sur trois rendements 1 %, 2 %, 3 % : moyenne 2 %, écarts -1, 0 et 1 point de pourcentage ; somme des carrés 2 ; division par n-1 = 2 ; racine de 1 = 1 point de pourcentage. Avec ddof=0, le résultat serait environ 0,8165. L'exemple explique l'écart-type ; l'application utilise une fenêtre de 30, pas de trois rendements.

La mesure n'est pas annualisée. Une conversion annuelle demanderait une convention et des hypothèses supplémentaires. Un résultat élevé indique de fortes fluctuations observées, sans indiquer à lui seul la direction des prix. Un résultat faible ne garantit pas l'absence de choc futur.

Un seul prix manquant peut invalider deux rendements consécutifs, puis plusieurs fenêtres de volatilité. C'est un comportement attendu, pas une raison pour remplacer les résultats indisponibles par zéro. La V1 ne calcule ni VaR ni risque de portefeuille.

## 15. Calcul 4 : comparaison en base 100

La formule est 100 × prix / premier prix disponible de la sélection. Avec 200 au départ et 220 à la fin, la base passe de 100 à 110. Cela correspond à une hausse de 10 %, même si un autre actif possède un niveau de prix très différent.

La base 100 est recalculée après le filtre de période avec select_period. Elle répond à une question liée à l'intervalle choisi : comment les actifs ont-ils évolué depuis leur premier prix disponible dans cette sélection ? Changer le début change la référence.

Une base finale 120 signifie +20 % par rapport au prix de référence, pas +120 %. Le graphique compare les trajectoires relatives, pas la capitalisation des actifs ni le rendement net d'un portefeuille tenant compte des frais.

Si une crypto ne possède pas de prix au début de la période, son premier prix disponible est utilisé. Deux actifs peuvent alors avoir des dates de référence différentes. Il faut vérifier ces dates avant de tirer une conclusion de comparaison ; une option d'alignement sur dates communes est une amélioration possible, non incluse.

## 16. Dashboard : une page, des choix simples

La page démarre en mode synthétique. Elle vérifie l'existence de la base puis l'existence de données pour la devise. Un état vide donne la commande d'initialisation plutôt qu'un tableau d'erreur. La dernière collecte et les données anciennes sont signalées.

La barre latérale permet de sélectionner les actifs et les dates. Le tableau montre le dernier prix disponible dans cette sélection, sa date, sa variation quotidienne et sa volatilité. Le graphique base 100 compare les actifs retenus. Un sélecteur choisit ensuite l'actif du graphique prix/MM7 et de la volatilité.

Le bouton export produit un CSV du tableau sélectionné, avec ses indicateurs et ses éventuelles lignes calendaires manquantes. Les fichiers portent un nom distinct selon le mode démo ou réel. La clé API n'est pas incluse dans les données exportées.

Streamlit réexécute le script lors des interactions. La V1 relit SQLite et recalcule sans cache. Pour ce volume réduit, cela garde le fonctionnement simple. Les filtres n'écrivent pas de prix et n'appellent jamais CoinGecko. Plotly fournit survol et zoom ; ce n'est pas une interface de trading.

Le volume et la capitalisation restent dans le stockage mais ne disposent pas de graphiques dédiés dans cette page. Garder les données sources disponibles n'oblige pas à élargir la présentation. Les messages et unités doivent toujours être lus avec la devise configurée et les dates UTC.

## 17. Démonstration et tests : interpréter les preuves

demo.py fabrique des séries déterministes selon la position dans la fenêtre, avec une progression et une sinusoïde. La fin du calendrier suit la veille UTC. Une base neuve contient 90 × 3 = 270 lignes ; une ancienne base peut en contenir davantage car le pipeline ne supprime pas les anciennes dates.

La suite actuelle exécute 18 cas : certaines fonctions de test sont paramétrées sur plusieurs entrées. Dix-huit cas ne signifie pas dix-huit fonctions distinctes. Les tests ne nécessitent ni clé ni requête extérieure.

Les contrôles couvrent réponses mal formées, réponse vide, timestamps non alignés, doublons, prix invalide, valeur infinie, jour courant, dernier snapshot valide, calendrier, calculs à la main, correction historique, erreurs HTTP et échec partiel. Le test dashboard vérifie l'état vide, l'absence d'exception et les filtres.

Le test d'upsert charge plusieurs fois trois dates, corrige un prix et vérifie qu'il reste trois lignes. Le test partiel commence avec des données valides, fait échouer Ethereum puis vérifie la conservation de son ancien prix et la mise à jour de Bitcoin. Ces assertions vérifient un résultat concret, pas seulement que la fonction ne plante pas.

AppTest de Streamlit exécute l'application sans ouvrir un navigateur. Cela ne remplace pas un contrôle visuel et ne teste pas tous les navigateurs. Des cas supplémentaires seraient utiles : plusieurs devises, rollback sur panne SQL, arrêt brutal et absence de clé. Aucun pourcentage de couverture n'a été mesuré.

## 18. GitHub, CI et protection des secrets

Git conserve l'historique local ; GitHub héberge les commits publiés. git status montre l'état du dossier ; git add prépare un commit ; git commit crée un jalon ; git push transmet le jalon. La branche main porte maintenant la V1. Le tag version-avancee-archive conserve le code précédent.

.gitignore exclut .env, les bases, les archives data, les logs, les caches et .venv. Un fichier déjà commité n'est pas retiré automatiquement par cette règle. Si un vrai secret a été publié, il faut d'abord le révoquer puis traiter l'historique ; simplement supprimer sa ligne ne suffit pas.

La clé est chargée depuis l'environnement, exclue du repr de Config et passée dans un en-tête. Le pipeline ne copie pas les messages d'erreur externes. Une variable d'environnement n'est pas un coffre chiffré : ces choix réduisent surtout l'exposition accidentelle dans un outil local.

GitHub Actions exécute installation, Ruff, formatage et pytest sur Windows/Linux avec Python 3.10/3.12. Le workflow ne collecte aucune donnée et n'a besoin d'aucune clé CoinGecko. Une CI verte prouve seulement que ces contrôles passent pour le commit exécuté dans ces environnements.

Le guide avancé de 57 pages est archivé et ne décrit plus cette V1. Pour préparer ton entretien, utiliser le présent guide et le README actuel. Il n'est pas nécessaire de présenter sur ton CV les fonctionnalités d'une ancienne version que tu ne maîtrises pas.

## 19. Limites à connaître et difficultés à expliquer

Les prix sont des snapshots CoinGecko, pas une clôture officielle. Les réponses peuvent manquer ou être révisées. Le volume est observé sur 24 h et ne doit pas être additionné comme si chaque point couvrait une période indépendante. Le projet ne garantit pas la qualité intrinsèque du fournisseur.

La collecte réelle n'a pas encore été validée avec une clé dans notre session. Le client est implémenté et testé par simulation, ce qui n'est pas la même preuve. La documentation fournisseur doit être revérifiée avant un premier usage réel ; aucun quota commercial permanent n'est garanti par le code.

L'outil est local : pas d'authentification, de haute disponibilité, de scheduler automatique, de cache, de migrations ou de gestion élaborée de concurrence. Le client n'attend pas automatiquement Retry-After. Les dépendances sont bornées mais pas verrouillées exactement. Les archives n'ont pas de politique automatique de rétention.

La V1 conserve les lignes valides antérieures si une nouvelle collecte ne les fournit plus. Elle ne conserve pas en SQL toutes les anciennes versions d'un prix. Elle peut laisser une exécution running après un arrêt brutal. Ces compromis doivent être expliqués, pas masqués.

Incident utile à raconter : dans l'ancienne interface, un module gardé en mémoire ne produisait pas la nouvelle colonne trend. Le diagnostic a comparé le serveur existant à un processus neuf. Le redémarrage et la surveillance du dossier src ont corrigé ce problème de chargement. La colonne trend n'existe plus dans la V1 ; cet incident illustre une difficulté passée, pas une fonctionnalité actuelle.

## 20. Plan d'apprentissage sur quatre semaines

Semaine 1 : lire config et client, reproduire un objet JSON simulé, puis transformer une série. Livrable personnel : expliquer les entrées et sorties et justifier la jointure par timestamp. Exercice : retirer une capitalisation et vérifier qu'elle ne glisse pas vers le mauvais prix.

Semaine 2 : comprendre la table SQLite et la clé composite, charger deux fois les mêmes dates, corriger un prix, simuler un échec. Livrable : montrer trois lignes conservées après deux chargements et la nouvelle valeur après correction. Expliquer la différence entre nouvelle ligne et ligne traitée.

Semaine 3 : refaire les quatre indicateurs à la main, modifier une période et suivre les colonnes jusqu'au graphique. Livrable : démonstration de la page, sans appeler l'API à chaque filtre. Exercice : introduire un jour absent et expliquer les valeurs indisponibles.

Semaine 4 : lancer les contrôles, écrire ou adapter un test simple, relire le README et préparer une présentation de cinq minutes. Livrable : une modification personnelle expliquée avec son test et une description CV proportionnée à ce que tu sais démontrer.

Environ 6 à 10 heures par semaine est une estimation de travail, pas une garantie. Si Python et SQL sont nouveaux, réduire la première étape à Bitcoin puis ajouter les autres après compréhension. Garder le périmètre stable : finir la chaîne de données avant d'ajouter un nouvel indicateur.

## 21. Valoriser le projet sur le CV selon ton avancement

Si tu commences seulement, écrire « Projet personnel en cours : apprentissage d'un pipeline API → pandas → SQLite et d'un dashboard Streamlit ». Tu peux mentionner l'objectif et les technologies étudiées, mais pas affirmer une maîtrise ni une collecte réelle terminée. Ne mets pas un projet en cours au même niveau qu'une réalisation professionnelle livrée.

Après avoir compris, exécuté et modifié la V1, titre conseillé : « Key Crypto - Pipeline ETL et dashboard d'analyse crypto ». Ligne de technologies : « Python · pandas · API REST · SQLite · Streamlit · Plotly ». NumPy, Matplotlib, corrélations et détection de motifs ne font pas partie de la V1 à valoriser.

Version courte prête à adapter : « Développement d'un pipeline Python de collecte et de nettoyage des données de trois cryptomonnaies ; stockage SQLite sans doublons et dashboard interactif de comparaison des performances. » Utiliser cette formulation lorsque tu peux défendre ses étapes. Si tu as surtout étudié le code généré, préférer « Réalisation avec assistance IA et appropriation d'un pipeline... ».

Version en trois puces, après appropriation : « Collecte API et nettoyage des données quotidiennes de Bitcoin, Ethereum et Solana avec pandas. » ; « Stockage SQLite avec upserts et tests des mises à jour sans doublons. » ; « Dashboard Streamlit/Plotly : variations, MM7, volatilité, comparaison base 100 et export CSV. » Ces phrases expriment des réalisations concrètes sans vocabulaire gonflé.

Les chiffres défendables sont trois actifs, 90 jours configurés, quatre indicateurs et 18 cas de test existants. Les 270 lignes sont synthétiques sur une base neuve, pas des données réelles collectées. Ne reprendre ni 50 000 observations, ni millions de lignes, ni gain de performance, ni taux de couverture sans mesure correspondante.

Ajouter un lien court vers le dépôt sous le titre. Le README permet au recruteur de retrouver l'installation, les tests et les limites. La qualité de la démonstration et ta capacité à expliquer les cas difficiles valent davantage qu'une longue liste de technologies.

## 22. Adapter le CV au poste visé

Pour un stage data analyst : mettre en avant la préparation des données et l'interprétation. Proposition : « Préparation de séries quotidiennes avec pandas et création d'un dashboard de comparaison en base 100, moyennes mobiles et volatilité ; gestion explicite des données manquantes. » Préparer un exemple où un trou empêche une moyenne valide.

Pour un stage data engineering ou Python : mettre en avant l'ingestion, la qualité et le stockage. Proposition : « Mise en œuvre d'un pipeline API REST → pandas → SQLite, avec validation des observations, upserts transactionnels et conservation des données après échec partiel. » Préparer une explication de la clé composite et du lot transactionnel.

Pour un profil généraliste : privilégier la chaîne complète. Proposition : « Réalisation d'une application locale Python reliant collecte API, stockage SQL et dashboard interactif, accompagnée de tests automatisés et d'une documentation d'installation. » Les détails de statistiques peuvent être réservés à l'entretien.

La CI est un élément de méthode complémentaire. Tu peux écrire « Vérifications automatisées avec pytest et GitHub Actions » si tu sais lire le workflow et expliquer qu'il ne collecte pas les prix. Ne pas écrire « déploiement automatique » : aucune application n'est déployée par cette CI.

Éviter : « expert des marchés crypto », « prédiction », « outil de trading », « infrastructure scalable », « production » et « haute disponibilité ». Le projet est une réalisation locale d'apprentissage. Une formulation précise peut être ambitieuse sans être trompeuse.

## 23. Présenter le projet en entretien et expliquer l'assistance IA

Pitch de 30 secondes, après appropriation : « J'ai travaillé sur un projet Python qui récupère des données CoinGecko, les nettoie et les conserve dans SQLite sans doublons. Une page Streamlit permet de comparer trois actifs et leurs indicateurs simples. J'ai utilisé une assistance IA, puis vérifié les traitements avec des tests et travaillé les limites sur les dates et les données manquantes. » Adapter au travail réellement effectué.

Présentation de deux minutes : expliquer d'abord le besoin ; dessiner le flux en cinq étapes ; choisir une difficulté, comme le double chargement ou un jour manquant ; montrer le test correspondant ; finir par une limite et l'amélioration suivante. Ne pas réciter toutes les fonctions.

Si l'on demande « Qu'as-tu fait toi-même ? », citer des actions vérifiables : lecture et explication d'une fonction, modification d'une règle, ajout d'un test, diagnostic d'un comportement, installation et démonstration. Ne pas prétendre avoir écrit sans aide du code fourni par un assistant. Tu peux valoriser ta capacité de vérification et d'appropriation.

Si tu ne maîtrises pas encore une partie, dire « Je comprends le rôle de la transaction mais je dois encore approfondir son comportement en cas de concurrence ». Une limite explicitée est plus défendable qu'une réponse improvisée. Le projet fournit un support concret pour apprendre.

Questions de relance à préparer : pourquoi SQLite, pourquoi ne pas interpoler, pourquoi 31 prix pour la volatilité, que fait un upsert, pourquoi une variable d'environnement, que prouvent les tests et ce qu'il faudrait ajouter avant un déploiement partagé. Les réponses suivantes donnent des repères, à reformuler avec tes mots.

## 24. Questions-réponses techniques

### Pourquoi séparer le pipeline et le dashboard ?

Le pipeline modifie la base ; le dashboard consulte son état. Cela évite des appels réseau à chaque filtre, facilite les tests et permet de garder une dernière version consultable après une erreur de collecte.

### Pourquoi SQLite plutôt qu'un CSV ?

SQLite fournit une clé primaire, des contraintes et des transactions. Un CSV est utile pour exporter mais ne gère pas lui-même un conflit d'unicité. Le stockage doit permettre de rejouer une collecte sans ajouter de doublons.

### Qu'est-ce qu'un upsert ?

Une insertion avec mise à jour si la clé existe déjà. Dans le projet, le conflit porte sur actif, devise et date. Le test vérifie qu'une correction remplace le prix sans augmenter le nombre de lignes.

### Pourquoi ne pas combler un prix absent ?

Le remplissage inventerait une valeur et pourrait créer un rendement nul artificiel, donc modifier la volatilité. La V1 garde le trou et rend indisponibles les calculs qui exigent ce prix.

### Pourquoi une MM7 peut-elle exister au début de la période filtrée ?

Les calculs utilisent toute l'histoire disponible avant le filtre. Les jours antérieurs à la sélection peuvent compléter la fenêtre. La base 100, elle, est recalculée après le filtre car elle doit commencer à 100 sur la sélection.

### Pourquoi 31 prix pour 30 jours de volatilité ?

Chaque rendement exige deux prix successifs. Une série de 31 prix fournit 30 rendements. L'écart-type est calculé sur ces rendements, pas sur les niveaux de prix.

### Le projet prédit-il le marché ?

Non. Les indicateurs résument l'historique ; aucune stratégie, performance prédictive ou rentabilité n'est testée. Les graphiques permettent de comparer et de comprendre les observations.

### Que se passe-t-il après une réponse HTTP 429 ?

La collecte de cet actif échoue sans reprise automatique. Le pipeline continue pour les autres et conserve les données anciennes. L'utilisateur attend puis relance manuellement. Les reprises avancées ont été volontairement reportées.

### Les 18 tests prouvent-ils que tout fonctionne ?

Ils vérifient des comportements définis sur des entrées choisies. Ils ne remplacent ni une collecte authentifiée, ni un test de charge, ni tous les contrôles visuels. Aucune couverture exhaustive n'est revendiquée.

### Comment évoluer vers un usage partagé ?

Commencer par mesurer le besoin : concurrence, volume, fréquence et sécurité. Ajouter ensuite une gestion d'accès, une planification surveillée, des erreurs structurées et éventuellement PostgreSQL. Ne pas complexifier la V1 sans besoin concret.

## 25. Exercices corrigés pour vérifier ton niveau

Exercice 1 : prix 100,105,110. Résultats : rendement initial indisponible, puis 5 % et environ 4,7619 %. Base 100 : 100,105,110. La performance totale est 10 %, pas la somme exacte des deux rendements.

Exercice 2 : sept prix de 100 à 106. La MM7 du dernier jour est 103 ; les six premières sont manquantes. Retirer le quatrième prix : la fenêtre reste incomplète et sa moyenne doit être manquante.

Exercice 3 : comparer deux actifs, A passant de 200 à 220 et B de 50 à 60. Leurs bases finales sont 110 et 120. B progresse davantage relativement même si son prix final reste plus faible. Les dates de début doivent être comparables.

Exercice 4 : prix constant pendant 31 jours. Après initialisation, les rendements valent zéro, la MM7 vaut ce prix et la volatilité vaut zéro. Les premiers résultats restent indisponibles tant que les fenêtres complètes n'existent pas.

Exercice 5 : trois dates chargées deux fois puis correction de la première. Résultat : trois lignes, prix corrigé et collected_at actualisé. Écrire une assertion sur le nombre de lignes et une autre sur le prix ; ne pas seulement vérifier que la commande termine.

Exercice 6 : simuler une réponse 429 avec Mock. Attendre un appel, une erreur et aucune boucle de reprise. Simuler un échec Ethereum après une première collecte valide : attendre partial, ancien prix Ethereum et nouveaux prix des autres actifs.

Exercice 7 : modifier toi-même la MM7 en MM5 dans une branche d'exercice. Mettre à jour le nom de colonne, le graphique, le test et la documentation. Ne publier cette modification que si le périmètre choisi la justifie ; le but est de montrer que tu sais suivre les dépendances.

## 26. Démonstration de cinq minutes et liste de contrôle

Minute 1 : présenter le besoin et préciser que la démo est synthétique. Minute 2 : montrer base 100 puis prix et MM7. Minute 3 : expliquer le calendrier et la volatilité. Minute 4 : montrer la clé SQL et le test d'upsert. Minute 5 : citer les limites et ta prochaine amélioration.

Avant l'entretien, exécuter la démo, ouvrir le serveur et lancer pytest. Préparer les fichiers client, transform, storage, indicators et un test. Garder une capture ou le PDF en cas de problème local. Ne pas dépendre d'un appel réseau réel pour expliquer le nettoyage.

Tu es prêt à présenter la V1 lorsque tu sais expliquer le flux sans lire, calculer les quatre indicateurs simples sur un exemple, retrouver l'upsert, justifier un trou, lire une assertion et modifier une règle avec son test. Aucun besoin de maîtriser une régression ou un RSI retiré du périmètre.

La prochaine étape raisonnable est de valider une collecte réelle avec ta clé, puis d'ajouter un petit test personnel. Plus de graphiques ne sont pas prioritaires. Conserver un périmètre modeste et le défendre précisément apporte une valeur claire sur un CV étudiant.

## 27. Glossaire et références

API REST : interface accessible par requêtes HTTP. Endpoint : adresse d'une ressource. JSON : format textuel de données structurées. Timestamp : valeur représentant un instant. UTC : référence temporelle commune. Snapshot : observation à un instant donné. ETL : extraire, transformer, charger.

DataFrame : tableau pandas. Index : clé des lignes. NaN : valeur numérique manquante en mémoire. NULL : absence de valeur SQL. Clé primaire : identifiant unique d'une ligne. Upsert : insertion ou mise à jour sur conflit. Transaction : groupe d'écritures validé ou annulé. Idempotence : répétition préservant l'état métier attendu.

Rendement : variation relative de prix. Moyenne mobile : moyenne d'une fenêtre glissante. Volatilité : dispersion des rendements selon une définition précisée. Base 100 : normalisation du prix par un prix initial. CI : contrôles automatiques après modification. Mock : objet simulé utilisé pour tester sans service externe.

Référence du comportement : code V1, README, pyproject.toml et tests reproduits en annexe. Documentation fournisseur déjà consultée pour le développement : https://www.coingecko.com/learn/download-bitcoin-historical-data et https://support.coingecko.com/hc/en-us/articles/4538879945625-API-key-can-I-store-the-key-in-my-headers . Les contrats et offres doivent être revérifiés avant une collecte réelle. Les numéros de ligne de l'annexe correspondent à cette édition.
