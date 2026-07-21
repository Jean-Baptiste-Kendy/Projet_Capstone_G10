# Version livrée

Cette archive contient le dashboard **complet et cumulatif**. Il n'existe pas
de version séparée par phase — chaque étape a modifié ce même projet, qui est
donc à jour dans son intégralité.

## ⚠️ Architecture : application single-page (mise à jour la plus récente)

Le dashboard est maintenant une **application single-page** : une seule URL,
une barre d'onglets en haut (façon Power BI/Tableau) qui bascule le contenu
sans rechargement de page — plus de navigation multi-URL comme dans les
premières versions.

## Contenu

- **Fondations** : `app.py`, barre d'onglets (`components/tabbar.py`),
  composants (navbar, footer, filter_bar, kpi_card, chart_panel), chargement
  de données avec cache, charte graphique bleu-pétrole/terracotta.
- **Carte interactive** (choroplèthe, jointure noms) + **Fiche commune**
  (recherche, comparaison nationale).
- **Toutes les données réelles branchées** (35 chemins GitHub vérifiés) :
  IIFT + clusters actifs sur la carte, pages ACP/IIFT, Clustering & AFCM,
  Modélisation supervisée — toutes en layout grille compact (panneaux
  côte à côte, pas un rapport linéaire).
- **Accueil** (storytelling 3 slides), **Méthodologie** (en onglets internes),
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

