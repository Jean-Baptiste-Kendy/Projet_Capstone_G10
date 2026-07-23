"""
Configuration centrale du dashboard.
Toutes les URLs / chemins de données et constantes de charte graphique
sont définis ici pour éviter les valeurs codées en dur dans les pages.

Chemins mis à jour à partir du README officiel du dépôt
(Jean-Baptiste-Kendy/Projet_Capstone_G10). Les chemins marqués ✅ ont été
testés directement (HTTP 200 + contenu vérifié). Ceux marqués ⚠️ suivent la
structure de dossiers documentée dans le README, mais le nom exact du
fichier à l'intérieur du sous-dossier n'est pas donné dans le README —
à confirmer avec Jean Baptiste (ou lister le dossier sur GitHub) avant la Phase 2.
"""

# ---------------------------------------------------------------------------
# Dépôt GitHub — source unique de vérité
# ---------------------------------------------------------------------------
GITHUB_USER = "Jean-Baptiste-Kendy"
GITHUB_REPO = "Projet_Capstone_G10"
GITHUB_BRANCH = "main"  # ✅ confirmé accessible

GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
)

# ---------------------------------------------------------------------------
# Chemins des données — structure confirmée par le README du dépôt
# ---------------------------------------------------------------------------
PATHS = {
    # ✅ TOUS LES CHEMINS CI-DESSOUS SONT VÉRIFIÉS EXHAUSTIVEMENT le 17/07/2026
    # via téléchargement de l'archive complète du dépôt (codeload.github.com),
    # pas par supposition — la liste de fichiers correspond exactement au repo réel.

    "matrice_globale": f"{GITHUB_RAW_BASE}/data/processed/G10_Matrice_Donnees_Finale.csv",
    "geojson_communes": f"{GITHUB_RAW_BASE}/data/raw/hti_admin_boundaries/hti_admin2.geojson",
    "points_brh_geo_csv": f"{GITHUB_RAW_BASE}/data/processed/G10_points_brh_geo.csv",
    "points_brh_geo_geojson": f"{GITHUB_RAW_BASE}/data/processed/G10_points_brh_geo.geojson",
    "brh_services": f"{GITHUB_RAW_BASE}/data/raw/G10_Donnees2017_Services_Financiers_BRH.xlsx",

    # output/tables/eda_tables/
    "eda_dictionnaire_acp": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_dictionnaire_ACP.csv",
    "eda_dictionnaire_afcm": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_dictionnaire_AFCM.csv",
    "eda_dictionnaire_variables": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_dictionnaire_variables.csv",
    "eda_dictionnaire_variables_actives": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_dictionnaire_variables_actives.csv",
    "matrice_acp": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_matrice_ACP.csv",
    "matrice_afcm": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_matrice_AFCM.csv",
    "matrice_active_eda": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_matrice_active_EDA.csv",

    # output/tables/acp_iift_tables/
    "acp_contributions_variables": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_acp_contributions_variables.csv",
    "acp_coordonnees_variables": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_acp_coordonnees_variables.csv",
    "acp_cos2_variables": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_acp_cos2_variables.csv",
    "acp_scores_communes": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_acp_scores_communes.csv",
    "acp_valeurs_propres": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_acp_valeurs_propres.csv",
    "dictionnaire_iift": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_dictionnaire_IIFT.csv",
    "iift_communes": f"{GITHUB_RAW_BASE}/output/tables/acp_iift_tables/G10_iift_communes.csv",

    # output/tables/clustering_afcm_tables/
    "afcm_valeurs_propres": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_afcm_valeurs_propres.csv",
    "choix_k_kmeans": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_choix_k_kmeans.csv",
    "clustering_resultats": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_clusters_kmeans.csv",
    "communes_representatives_par_cluster": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_communes_representatives_par_cluster.csv",
    "comparaison_kmeans_cha": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_comparaison_kmeans_cha.csv",
    "dictionnaire_clusters": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_dictionnaire_clusters.csv",
    "profil_qualitatif_clusters": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_profil_qualitatif_clusters.csv",
    "profil_quantitatif_clusters": f"{GITHUB_RAW_BASE}/output/tables/clustering_afcm_tables/G10_profil_quantitatif_clusters.csv",

    # output/tables/comparaison_Kmeans_Q_iift_tables/
    "comparaison_kmeans_quartiles_iift": f"{GITHUB_RAW_BASE}/output/tables/comparaison_Kmeans_Q_iift_tables/G10_comparaison_kmeans_quartiles_iift.csv",
    "eta2_kmeans_vs_quartiles": f"{GITHUB_RAW_BASE}/output/tables/comparaison_Kmeans_Q_iift_tables/G10_eta2_kmeans_vs_quartiles_iift.csv",
    "synthese_kmeans_vs_quartiles": f"{GITHUB_RAW_BASE}/output/tables/comparaison_Kmeans_Q_iift_tables/G10_synthese_kmeans_vs_quartiles_iift.csv",
    "tableau_croise_kmeans_quartiles": f"{GITHUB_RAW_BASE}/output/tables/comparaison_Kmeans_Q_iift_tables/G10_tableau_croise_kmeans_quartiles_iift.csv",

    # output/tables/modelisation_importance_variables_tables/
    # ⚠️ Ces 4 fichiers ont un suffixe littéral " (1)" dans leur nom sur le repo
    # (probablement un doublon d'upload) — nécessite un encodage URL (espace -> %20,
    # parenthèses -> %28 %29), déjà géré ci-dessous.
    "modelisation_comparaison": f"{GITHUB_RAW_BASE}/output/tables/modelisation_importance_variables_tables/G10_modelisation_comparaison_modeles%20%281%29.csv",
    "modelisation_importance": f"{GITHUB_RAW_BASE}/output/tables/modelisation_importance_variables_tables/G10_modelisation_importance_variables%20%281%29.csv",
    "modelisation_predictions": f"{GITHUB_RAW_BASE}/output/tables/modelisation_importance_variables_tables/G10_modelisation_predictions_communes%20%281%29.csv",
    "modelisation_variables_lasso_retirees": f"{GITHUB_RAW_BASE}/output/tables/modelisation_importance_variables_tables/G10_modelisation_variables_lasso_retirees%20%281%29.csv",

    "data_dictionary": f"{GITHUB_RAW_BASE}/output/tables/eda_tables/G10_dictionnaire_variables.csv",
}

