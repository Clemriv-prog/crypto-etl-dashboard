# V1 : parcours d'apprentissage en quatre semaines

Objectif : comprendre la chaîne API → pandas → SQLite → dashboard. Le code livré est une
base de travail réalisée avec assistance IA ; refaire les étapes soi-même permet de l'expliquer.

## Semaine 1 - extraire et nettoyer

Lire `config.py` et `client.py`. Identifier URL, paramètres, en-tête et timeout.
Observer une réponse simulée dans `tests/test_core.py`, puis suivre `transform.py`.
Expliquer la différence entre un timestamp et une date UTC. Supprimer un jour dans un
exemple et montrer qu'il n'est pas inventé. Vérifier les prix négatifs, nuls et infinis.

## Semaine 2 - stocker sans doublons

Lire `storage.py` : les deux tables, la clé composite et ON CONFLICT DO UPDATE.
Charger deux fois trois observations puis corriger un prix. Vérifier qu'il reste trois lignes.
Lire `pipeline.py` : archives, boucle par crypto, statut global et conservation en cas d'échec.
Une transaction couvre un actif ; les autres peuvent réussir si celui-ci échoue.

## Semaine 3 - calculer et visualiser

Lire `indicators.py`, puis refaire à la main 100 → 105 : rendement 5 %.
Pour 100,101,102,103,104,105,106, la MM7 vaut 103.
Expliquer `asfreq("D")`, les fenêtres complètes et les valeurs manquantes.
La volatilité est l'écart-type de 30 rendements en pourcentage, non annualisé, ddof=1.
Lire `dashboard/app.py` et relier chaque graphique à sa colonne.

## Semaine 4 - vérifier et présenter

Lancer pytest et Ruff. Expliquer au moins trois tests : calcul, doublon, erreur API.
Changer une règle simple puis adapter son test. Préparer une démonstration de cinq minutes :
besoin, chaîne de données, graphiques, chargement sans doublon, limites.
Les données de démonstration sont synthétiques. La collecte réelle exige une clé et reste
à valider avec elle. Une erreur HTTP ne déclenche pas de reprise automatique dans cette V1.

## Questions à savoir traiter en entretien

- Pourquoi SQLite ? Petit stockage local, contraintes et transactions sans serveur.
- Pourquoi la clé contient-elle la devise ? Un même actif peut avoir plusieurs prix par date.
- Pourquoi ne pas combler les prix absents ? Ne pas fabriquer de rendements et de volatilité.
- Pourquoi 31 prix pour la volatilité ? Ils donnent 30 variations quotidiennes.
- Pourquoi calculer la MM avant le filtre ? Utiliser l'historique antérieur disponible.
- Que se passe-t-il si une crypto échoue ? Les anciennes données restent, statut partiel.
- Que prouvent les tests ? Des comportements ciblés, pas l'absence de tout bug.

## Extensions reportées

RSI, régression, motifs, corrélations, drawdown, planification et reprises HTTP avancées.
Ajouter une extension seulement après avoir compris, expliqué et testé la V1.
