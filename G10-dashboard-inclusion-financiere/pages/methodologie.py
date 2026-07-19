"""Page 7 — Méthodologie : traçabilité scientifique du pipeline complet."""

import dash
from dash import html, dcc

from data.loaders import get_table, DataLoadError
from data.config import COLORS

dash.register_page(__name__, path="/methodologie", name="Méthodologie", order=7)


def layout():
    try:
        choix_k = get_table("choix_k_kmeans")
    except DataLoadError as e:
        choix_k = None
        error_banner = html.Div(className="error-banner", children=str(e))
    else:
        error_banner = None

    table_k = None
    if choix_k is not None:
        table_k = html.Table(
            className="fiche-table",
            children=[
                html.Thead(html.Tr([html.Th(c) for c in choix_k.columns])),
                html.Tbody([
                    html.Tr([
                        html.Td(f"{v:.3f}" if isinstance(v, float) else str(v))
                        for v in row
                    ])
                    for row in choix_k.itertuples(index=False)
                ]),
            ],
        )

    return html.Div(
        className="page-container",
        children=[
            html.H1("Méthodologie"),
            html.P(
                "Documentation du pipeline complet : origine des données, principes "
                "méthodologiques clés, choix de K et limites reconnues.",
                style={"color": "var(--text-secondary)"},
            ),
            error_banner,

            html.H3("Origine des données"),
            html.Div(
                className="error-banner",
                style={"background": "rgba(193,98,45,0.06)", "borderColor": COLORS["terracotta_300"]},
                children=(
                    "Les données de services financiers (BRH) n'ont pas été obtenues "
                    "directement auprès des institutions concernées : elles ont été "
                    "collectées manuellement à partir du tableau de bord public en ligne "
                    "de la BRH, commune par commune. Certaines variables de pauvreté et de "
                    "privation spatiale sont des proxys reconstruits par lecture visuelle "
                    "de cartes à quantiles, et non des statistiques officielles publiées "
                    "commune par commune."
                ),
            ),
            html.Table(
                className="fiche-table",
                style={"marginTop": "16px"},
                children=[
                    html.Thead(html.Tr([html.Th("Source"), html.Th("Contenu"), html.Th("Rôle")])),
                    html.Tbody([
                        html.Tr([html.Td("BRH (collecte manuelle 2017)"), html.Td("29 variables de services financiers"), html.Td("Offre de services par commune")]),
                        html.Tr([html.Td("IHSI 2024"), html.Td("Démographie officielle"), html.Td("Population, ménages, superficie")]),
                        html.Tr([html.Td("OCHA COD-AB"), html.Td("Limites administratives (140 communes)"), html.Td("Géolocalisation")]),
                        html.Tr([html.Td("Banque Mondiale / BID"), html.Td("Proxy pauvreté et privation spatiale"), html.Td("Contexte socio-économique")]),
                        html.Tr([html.Td("OpenStreetMap (Overpass API)"), html.Td("Points géolocalisés réels"), html.Td("Géolocalisation hybride des prestataires")]),
                    ]),
                ],
            ),

            html.H3("Principes méthodologiques clés", style={"marginTop": "28px"}),
            html.Ul(
                className="methodo-list",
                children=[
                    html.Li("Jointures exactes uniquement sur id_commune (how='inner', validate='1:1')."),
                    html.Li(
                        "Correspondance par nom utilisée quand id_commune est absent (ex. le "
                        "geojson OCHA) — vérifiée sur ce dashboard : 63 des 67 écarts de noms "
                        "résolus par normalisation automatique (accents, tirets), les 4 cas "
                        "restants correspondant aux corrections manuelles documentées "
                        "(Estère ↔ L'Estère, Cornillon ↔ Cornillon/Grand Bois, etc.)."
                    ),
                    html.Li(
                        "Géolocalisation hybride : points réels OpenStreetMap utilisés en "
                        "priorité (~7 % de l'effectif), complétés par un bruit gaussien "
                        "calibré (±0,003° ≈ ±330 m) pour le reliquat, chaque point étiqueté "
                        "osm_reel / bruit_synthetique pour traçabilité."
                    ),
                    html.Li("Bruit gaussien calibré (σ = 15 %, seed = 42) appliqué aux variables WBG dérivées de groupes, pour éviter des valeurs strictement identiques entre communes d'un même groupe."),
                    html.Li("Séparation variables actives / supplémentaires pour l'AFCM, afin d'éviter que des variables redondantes ne dominent artificiellement les premiers axes factoriels."),
                    html.Li("Correction de Benzécri appliquée aux valeurs propres de l'AFCM (Axe 1 : 12,3 % → 66,3 % de variance corrigée) — la variance brute d'une AFCM sous-estime systématiquement la structure réelle."),
                    html.Li("DBSCAN testé puis rejeté empiriquement (classification en bruit trop importante, silhouette inférieure à K-Means)."),
                    html.Li("K=3 retenu pour K-Means après examen du score de silhouette sur K=2 à K=10 (voir tableau ci-dessous), et validé par comparaison à un modèle de référence simple (quartiles de l'IIFT)."),
                ],
            ),

            html.H3("Choix de K pour le K-Means", style={"marginTop": "28px"}),
            table_k if table_k is not None else html.Div(className="loading-placeholder", children="Table indisponible."),

            html.H3("Limites méthodologiques principales", style={"marginTop": "28px"}),
            html.Ul(
                className="methodo-list",
                children=[
                    html.Li("Données BRH collectées manuellement, non issues d'un export institutionnel officiel."),
                    html.Li("Seuil urbain/rural (50 %) : choix méthodologique, pas une valeur officielle IHSI/WBG."),
                    html.Li("Variables de pauvreté/privation spatiale : proxys visuels, pas des statistiques certifiées."),
                    html.Li("Points GPS des prestataires BRH : stratégie hybride, valide pour l'appartenance communale mais pas pour une précision cartographique fine."),
                    html.Li("Variables recherchées mais non disponibles : couverture réseau mobile par commune, taux d'alphabétisation par commune, IPM officiel complet."),
                ],
            ),

            html.H3("Stack technique", style={"marginTop": "28px"}),
            html.P(
                "Python (pandas, numpy, geopandas, shapely, requests, scikit-learn, scipy), "
                "analyse multivariée avec prince (ACP / AFCM), visualisation matplotlib/seaborn "
                "pour les notebooks et Plotly/Dash pour cette application web. "
                "Environnement de développement : Google Colab.",
                style={"color": "var(--text-secondary)", "fontSize": "13px"},
            ),
        ],
    )
