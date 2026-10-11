# Mise à jour quotidienne locale

La planification est une procédure à appliquer, aucune tâche système n'est créée automatiquement.
Éviter deux collectes simultanées. SQLite peut refuser un accès concurrent ; relancer ensuite.
Ne pas mettre la clé dans la commande, le script versionné ou les arguments du planificateur.

## Windows

1. Définir `COINGECKO_API_KEY` dans les variables d'environnement du compte utilisateur,
   via les paramètres Windows. Redémarrer la session si nécessaire.
2. Dans le Planificateur de tâches, créer une tâche quotidienne à **03:00 UTC**, ou choisir
   une heure locale après disponibilité des données. Attention aux changements d'heure.
3. Programme : chemin absolu de `.venv\Scripts\python.exe` dans ce projet.
4. Arguments : `-m crypto_etl.cli update`.
5. « Démarrer dans » : chemin absolu du dossier `crypto-etl`.
6. Utiliser le compte qui possède la variable et les droits d'écriture sur `data`.
   Empêcher le lancement d'une nouvelle instance si une instance tourne déjà.
7. Lancer manuellement la tâche, puis consulter `pipeline_runs` dans SQLite ou le dashboard.
   Code de sortie 0 : succès ; 1 : échec total ou partiel ; 2 : configuration CLI manquante.

## Linux

Créer un wrapper **hors dépôt**, lisible seulement par son propriétaire (`chmod 700`),
qui charge la clé depuis un fichier privé (`chmod 600`) puis exécute :

```sh
cd /chemin/absolu/crypto-etl || exit 1
exec .venv/bin/python -m crypto_etl.cli update
```

Ajouter avec `crontab -e`, en adaptant les chemins et le fuseau du système :

```cron
0 3 * * * /usr/bin/flock -n /chemin/absolu/crypto-etl/data/update.lock /chemin/prive/update-crypto.sh >> /chemin/absolu/crypto-etl/data/update.log 2>&1
```

Créer `data/` avant le premier lancement. La ligne correspond à 03:00 dans le fuseau de cron,
pas forcément UTC. Tester le wrapper sous le compte de cron. Sauvegarder régulièrement la
base à l'aide de l'API `sqlite3.Connection.backup`, afin de garantir une copie cohérente.
