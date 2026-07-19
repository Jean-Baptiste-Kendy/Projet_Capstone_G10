# Version livrée

Cette archive contient le dashboard **complet et cumulatif** (Phases 1 à 4).
Il n'existe pas de version séparée par phase — chaque phase a modifié ce même
projet, qui est donc à jour dans son intégralité.

## Correctifs post-audit (après relecture complète du projet)

Quatre problèmes identifiés lors d'une relecture indépendante ont été corrigés :

1. **Double chargement des données** — `load_all()` (démarrage) et `get_table()`
   (pages) utilisaient deux caches séparés, donc chaque fichier était téléchargé
   deux fois. Unifiés dans un seul cache (`_TABLE_CACHE`, cf. `data/loaders.py`).
2. **Filtre "Niveau géographique" non fonctionnel** — le radio Pays/Département/
   Commune ne déclenchait aucun callback. Il pilote maintenant réellement
   l'affichage et le filtrage, **avec un niveau Arrondissement ajouté** entre
   Département et Commune (cascade à 4 niveaux, cf. `pages/carte.py`).
3. **`selection-store` non branché** — déplacé dans `app.py` (persistant entre
   pages) et réellement alimenté par le dropdown "Commune" ou un clic direct sur
   la carte ; la page Fiche commune se pré-remplit automatiquement.
4. **Aucun CSS responsive** — 3 points de rupture ajoutés (1024px / 768px / 480px)
   dans `assets/style.css`.

Reformulation également apportée à l'insight Random Forest de la page d'accueil
(le R²=1,00 de Ridge/Lasso y était présenté comme une performance, alors qu'il ne
fait que confirmer que l'IIFT est une combinaison linéaire de ces variables — seul
le R²=0,93 de Random Forest, qui ne voit pas cette formule, valide réellement la
structure de l'indice).

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
