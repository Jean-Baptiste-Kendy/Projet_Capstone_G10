# Version livrée

Cette archive contient le dashboard **complet et cumulatif** (Phases 1 à 4).
Il n'existe pas de version séparée par phase — chaque phase a modifié ce même
projet, qui est donc à jour dans son intégralité.

## Contenu par phase (toutes incluses ici)

- **Phase 1** — Fondations : `app.py`, navigation multi-pages, composants
  (navbar, filter_bar, kpi_card, footer), chargement de données avec cache,
  charte graphique bleu-pétrole/terracotta.
- **Phase 2** — Carte interactive (choroplèthe, jointure noms) + Fiche commune
  (recherche, comparaison nationale).
- **Phase 3** — Toutes les données réelles branchées (35 chemins GitHub
  vérifiés) : IIFT + clusters actifs sur la carte, pages ACP/IIFT,
  Clustering & AFCM, Modélisation supervisée.
- **Phase 4** — Page Accueil (storytelling 3 slides), page Méthodologie,
  durcissement (test de panne réseau simulée), fichiers de déploiement
  (`Procfile`, `.gitignore`, `README.md`).

## Ce qu'il reste à faire (hors dashboard)

1. Renseigner `YOUTUBE_VIDEO_ID` dans `pages/presentation.py`
2. Déployer (Render/Railway) et tester sur un autre réseau avant le 24 juillet
3. Repasser `debug=False` dans `app.py` avant mise en production

## Comment lancer

```bash
pip install -r requirements.txt
python app.py
```
Ouvrir `http://localhost:8050`.
