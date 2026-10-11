# Parcours pédagogique

1. **Configuration** — une dataclass partage devise, fenêtre, chemins et délais.
   Valider tôt évite une collecte incohérente. La clé est exclue de `repr`.
2. **Client** — `requests` reçoit explicitement paramètres, en-tête et timeout.
   Injecter session et fonction d'attente permet de tester les erreurs sans réseau ni délai.
3. **Transformation** — la jointure sur timestamp évite de mélanger prix et volumes.
   Le bilan qualité documente les rejets et trous ; aucune interpolation ne fabrique un prix.
4. **Stockage** — SQLite garantit l'unicité au niveau SQL, indépendamment de Python.
   Une transaction par crypto empêche un chargement partiel de cette série.
5. **Indicateurs** — `asfreq('D')` matérialise les trous ; `shift(7)` signifie réellement
   sept jours. Une fenêtre pleine et `fill_method=None` empêchent des calculs trompeurs.
6. **Interface** — Streamlit lit la base à chaque interaction, sans requête CoinGecko.
   Plotly permet de zoomer ; l'export conserve les valeurs manquantes.
7. **Tests** — vérifier les résultats calculables à la main et les conséquences d'un échec,
   plutôt que seulement vérifier qu'une fonction s'exécute.
8. **Reproductibilité** — installation depuis pyproject, guide français, démo sans clé et CI.
9. **Planification** — un ordonnanceur lance la même commande que l'humain, avec un dossier
   de travail stable et un stockage persistant ; il ne dépend pas du dashboard ouvert.

Pour un entretien, montrer successivement `client.py`, `transform.py`, la clé primaire
dans `storage.py`, puis les tests de révision et d'échec partiel. Expliquer pourquoi une
variation hebdomadaire ne doit pas utiliser simplement la septième ligne précédente.
