# Analyse territoriale de l'inclusion financière en Haïti : segmentation des communes et cartographie des disparités d'accès aux services financiers

**Capstone Groupe 10 (G10) — Programme FRST/SDMIA, Faculté des Sciences, Université d'État d'Haïti (UEH)**

---

## 🎯 Objectif du projet

Ce projet vise à **identifier et cartographier les zones d'exclusion financière** sur l'ensemble des 140 communes d'Haïti, à partir d'une analyse géospatiale combinée à une classification multivariée (AFCM, indice cible IIFT, clustering K-Means/CHA, modélisation supervisée). L'objectif final est de produire un outil d'aide à la décision — incluant une application web interactive — pouvant guider des choix de **politique publique** (priorisation de zones à désenclaver) ou des **décisions commerciales** (implantation de nouveaux points de service financier).

Le projet complet est découpé en plusieurs notebooks (voir [Structure du projet](#️-structure-du-projet-plusieurs-notebooks)). **Ce notebook-ci ne réalise ni l'AFCM, ni le clustering, ni la modélisation** : il produit uniquement le dictionnaire de données finales — la matrice consolidée, nettoyée et documentée — qui sera utilisée par les notebooks d'analyse à venir.

---

## ⚠️ Note importante sur l'origine des données

**Les données de services financiers (BRH) utilisées dans ce projet n'ont pas été obtenues directement auprès des institutions concernées.** Elles ont été **collectées manuellement** par l'équipe à partir :
- du **tableau de bord public en ligne de la BRH** (relevé manuel, poste par poste, commune par commune) ;
- de **rapports et cartographies publiées** (Banque Mondiale, BID) pour les variables contextuelles et de pauvreté.

Il ne s'agit donc **pas d'un extrait officiel fourni par une institution**, mais d'une **reconstitution manuelle à partir de sources publiques disponibles**. Cette limite est documentée de façon transparente dans le notebook et doit être rappelée dans toute utilisation ou diffusion de ces résultats. Certaines variables (pauvreté, privation spatiale, contexte WBG) sont explicitement des **proxys** reconstruits par lecture visuelle de cartes à quantiles, et non des statistiques officielles publiées commune par commune.

---

## 🗂️ Sources de données

| Fichier | Contenu | Origine | Rôle |
|---|---|---|---|
| `G10_Donnees2017_Services_Financiers_BRH.xlsx` | 29 variables brutes de services financiers (2017) | **Collecte manuelle** depuis le tableau public BRH | Offre de services par commune |
| `population_commune_IHSI2024_G10.xlsx` | Démographie officielle | IHSI 2024 | Population, ménages, superficie |
| `data/hti_admin_boundaries/hti_admin2.geojson` | Limites administratives communales (140 communes) | OCHA COD-AB | Géolocalisation, découpage territorial — **seul fichier du dossier `hti_admin_boundaries/` utilisé dans ce notebook** (le dossier contient aussi les niveaux admin0/1/3, capitales, lignes et points, conservés pour un usage cartographique futur) |
| `base_communes_proxy_pauvrete_privation.xlsx` | Pauvreté / privation spatiale (proxy) | Reconstruit à partir du rapport *Groupe de la Banque Mondiale (2022)*, basé sur la carte de pauvreté BID / Pokhriyal et al. (2014) | Contexte socio-économique (variables proxy) |
| Rapport *Enquête sur la Capacité et l'Inclusion Financière — Banque Mondiale, Haïti 2017* | Zones/strates WBG | Captures manuelles du rapport | Variables contextuelles (WBG 2017) |

Toutes les sources sont croisées sur les **140 communes d'Haïti** (découpage IHSI 2024).

---

## 🗃️ Structure du projet (plusieurs notebooks)

Ce dépôt est organisé en **plusieurs notebooks**, chacun responsable d'une étape distincte du pipeline. D'après la feuille de route du projet :

| Notebook / Étape | Rôle |
|---|---|
| **`G10_Creation_Dictionnaire_Donnees.ipynb`** *(ce notebook)* | Import, nettoyage, géolocalisation et fusion de toutes les sources (BRH, IHSI, geojson, WBG, pauvreté) pour produire le **dictionnaire de données finales** |
| *(à venir)* EDA & visualisation | Analyse exploratoire et visualisation des disparités territoriales |
| *(à venir)* AFCM & IIFT | Implémentation de l'AFCM et calcul de l'indice cible (IIFT) |
| *(à venir)* Clustering | K-Means & CHA, profilage des communes |
| *(à venir)* Comparaison de modèles | K-Means vs modèle de référence simple (quartiles) |
| *(à venir)* Modélisation supervisée | Ridge/Lasso/Random Forest & analyse de l'importance des variables (feature importance) |

D'autres livrables du projet (hors notebooks à proprement parler) sont également prévus en Phase 3 : une **application web interactive** (Dash/Plotly), un **rapport final**, le **dictionnaire de données définitif**, ainsi que le support de présentation.

> Le clustering, l'AFCM/IIFT et la modélisation supervisée ne sont **pas exécutés** dans ce notebook : celui-ci se limite à produire une matrice finale propre, documentée et prête à l'emploi pour les notebooks d'analyse suivants.

## 🧭 Structure du notebook `G10_Creation_Dictionnaire_Donnees.ipynb`

| Section | Contenu | Sortie principale |
|---|---|---|
| **0** | Installation & imports (`geopandas`, `pandas`, `shapely`, `requests`, `openpyxl`) | — |
| **1** | Chemins des fichiers sources | — |
| **2** | Import brut BRH (Excel) + IHSI (Excel) | `df_brh`, `df_ihsi` |
| **3** | Géolocalisation des prestataires BRH (génération de points GPS communaux) + jointure avec `hti_admin2.geojson` | `gdf_brh_geo` → CSV/GeoJSON |
| **4** | Jointure exacte BRH ↔ IHSI sur `id_commune` | `matrice_brh_ihsi` |
| **5** | Variables contextuelles WBG 2017 (6 strates urbain/rural × zone) | `matrice` |
| **5E–5H** | Construction et documentation des variables qualitatives candidates pour une future AFCM (discrétisation, typologie des profils de services, proposition de séparation variables actives/supplémentaires) | `matrice` enrichie |
| **6** | Table finale + export du dictionnaire de données | Fichier consolidé (matrice + description des variables) |
| **7** | Méthodologie, limites et variables recherchées mais non disponibles | Documentation |

### Principes méthodologiques clés
- **Jointures exactes uniquement** sur `id_commune` (`how='inner'`, `validate='1:1'`) entre fichiers qui partagent cette clé.
- **Correspondance par nom** utilisée seulement quand `id_commune` est absent (ex. `hti_admin2.geojson`), avec **4 corrections manuelles documentées** (ex. `Estère` ↔ `L'Estère`, `Cornillon` ↔ `Cornillon / Grand Bois`).
- **Aucune correspondance floue à l'exécution** : toute correction de nom de commune est vérifiée et figée manuellement.
- **Bruit gaussien calibré (σ = 15 %, seed = 42)** appliqué aux variables WBG dérivées de groupes, pour éviter des valeurs strictement identiques entre communes d'un même groupe — stratégie hybride réel + synthétique calibré, documentée comme telle.
- **Séparation variables actives / supplémentaires** pour l'AFCM, afin d'éviter que des variables redondantes (urbain/rural répété sous plusieurs formes) ne dominent artificiellement les premiers axes factoriels.

---

## 📉 Limites méthodologiques principales

- Données BRH collectées **manuellement**, non issues d'un export institutionnel officiel.
- Seuil urbain/rural (50 %) : choix méthodologique, pas une valeur officielle IHSI/WBG.
- Variables de pauvreté/privation spatiale : **proxys visuels**, pas des statistiques certifiées.
- Points GPS des prestataires BRH : placement approximatif (centroïde communal ± bruit, ou réseau routier via Overpass en option) — valide pour l'appartenance communale, pas pour une précision cartographique fine.
- Variables recherchées mais **non disponibles** : couverture réseau mobile par commune (2G/3G/4G), taux d'alphabétisation par commune, IPM officiel complet (seules 11 valeurs réelles identifiées via un rapport BID, le reste étant une reconstruction proxy).

La liste complète des limites, avec leur impact et leur traitement, est documentée section par section dans le notebook (Section 7).

---

## 🛠️ Stack technique

- **Python** : `pandas`, `numpy`, `geopandas`, `shapely`, `requests`
- **Visualisation** : `matplotlib`
- **Analyse multivariée** : `prince` (AFCM / MCA)
- Environnement : Google Colab (avec repli local si Colab non détecté)

---

## 📁 Structure du dépôt

```
├── G10_Creation_Dictionnaire_Donnees.ipynb   # Ce notebook : préparation des données + dictionnaire final
├── (notebooks à venir : EDA, AFCM/IIFT, Clustering, Comparaison de modèles, Modélisation supervisée)
├── (application web Dash/Plotly à venir)
├── data/
│   ├── hti_admin_boundaries/
│   │   ├── hti_admin0.geojson / hti_admin0_em.geojson     # Frontière nationale
│   │   ├── hti_admin1.geojson / hti_admin1_em.geojson     # Départements
│   │   ├── hti_admin2.geojson / hti_admin2_em.geojson     # Communes (140) — utilisé dans ce notebook
│   │   ├── hti_admin3.geojson / hti_admin3_em.geojson     # Sections communales
│   │   ├── hti_admincapitals.geojson                       # Chefs-lieux
│   │   ├── hti_adminlines.geojson / hti_adminlines_em.geojson  # Lignes de délimitation
│   │   └── hti_adminpoints.geojson                          # Points de repère administratifs
│   ├── G10_Donnees2017_Services_Financiers_BRH.xlsx
│   ├── population_commune_IHSI2024_G10.xlsx
│   └── base_communes_proxy_pauvrete_privation.xlsx
├── outputs/                                   # Exports (CSV, GeoJSON, dictionnaire de données finales)
└── README.md
```

> Structure indicative — à ajuster au fur et à mesure de l'ajout des notebooks d'analyse et de l'application web.

---

## 👥 Équipe

Projet réalisé dans le cadre du Capstone Groupe 10, programme FRST/SDMIA, Faculté des Sciences, Université d'État d'Haïti.

---

## 📌 Avertissement

Ce travail est un exercice académique de recherche appliquée réalisé avec des contraintes réelles d'accès aux données en Haïti. Les résultats doivent être interprétés en tenant compte des limites documentées ci-dessus, en particulier la nature manuelle de la collecte des données BRH et le caractère proxy de certaines variables socio-économiques.