# ---------------------------------------------------------------------------
# Clé de jointure géographique
# ---------------------------------------------------------------------------
# La matrice de données utilise id_commune (format C-001 à C-140).
# ⚠️ IMPORTANT (vérifié directement sur le geojson) : hti_admin2.geojson n'a
# PAS de colonne id_commune. Ses propriétés sont : adm2_name, adm2_pcode,
# adm1_name, adm0_name, center_lat, center_lon, etc. La jointure carte <-> données
# doit donc passer par une correspondance NOM DE COMMUNE (adm2_name) <-> id_commune,
# exactement comme documenté dans le README (4 corrections manuelles :
# Estère <-> L'Estère, Cornillon <-> Cornillon / Grand Bois, etc.)
#
# Si vous disposez d'un CSV de correspondance déjà exporté (id_commune <-> adm2_name),
# ajoutez son chemin dans PATHS ci-dessus sous "correspondance_communes" et utilisez-le
# pour fusionner avant de construire le choroplèthe. Sinon, la jointure peut être
# refaite directement dans loaders.py à partir de nom_commune (présent dans la
# matrice finale) <-> adm2_name (dans le geojson), avec les mêmes 4 corrections.
ID_COMMUNE_COL = "id_commune"
NOM_COMMUNE_COL = "nom_commune"        # présent dans G10_Matrice_Donnees_Finale.csv
DEPARTEMENT_COL = "departement"
ARRONDISSEMENT_COL = "arrondissement"  # présent dans G10_Matrice_Donnees_Finale.csv (source IHSI)
GEOJSON_NAME_PROPERTY = "adm2_name"    # ✅ confirmé par inspection directe du geojson
GEOJSON_PCODE_PROPERTY = "adm2_pcode"  # code administratif OCHA, alternative possible

