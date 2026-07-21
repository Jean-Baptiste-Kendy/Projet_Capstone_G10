# Dashboard — Inclusion Financière en Haïti (Capstone G10)

Application web Dash présentant les résultats du projet : IIFT, clustering K-Means,
AFCM et modélisation supervisée, sur les 140 communes d'Haïti.

## Lancement local

```bash
pip install -r requirements.txt
python app.py
```
Puis ouvrir `http://localhost:8050`.

## Structure

```
app.py                  # point d'entrée, layout global, dispatch des onglets
pages/                  # une fonction layout() par section (appelée par app.py)
components/
  navbar.py              # bandeau de marque
  tabbar.py              # barre d'onglets principale (navigation)
  filter_bar.py          # filtres partagés (page Carte)
  kpi_card.py            # cartes KPI
  chart_panel.py         # panneau de visualisation (grille façon Power BI)
  footer.py
data/
  config.py             # chemins GitHub raw + charte graphique (source unique de vérité)
  loaders.py             # chargement + cache des tables, jointure carte<->données
assets/
  style.css              # charte bleu-pétrole / terracotta + grille + onglets
```

Application **single-page** : une seule URL, une barre d'onglets en haut
bascule le contenu (pas de navigation par URL séparée).

## Principe de robustesse

Toutes les données sont chargées depuis le dépôt GitHub
(`Jean-Baptiste-Kendy/Projet_Capstone_G10`, branche `main`) via `raw.githubusercontent.com`.
Si une table est indisponible (réseau coupé, fichier renommé), la page correspondante
affiche un message d'erreur clair au lieu de faire planter le serveur — testé et
validé y compris en cas de panne réseau totale.

## Déploiement

Un `Procfile` est fourni pour Render/Railway (`gunicorn app:server`). Penser à :
- Désactiver `debug=True` dans `app.py` avant la mise en production
- Tester le déploiement sur un réseau différent de la machine de développement,
  avant la soutenance

## Points restant à compléter

- `pages/presentation.py` : renseigner `YOUTUBE_VIDEO_ID` une fois la vidéo en ligne
  (ou déposer `assets/presentation.mp4` comme fallback local)
