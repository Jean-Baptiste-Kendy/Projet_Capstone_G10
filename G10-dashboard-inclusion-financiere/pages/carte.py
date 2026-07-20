"""
Page 2 — Carte interactive : choroplèthe IIFT / clusters K-Means / indicateurs bruts.

Utilise get_matrice_carte() qui enrichit la matrice globale avec :
- adm2_name (jointure geojson par nom, cf. build_nom_commune_to_adm2name)
- IIFT + classe_IIFT (notebook 3 — G10_iift_communes.csv)
- cluster_kmeans (notebook 4 — G10_clusters_kmeans.csv)

Le filtre "Cluster IIFT" est maintenant actif (cluster_available=True) : les
3 clusters ont une sémantique vérifiée sur les données réelles
(cf. data/config.py — CLUSTER_LABELS).
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go

from components.filter_bar import build_filter_bar, FILTER_BAR_ID_PREFIX
from data.loaders import get_matrice_carte, load_geojson_communes, DataLoadError
from data.config import (
    COLORS,
    INDICATOR_LABELS,
    CATEGORICAL_INDICATORS,
    CLUSTER_COLORS,
    CLUSTER_LABELS,
    DEFAULT_MAP_INDICATOR,
    GEOJSON_NAME_PROPERTY,
)

dash.register_page(__name__, path="/carte", name="Carte interactive", order=2)


def layout():
    try:
        df = get_matrice_carte()
        departements = sorted(df["departement"].dropna().unique())
    except DataLoadError as e:
        return html.Div(
            className="page-container",
            children=[
                html.H1("Carte interactive"),
                html.Div(className="error-banner", children=str(e)),
            ],
        )

    indicator_options = (
        [{"label": lbl, "value": col} for col, lbl in CATEGORICAL_INDICATORS.items()]
        + [{"label": lbl, "value": col} for col, lbl in INDICATOR_LABELS.items()]
    )

    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="page-header-row",
                children=[
                    html.H1("Carte interactive"),
                    html.Span("IIFT, clusters K-Means et indicateurs bruts — 140 communes", className="page-header-sub"),
                ],
            ),
            build_filter_bar(departements=departements, cluster_available=True),
            html.Div(
                style={"maxWidth": "360px", "marginBottom": "16px"},
                children=[
                    html.Label("Indicateur affiché", className="filter-label"),
                    dcc.Dropdown(
                        id="carte-indicateur",
                        options=indicator_options,
                        value=DEFAULT_MAP_INDICATOR,
                        clearable=False,
                    ),
                ],
            ),
            dcc.Loading(
                type="circle",
                color=COLORS["terracotta_500"],
                children=dcc.Graph(id="carte-choropleth", style={"height": "650px"}),
            ),
        ],
    )


@callback(
    Output("carte-choropleth", "figure"),
    Output(f"{FILTER_BAR_ID_PREFIX}-total", "children"),
    Output(f"{FILTER_BAR_ID_PREFIX}-selectionne", "children"),
    Input("carte-indicateur", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-cluster", "value"),
)
def update_carte(indicateur, departement, cluster):
    try:
        df = get_matrice_carte()
        geojson = load_geojson_communes()
    except DataLoadError:
        return go.Figure(), "—", "—"

    total = len(df)
    df_filtre = df
    if departement:
        df_filtre = df_filtre[df_filtre["departement"] == departement]
    if cluster and cluster != "all":
        df_filtre = df_filtre[df_filtre["cluster_kmeans"] == str(cluster)]
    n_selection = len(df_filtre)

    is_categorical = indicateur in CATEGORICAL_INDICATORS

    common_kwargs = dict(
        geojson=geojson,
        locations="adm2_name",
        featureidkey=f"properties.{GEOJSON_NAME_PROPERTY}",
        mapbox_style="carto-positron",
        zoom=6.7,
        center={"lat": 18.97, "lon": -72.5},
        opacity=0.85,
        hover_name="nom_commune",
    )

    if indicateur == "cluster_kmeans":
        df_plot = df_filtre.copy()
        df_plot["cluster_label"] = df_plot["cluster_kmeans"].map(CLUSTER_LABELS)
        color_map = {CLUSTER_LABELS[k]: v for k, v in CLUSTER_COLORS.items()}
        fig = px.choropleth_mapbox(
            df_plot,
            color="cluster_label",
            color_discrete_map=color_map,
            category_orders={"cluster_label": list(CLUSTER_LABELS.values())},
            hover_data={"departement": True, "IIFT": ":.1f", "adm2_name": False},
            **common_kwargs,
        )
        legend_title = "Cluster K-Means"
    elif indicateur == "classe_IIFT":
        fig = px.choropleth_mapbox(
            df_filtre,
            color="classe_IIFT",
            category_orders={
                "classe_IIFT": ["Très faible", "Faible", "Moyen", "Élevé", "Très élevé"]
            },
            color_discrete_sequence=[
                COLORS["terracotta_700"],
                COLORS["terracotta_500"],
                COLORS["petrole_200"],
                COLORS["petrole_500"],
                COLORS["petrole_900"],
            ],
            hover_data={"departement": True, "IIFT": ":.1f", "adm2_name": False},
            **common_kwargs,
        )
        legend_title = "Classe IIFT"
    else:
        label = INDICATOR_LABELS.get(indicateur, indicateur)
        fig = px.choropleth_mapbox(
            df_filtre,
            color=indicateur,
            color_continuous_scale=[
                COLORS["petrole_200"],
                COLORS["petrole_500"],
                COLORS["petrole_900"],
            ],
            hover_data={indicateur: ":.2f", "departement": True, "adm2_name": False},
            labels={indicateur: label},
            **common_kwargs,
        )
        legend_title = label

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        font_family="Inter, sans-serif",
        paper_bgcolor=COLORS["surface"],
        legend=dict(title=legend_title, bgcolor="rgba(255,255,255,0.9)"),
    )
    if not is_categorical:
        fig.update_layout(coloraxis_colorbar=dict(title=legend_title, x=0.98))

    return fig, str(total), str(n_selection)