# Corrections manuelles de noms (vérifiées le 15/07/2026 par comparaison directe
# matrice <-> geojson : 63/67 écarts résolus par normalisation accents/tirets,
# ces 4 restants correspondent exactement aux "4 corrections manuelles" du README)
CORRESPONDANCE_NOMS_MANUELLE = {
    # "nom_dans_matrice": "nom_dans_geojson (adm2_name, valeur exacte)"
    "Chansolme": "Chamsolme",                # coquille dans le geojson OCHA
    "Cornillon": "Cornillon / Grand Bois",
    "Estère": "L'Estere",
    "La Vallée de Jacmel": "La Vallee",
}

# ---------------------------------------------------------------------------
# Charte graphique — bleu-pétrole / terracotta
# ---------------------------------------------------------------------------
COLORS = {
    "petrole_900": "#0F2E38",   # texte / navbar foncé
    "petrole_700": "#1B4B5A",   # couleur principale
    "petrole_500": "#2C6E7F",   # accents secondaires, hover
    "petrole_200": "#B9D4D9",   # fonds légers, zones désactivées
    "terracotta_700": "#B14A22",  # accent fort (alertes, CTA)
    "terracotta_500": "#C1622D",  # accent principal
    "terracotta_300": "#E0A87C",  # accent doux, highlights
    "background": "#F6F4EF",     # fond général (crème neutre, pas blanc pur)
    "surface": "#FFFFFF",        # cartes / panneaux
    "text_primary": "#1F2D30",
    "text_secondary": "#5B6B6E",
    "border": "#DDE3E1",
    "success": "#4C7A5E",
    "warning": "#C1622D",
}

# Palette discrète pour les 3 clusters (cohérente avec la charte)
# Sémantique vérifiée sur les données réelles (clusters_kmeans.csv x iift_communes.csv)
# ET alignée sur le rapport (Section 2 — Wilson) :
#   Cluster 0 : Dim1 moy. -1,95 | IIFT moy. 13 | n=74
#   Cluster 2 : Dim1 moy.  0,68 | IIFT moy. 33 | n=49
#   Cluster 1 : Dim1 moy.  6,53 | IIFT moy. 75 | n=17
#
# L'écart Cluster 2 -> Cluster 1 (5,85 sur Dim1) est plus du double de l'écart
# Cluster 0 -> Cluster 2 (2,63) : le cluster 1 n'est pas "juste un cran
# au-dessus" du 2, c'est un isolat statistique nettement détaché du reste.
# D'où "Extrême" (et non "Élevé") pour rester cohérent avec le rapport, qui
# capture bien cet écart plutôt qu'une fausse progression régulière à 3 marches
# égales.
CLUSTER_COLORS = {
    "0": "#C1622D",   # exclusion -> terracotta (signal d'alerte/priorité d'intervention)
    "1": "#1B4B5A",   # avancé -> bleu-pétrole foncé (pôle fort)
    "2": "#2C6E7F",   # émergent -> bleu-pétrole clair (palier intermédiaire)
}

# Statistiques réelles par cluster (source : G10_clusters_kmeans.csv x
# G10_iift_communes.csv), réutilisées pour construire CLUSTER_LABELS et
# disponibles séparément pour tout affichage qui a besoin des chiffres bruts
# plutôt que du libellé déjà formaté.
CLUSTER_STATS = {
    "0": {"dim1_moyen": -1.95, "iift_moyen": 13, "effectif": 74},
    "2": {"dim1_moyen": 0.68, "iift_moyen": 33, "effectif": 49},
    "1": {"dim1_moyen": 6.53, "iift_moyen": 75, "effectif": 17},
}

