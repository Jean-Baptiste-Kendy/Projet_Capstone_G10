"""
Chargement centralisé des données.

Principe de robustesse : chaque table est chargée UNE SEULE FOIS au démarrage
du serveur (grâce à lru_cache), jamais recalculée dans un callback. Les
callbacks ne font que filtrer/agréger des DataFrames déjà en mémoire.

Chaque loader a un fallback explicite : si le chargement échoue (repo
inaccessible, fichier renommé...), on lève une erreur claire au démarrage
plutôt qu'un crash silencieux pendant la démo.
"""

import io
import json
import logging
import re
import unicodedata
from functools import lru_cache

import pandas as pd
import requests

from data.config import (
    PATHS,
    ID_COMMUNE_COL,
    NOM_COMMUNE_COL,
    GEOJSON_NAME_PROPERTY,
    CORRESPONDANCE_NOMS_MANUELLE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("loaders")

REQUEST_TIMEOUT = 15  # secondes — évite un blocage indéfini si GitHub est lent


class DataLoadError(Exception):
    """Erreur explicite de chargement, avec le nom de la table concernée."""
    pass


def _safe_read_csv(url: str, label: str) -> pd.DataFrame:
    """Charge un CSV depuis une URL avec gestion d'erreur explicite (timeout inclus)."""
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        logger.info(f"[OK] {label} chargé : {df.shape[0]} lignes x {df.shape[1]} colonnes")
        return df
    except Exception as e:
        logger.error(f"[ÉCHEC] Impossible de charger '{label}' depuis {url} : {e}")
        raise DataLoadError(
            f"Échec du chargement de '{label}'. Vérifiez l'URL dans data/config.py "
            f"et la disponibilité du repo GitHub. Détail : {e}"
        ) from e


def _safe_read_geojson(url: str, label: str) -> dict:
    """Charge un GeoJSON depuis une URL avec gestion d'erreur explicite."""
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        geojson = resp.json()
        n_features = len(geojson.get("features", []))
        logger.info(f"[OK] {label} chargé : {n_features} features")
        return geojson
    except Exception as e:
        logger.error(f"[ÉCHEC] Impossible de charger '{label}' depuis {url} : {e}")
        raise DataLoadError(
            f"Échec du chargement de '{label}'. Vérifiez l'URL dans data/config.py "
            f"et la disponibilité du repo GitHub. Détail : {e}"
        ) from e


# ---------------------------------------------------------------------------
# Loaders individuels — chacun mis en cache (appelé une seule fois par process)
# Utiles pour un accès ciblé depuis une page sans recharger tout `load_all()`
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_matrice_globale() -> pd.DataFrame:
    return _safe_read_csv(PATHS["matrice_globale"], "matrice_globale")


@lru_cache(maxsize=1)
def load_matrice_acp() -> pd.DataFrame:
    return _safe_read_csv(PATHS["matrice_acp"], "matrice_acp")


@lru_cache(maxsize=1)
def load_matrice_afcm() -> pd.DataFrame:
    return _safe_read_csv(PATHS["matrice_afcm"], "matrice_afcm")


@lru_cache(maxsize=1)
def load_clustering_resultats() -> pd.DataFrame:
    return _safe_read_csv(PATHS["clustering_resultats"], "clustering_resultats")


@lru_cache(maxsize=1)
def load_modelisation_predictions() -> pd.DataFrame:
    return _safe_read_csv(PATHS["modelisation_predictions"], "modelisation_predictions")


@lru_cache(maxsize=1)
def load_modelisation_importance() -> pd.DataFrame:
    return _safe_read_csv(PATHS["modelisation_importance"], "modelisation_importance")


@lru_cache(maxsize=1)
def load_data_dictionary() -> pd.DataFrame:
    return _safe_read_csv(PATHS["data_dictionary"], "data_dictionary")


@lru_cache(maxsize=1)
def load_geojson_communes() -> dict:
    return _safe_read_geojson(PATHS["geojson_communes"], "geojson_communes")


# ---------------------------------------------------------------------------
# Chargement global au démarrage — appelé une fois depuis app.py
# ---------------------------------------------------------------------------

def _normalize_nom(s: str) -> str:
    """Normalise un nom de commune pour comparaison (accents, tirets, espaces)."""
    s = str(s).strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[-']", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.lower().strip()


@lru_cache(maxsize=1)
def build_nom_commune_to_adm2name() -> dict:
    """
    Construit le dict nom_commune (matrice) -> adm2_name (geojson).

    Le geojson OCHA n'a pas de colonne id_commune (vérifié par inspection directe :
    ses propriétés sont adm2_name, adm2_pcode, etc.). La jointure carte <-> données
    passe donc par le nom de commune, avec :
    1. Correspondance directe (nom identique)
    2. Normalisation (accents, tirets, espaces) — résout 63/67 écarts observés
    3. Corrections manuelles documentées (CORRESPONDANCE_NOMS_MANUELLE dans config.py)
       — les 4 cas restants après normalisation, conformes au README du projet.
    """
    df = load_matrice_globale()
    geojson = load_geojson_communes()

    noms_geojson = [f["properties"][GEOJSON_NAME_PROPERTY] for f in geojson["features"]]
    norm_to_geojson = {_normalize_nom(n): n for n in noms_geojson}

    mapping = {}
    non_resolus = []
    for nom in df[NOM_COMMUNE_COL].dropna().unique():
        if nom in CORRESPONDANCE_NOMS_MANUELLE:
            mapping[nom] = CORRESPONDANCE_NOMS_MANUELLE[nom]
            continue
        norm = _normalize_nom(nom)
        if norm in norm_to_geojson:
            mapping[nom] = norm_to_geojson[norm]
        else:
            non_resolus.append(nom)

    if non_resolus:
        logger.warning(
            f"{len(non_resolus)} commune(s) non résolue(s) pour la jointure geojson : "
            f"{non_resolus}. Ajoutez-les à CORRESPONDANCE_NOMS_MANUELLE dans data/config.py."
        )
    else:
        logger.info(f"Correspondance nom_commune <-> adm2_name : {len(mapping)}/140 résolues.")

    return mapping


@lru_cache(maxsize=1)
def get_matrice_avec_geojson_name() -> pd.DataFrame:
    """
    Retourne la matrice globale enrichie d'une colonne `adm2_name` prête à être
    utilisée comme `locations` dans un choroplèthe Plotly
    (avec featureidkey='properties.adm2_name').
    """
    df = load_matrice_globale().copy()
    mapping = build_nom_commune_to_adm2name()
    df["adm2_name"] = df[NOM_COMMUNE_COL].map(mapping)
    return df


_TABLE_CACHE: dict[str, pd.DataFrame] = {}


def get_table(key: str) -> pd.DataFrame:
    """
    Charge (et met en cache) n'importe quelle table CSV référencée par sa clé
    dans data/config.PATHS. Point d'accès générique pour les pages qui n'ont
    pas besoin d'un loader dédié.
    """
    if key not in _TABLE_CACHE:
        _TABLE_CACHE[key] = _safe_read_csv(PATHS[key], key)
    return _TABLE_CACHE[key]


@lru_cache(maxsize=1)
def get_matrice_carte() -> pd.DataFrame:
    """
    Matrice enrichie pour la carte interactive : matrice_globale + adm2_name
    (jointure geojson) + IIFT/classe_IIFT (notebook 3) + cluster_kmeans
    (notebook 4), tous joints sur id_commune.
    """
    df = get_matrice_avec_geojson_name()
    iift = get_table("iift_communes")[[ID_COMMUNE_COL, "IIFT", "classe_IIFT"]]
    clusters = get_table("clustering_resultats")[[ID_COMMUNE_COL, "cluster_kmeans"]]
    df = df.merge(iift, on=ID_COMMUNE_COL, how="left")
    df = df.merge(clusters, on=ID_COMMUNE_COL, how="left")
    df["cluster_kmeans"] = df["cluster_kmeans"].astype("Int64").astype(str)
    return df


def load_all() -> dict:
    """
    Charge toutes les tables au démarrage du serveur et les retourne dans un
    dict. Si une table échoue, l'erreur est loguée mais ne bloque pas le
    chargement des autres — permet de démarrer le dashboard même si une
    page spécifique est temporairement indisponible.
    """
    data = {}

    csv_keys = [
        "matrice_globale",
        "points_brh_geo_csv",
        "eda_dictionnaire_acp",
        "eda_dictionnaire_afcm",
        "eda_dictionnaire_variables",
        "eda_dictionnaire_variables_actives",
        "matrice_acp",
        "matrice_afcm",
        "matrice_active_eda",
        "acp_contributions_variables",
        "acp_coordonnees_variables",
        "acp_cos2_variables",
        "acp_scores_communes",
        "acp_valeurs_propres",
        "dictionnaire_iift",
        "iift_communes",
        "afcm_valeurs_propres",
        "choix_k_kmeans",
        "clustering_resultats",
        "communes_representatives_par_cluster",
        "comparaison_kmeans_cha",
        "dictionnaire_clusters",
        "profil_qualitatif_clusters",
        "profil_quantitatif_clusters",
        "comparaison_kmeans_quartiles_iift",
        "eta2_kmeans_vs_quartiles",
        "synthese_kmeans_vs_quartiles",
        "tableau_croise_kmeans_quartiles",
        "modelisation_comparaison",
        "modelisation_importance",
        "modelisation_predictions",
        "modelisation_variables_lasso_retirees",
        "data_dictionary",
    ]

    erreurs = []
    for key in csv_keys:
        try:
            data[key] = _safe_read_csv(PATHS[key], key)
        except DataLoadError:
            erreurs.append(key)
            data[key] = None

    try:
        data["geojson_communes"] = load_geojson_communes()  # ✅ chemin confirmé
    except DataLoadError:
        erreurs.append("geojson_communes")
        data["geojson_communes"] = None

    if erreurs:
        logger.warning(
            f"Démarrage avec {len(erreurs)} table(s) indisponible(s) : {erreurs}. "
            "Les pages correspondantes afficheront un message d'erreur au lieu de planter."
        )
    else:
        logger.info("Toutes les tables ont été chargées avec succès.")

    return data
