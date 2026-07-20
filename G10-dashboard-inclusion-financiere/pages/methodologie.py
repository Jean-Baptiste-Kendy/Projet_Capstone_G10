"""Page 7 — Méthodologie : onglets compacts, pas un long document scrollable."""

import dash
from dash import html, dcc, callback, Output, Input

from data.loaders import get_table, DataLoadError
from data.config import COLORS

dash.register_page(__name__, path="/methodologie", name="Méthodologie", order=7)

TAB_STYLE = {"padding": "8px 14px", "fontSize": "12px"}
TAB_SELECTED_STYLE = {
    "padding": "8px 14px", "fontSize": "12px", "fontWeight": "600",
    "borderTop": f"2px solid {COLORS['terracotta_500']}", "color": COLORS["petrole_900"],
}


def layout():
    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="page-header-row",
                children=[
                    html.H1("Méthodologie"),
                    html.Span("Origine des données, principes clés, choix de K, limites", className="page-header-sub"),
                ],
            ),
            dcc.Tabs(
                id="methodo-tabs",
                value="sources",
                children=[
                    dcc.Tab(label="Sources", value="sources", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(label="Principes clés", value="principes", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(label="Choix de K", value="choix_k", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(label="Limites & stack", value="limites", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                ],
            ),
            html.Div(id="methodo-tab-content", style={"marginTop": "16px"}),
        ],
    )


@callback(Output("methodo-tab-content", "children"), Input("methodo-tabs", "value"))
def render_tab(tab):
    if tab == "sources":
        return html.Div(
            className="chart-panel chart-panel-full",
            children=[
                html.Div(
                    className="chart-panel-header",
                    children=[html.Span("Origine des données", className="chart-panel-title")],
                ),
                html.Div(
                    className="chart-panel-body",
                    children=[
                        html.Div(
                            className="error-banner",
                            style={"background": "rgba(193,98,45,0.06)", "borderColor": COLORS["terracotta_300"]},
                            children=(
                                "Données BRH collectées manuellement depuis le tableau de bord public "
                                "(pas un export institutionnel officiel). Variables de pauvreté/privation "
                                "spatiale : proxys reconstruits par lecture visuelle de cartes à quantiles."
                            ),
                        ),
                        html.Table(
                            className="fiche-table",
                            style={"marginTop": "12px"},
                            children=[
                                html.Thead(html.Tr([html.Th("Source"), html.Th("Contenu"), html.Th("Rôle")])),
                                html.Tbody([
                                    html.Tr([html.Td("BRH (collecte manuelle 2017)"), html.Td("29 var. services financiers"), html.Td("Offre par commune")]),
                                    html.Tr([html.Td("IHSI 2024"), html.Td("Démographie officielle"), html.Td("Population, ménages, superficie")]),
                                    html.Tr([html.Td("OCHA COD-AB"), html.Td("Limites admin. (140 communes)"), html.Td("Géolocalisation")]),
                                    html.Tr([html.Td("Banque Mondiale / BID"), html.Td("Proxy pauvreté/privation"), html.Td("Contexte socio-éco")]),
                                    html.Tr([html.Td("OpenStreetMap"), html.Td("Points géolocalisés réels"), html.Td("Géoloc. hybride prestataires")]),
                                ]),
                            ],
                        ),
                    ],
                ),
            ],
        )

    if tab == "principes":
        principes = [
            "Jointures exactes uniquement sur id_commune (how='inner', validate='1:1').",
            "Correspondance par nom quand id_commune est absent (geojson OCHA) — vérifié sur ce dashboard : 63/67 écarts résolus par normalisation, 4 corrections manuelles documentées (Estère↔L'Estère, Cornillon↔Cornillon/Grand Bois, etc.).",
            "Géolocalisation hybride : points OSM réels en priorité (~7%), bruit gaussien calibré (±330 m) pour le reliquat, traçabilité osm_reel/bruit_synthetique.",
            "Bruit gaussien calibré (σ=15%, seed=42) sur les variables WBG dérivées de groupes.",
            "Séparation variables actives/supplémentaires pour l'AFCM (évite la redondance urbain/rural).",
            "Correction de Benzécri sur les valeurs propres AFCM (Axe1 : 12,3%→66,3% de variance corrigée).",
            "DBSCAN testé puis rejeté empiriquement (silhouette inférieure à K-Means).",
        ]
        return html.Div(
            className="chart-panel chart-panel-full",
            children=[
                html.Div(className="chart-panel-header", children=[html.Span("Principes méthodologiques clés", className="chart-panel-title")]),
                html.Div(className="chart-panel-body", children=[
                    html.Ul(className="methodo-list", children=[html.Li(p) for p in principes]),
                ]),
            ],
        )

    if tab == "choix_k":
        try:
            choix_k = get_table("choix_k_kmeans")
        except DataLoadError as e:
            return html.Div(className="error-banner", children=str(e))
        return html.Div(
            className="chart-panel chart-panel-full",
            children=[
                html.Div(className="chart-panel-header", children=[
                    html.Span("Choix de K pour le K-Means", className="chart-panel-title"),
                    html.Span("K=3 retenu (silhouette maximale)", className="chart-panel-caption"),
                ]),
                html.Div(className="chart-panel-body", children=[
                    html.Table(
                        className="fiche-table",
                        children=[
                            html.Thead(html.Tr([html.Th(c) for c in choix_k.columns])),
                            html.Tbody([
                                html.Tr([html.Td(f"{v:.3f}" if isinstance(v, float) else str(v)) for v in row])
                                for row in choix_k.itertuples(index=False)
                            ]),
                        ],
                    ),
                ]),
            ],
        )

    # limites & stack
    limites = [
        "Données BRH collectées manuellement, non issues d'un export institutionnel officiel.",
        "Seuil urbain/rural (50%) : choix méthodologique, pas une valeur officielle IHSI/WBG.",
        "Variables de pauvreté/privation spatiale : proxys visuels, pas des statistiques certifiées.",
        "Points GPS des prestataires BRH : valide pour l'appartenance communale, pas pour une précision fine.",
        "Variables non disponibles : couverture réseau mobile, taux d'alphabétisation, IPM officiel complet.",
    ]
    return html.Div(
        className="dash-grid",
        children=[
            html.Div(
                className="chart-panel",
                children=[
                    html.Div(className="chart-panel-header", children=[html.Span("Limites méthodologiques", className="chart-panel-title")]),
                    html.Div(className="chart-panel-body", children=[html.Ul(className="methodo-list", children=[html.Li(l) for l in limites])]),
                ],
            ),
            html.Div(
                className="chart-panel",
                children=[
                    html.Div(className="chart-panel-header", children=[html.Span("Stack technique", className="chart-panel-title")]),
                    html.Div(className="chart-panel-body", children=[
                        html.P(
                            "Python (pandas, numpy, geopandas, shapely, requests, scikit-learn, scipy), "
                            "prince (ACP/AFCM), matplotlib/seaborn (notebooks), Plotly/Dash (application web). "
                            "Environnement : Google Colab.",
                            style={"fontSize": "12px", "color": "var(--text-secondary)"},
                        ),
                    ]),
                ],
            ),
        ],
    )