# Format volontairement "Terminologie financière courte — détail statistique",
# séparés par un tiret cadratin (—) : plusieurs pages (clustering_afcm.py)
# font `CLUSTER_LABELS[k].split("—")[0].strip()` pour n'afficher que le terme
# court dans les tableaux compacts — NE PAS retirer ce séparateur ni changer
# sa position sans mettre à jour ces appels.
#
# Terminologie alignée sur le vocabulaire standard de l'inclusion financière
# (Banque Mondiale, CGAP, BID) plutôt que sur des étiquettes génériques
# "Cluster 0/1/2", illisibles pour un public non technique (jury, décideurs).
# Ordre du dict volontairement 0 -> 2 -> 1 (par sévérité croissante, pas par
# identifiant numérique brut) : c'est cet ordre qui pilote category_orders
# dans les graphiques (clustering_afcm.py, carte.py) — les 3 clusters
# apparaissent donc dans le bon sens de lecture partout, pas dans l'ordre 0/1/2.
CLUSTER_LABELS = {
    "0": (
        "Zones d'exclusion financière — Classe IIFT Très faible "
        "(IIFT moy. 13 ; Dim1 moy. -1,95 ; n=74)"
    ),
    "2": (
        "Zones d'inclusion financière émergente — Classe IIFT Moyen "
        "(IIFT moy. 33 ; Dim1 moy. 0,68 ; n=49)"
    ),
    "1": (
        "Pôles d'inclusion financière avancée — Classe IIFT Extrême "
        "(IIFT moy. 75 ; Dim1 moy. 6,53 ; n=17)"
    ),
}

# Version courte (sans les statistiques), pour les espaces très compacts
# (badges, puces de légende étroite) où même le libellé tronqué par
# split("—")[0] serait encore trop long. Valeurs IDENTIQUES mot pour mot à
# CLUSTER_LABELS[k].split("—")[0].strip() — vérifié par assertion en tests
# manuels : un même cluster ne doit jamais porter deux formulations
# légèrement différentes selon la page consultée.
CLUSTER_LABELS_COURT = {
    "0": "Zones d'exclusion financière",
    "2": "Zones d'inclusion financière émergente",
    "1": "Pôles d'inclusion financière avancée",
}

# Échelle séquentielle à teinte unique pour les 5 classes IIFT (ordinal :
# Très faible -> Très élevé). Dégradé du bleu-pétrole clair au foncé, 5 pas
# régulièrement espacés entre petrole_200 et petrole_900 — corrige l'ancienne
# palette qui mélangeait terracotta (2 premières classes) et petrole (3
# suivantes), ce qui donnait l'illusion visuelle de 2 groupes plutôt qu'un
# dégradé ordonné à 5 niveaux.
CLASSE_IIFT_ORDER = ["Très faible", "Faible", "Moyen", "Élevé", "Très élevé"]
CLASSE_IIFT_COLORS = ["#B9D4D9", "#8FABB1", "#648189", "#3A5860", "#0F2E38"]

# Indicateurs pour lesquels une valeur supérieure à la moyenne nationale est
# défavorable (sens inverse des autres indicateurs d'inclusion). Utilisé par
# la Fiche Commune pour colorer correctement l'écart à la moyenne (vert/teal
# = favorable, terracotta = défavorable), quel que soit le sens de
# l'indicateur.
INVERSE_INDICATORS = {"taux_pauvrete_proxy", "indice_privation_spatiale"}

# Typographie (chargée via Google Fonts dans assets/style.css)
FONTS = {
    "display": "'IBM Plex Sans', sans-serif",
    "body": "'Inter', sans-serif",
    "mono": "'IBM Plex Mono', monospace",  # pour les indicateurs chiffrés
}

# ---------------------------------------------------------------------------
# Métadonnées du projet (réutilisées dans plusieurs pages)
# ---------------------------------------------------------------------------
PROJECT_TITLE = (
    "Analyse territoriale de l'inclusion financière en Haïti : "
    "segmentation des communes et cartographie des disparités "
    "d'accès aux services financiers"
)
COHORTE = "FRST/SDMIA — Cohorte 2025"
EQUIPE = "Groupe 10 : Jean Baptiste Kendy, Louis Wilson Junior, Jonathan François Alcena"
SUPERVISEUR = "ING Evens Toussaint"
DATE_SOUTENANCE = "24 juillet 2026"

N_COMMUNES = 140
N_CLUSTERS = 3

# ---------------------------------------------------------------------------
# Libellés lisibles pour les indicateurs numériques de la matrice finale
# (utilisés dans les dropdowns de la carte et la fiche commune)
# ---------------------------------------------------------------------------
INDICATOR_LABELS = {
    "IIFT": "Indice IIFT (0-100)",
    "taux_compte_formel": "Taux de compte formel (%)",
    "taux_compte_mobile": "Taux de compte mobile (%)",
    "taux_utilisation_OTA": "Taux d'utilisation OTA (%)",
    "taux_connaissance_banque": "Connaissance des banques (%)",
    "taux_satisfaction_banque": "Satisfaction bancaire (%)",
    "taux_epargne_formelle": "Épargne formelle (%)",
    "taux_endettement_formel": "Endettement formel (%)",
    "taux_telephone_mobile": "Accès téléphone mobile (%)",
    "taux_internet": "Accès Internet (%)",
    "taux_pauvrete_proxy": "Pauvreté (proxy) (%)",
    "indice_privation_spatiale": "Indice de privation spatiale",
    "densite_bancaire_10k": "Densité bancaire (pour 10k hab.)",
    "densite_hab_km2": "Densité de population (hab/km²)",
    "part_urbaine": "Part de population urbaine (%)",
    "nb_types_services": "Nombre de types de services financiers",
    "brh_total_effectif": "Nb total de points de service (BRH)",
    "population_totale": "Population totale",
    "taille_moyenne_menage": "Taille moyenne des ménages",
}

# Indicateurs catégoriels (rendus en couleurs discrètes sur la carte, pas continues)
CATEGORICAL_INDICATORS = {
    "cluster_kmeans": "Cluster K-Means (typologie, K=3)",
    "classe_IIFT": "Classe IIFT (quantiles)",
}

# Indicateur par défaut affiché sur la carte au chargement
DEFAULT_MAP_INDICATOR = "IIFT"

# Points de service BRH 2017 : regroupement des 26 variables du classeur brut
# en six familles de prestataires. Les colonnes calculées sont jointes à la
# matrice de la carte dans data/loaders.py et peuvent donc être agrégées à tous
# les niveaux administratifs (pays, département, arrondissement, commune).
GROUPES_SERVICES = {
    "Maison de Transfert": [
        "mt_agence_sogexpress", "mt_agence_unitransfer",
        "mt_agent_unitransfer", "mt_agent_capital_transfert",
        "mt_agent_sogexpress", "mt_agent_rapide_transfer",
    ],
    "Agent Non Bancaire": ["anb_moncash_digicel", "anb_lajancash_haitipay"],
    "Banque": [
        "bc_agence_unibank", "bc_agence_sogebank",
        "bc_agence_banca_nac_credit", "bc_agence_capital_bank",
        "bc_agence_union_haitienne", "bc_agence_autres_banques",
    ],
    "ATM": ["bc_atm_sogebank", "bc_atm_unibank"],
    "Microfinance": [
        "imf_fonkoze", "imf_micro_credit_national", "imf_acme",
        "imf_sogesol", "imf_micro_credit_capital", "imf_finca_haiti",
        "imf_initiative_developpement", "imf_fhaf", "imf_autres",
    ],
    "Caisse Populaire": ["cp_autres_caisses_populaires"],
}

BRH_SERVICE_INDICATOR_LABELS = {
    "brh_total_points": "Points de service BRH — Total",
    "brh_maison_transfert": "Points BRH — Maison de transfert",
    "brh_agent_non_bancaire": "Points BRH — Agent non bancaire",
    "brh_banque": "Points BRH — Banque",
    "brh_atm": "Points BRH — ATM",
    "brh_microfinance": "Points BRH — Microfinance",
    "brh_caisse_populaire": "Points BRH — Caisse populaire",
}

OFFER_INDICATOR_LABELS = {
    "brh_total_effectif": "Nb de points d'accès",
    "densite_bancaire_10k": "Nb de points d'accès pour 10 000 habitants",
    "brh_maison_transfert": "Points — Maison de transfert",
    "brh_agent_non_bancaire": "Points — Agent non bancaire",
    "brh_banque": "Points — Banque",
    "brh_atm": "Points — ATM",
    "brh_microfinance": "Points — Microfinance",
    "brh_caisse_populaire": "Points — Caisse populaire",
}

DEMAND_INDICATOR_LABELS = {
    "part_rurale_superficie_pct": "% rurale (par superficie)",
    "part_rurale_population_pct": "% rurale (par population)",
    "part_urbaine_superficie_pct": "% urbaine (par superficie)",
    "part_urbaine_pct": "% urbaine (par population)",
    "taille_moyenne_menage": "Taille moyenne des ménages",
    "taille_moyenne_menage_rurale": "Taille moyenne des ménages (rural)",
    "taille_moyenne_menage_urbaine": "Taille moyenne des ménages (urbain)",
    "superficie_km2": "Superficie (km²)",
    "superficie_rurale_km2": "Superficie rurale (km²)",
    "superficie_urbaine_km2": "Superficie urbaine (km²)",
    "nb_menages": "Nb de ménages",
    "nb_menages_ruraux": "Nb de ménages ruraux",
    "nb_menages_urbains": "Nb de ménages urbains",
    "population_totale": "Population totale",
    "pop_feminine": "Population (femmes)",
    "pop_masculine": "Population (hommes)",
    "population_rurale": "Population (rurale)",
    "pop_feminine_rurale": "Population (rurale, femmes)",
    "pop_masculine_rurale": "Population (rurale, hommes)",
    "population_urbaine": "Population (urbaine)",
    "pop_feminine_urbaine": "Population (urbaine, femmes)",
    "pop_masculine_urbaine": "Population (urbaine, hommes)",
    "population_18_plus": "Population 18+",
    "population_18_plus_rurale": "Population 18+ (rurale)",
    "population_18_plus_urbaine": "Population 18+ (urbaine)",
    "densite_population_totale": "Densité population (pop. / km²)",
    "densite_population_rurale": "Densité population (rurale, pop. / km²)",
    "densite_population_urbaine": "Densité population (urbaine, pop. / km²)",
    "ratio_genre": "Ratio genre (hommes pour 100 femmes)",
    "ratio_genre_rural": "Ratio genre (rural, hommes pour 100 femmes)",
    "ratio_genre_urbain": "Ratio genre (urbain, hommes pour 100 femmes)",
}

SUM_INDICATORS = {
    "brh_total_effectif", *BRH_SERVICE_INDICATOR_LABELS,
    "superficie_km2", "superficie_rurale_km2", "superficie_urbaine_km2",
    "nb_menages", "nb_menages_ruraux", "nb_menages_urbains",
    "population_totale", "pop_feminine", "pop_masculine", "population_rurale",
    "pop_feminine_rurale", "pop_masculine_rurale", "population_urbaine",
    "pop_feminine_urbaine", "pop_masculine_urbaine", "population_18_plus",
    "population_18_plus_rurale", "population_18_plus_urbaine",
}
