"""
Page 2 — Carte interactive : choroplèthe IIFT / clusters K-Means / indicateurs bruts.

Utilise get_matrice_carte() qui enrichit la matrice globale avec :
- adm2_name (jointure geojson par nom, cf. build_nom_commune_to_adm2name)
- IIFT + classe_IIFT (notebook 3 — G10_iift_communes.csv)
- cluster_kmeans (notebook 4 — G10_clusters_kmeans.csv)

Le filtre "Cluster IIFT" est actif (cluster_available=True) : les 3 clusters
ont une sémantique vérifiée sur les données réelles (cf. data/config.py —
CLUSTER_LABELS).

[Correctif] Le radio "Niveau géographique" (Pays / Département / Arrondissement
/ Commune) est maintenant réellement fonctionnel :
- toggle_niveau_geo() affiche/masque les dropdowns Département/Arrondissement/
  Commune selon le niveau choisi, et réinitialise ceux qui deviennent masqués.
- update_arrondissement_options() / update_commune_options() implémentent la
  cascade (choisir un département restreint les arrondissements proposés,
  qui restreignent à leur tour les communes proposées).
- update_carte() applique désormais le filtrage département -> arrondissement
  -> commune, et pas seulement département comme avant.
- Cliquer une commune sur la carte alimente "selection-store" (partagé,
  monté globalement dans app.py), lu par l'onglet Fiche commune pour s'y
  pré-remplir automatiquement.
"""

import dash
from dash import html, dcc, callback, Output, Input, State, ctx, no_update
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
    CLASSE_IIFT_ORDER,
    CLASSE_IIFT_COLORS,
    DEFAULT_MAP_INDICATOR,
    GEOJSON_NAME_PROPERTY,
    DEPARTEMENT_COL,
    ARRONDISSEMENT_COL,
    NOM_COMMUNE_COL,
)


def layout():
    try:
        df = get_matrice_carte()
        departements = sorted(df[DEPARTEMENT_COL].dropna().unique())
        arrondissements = sorted(df[ARRONDISSEMENT_COL].dropna().unique())
        communes = sorted(df[NOM_COMMUNE_COL].dropna().unique())
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
            build_filter_bar(
                departements=departements,
                arrondissements=arrondissements,
                communes=communes,
                cluster_available=True,
            ),
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


# ---------------------------------------------------------------------------
# Cascade du niveau géographique
# ---------------------------------------------------------------------------

@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-departement-group", "style"),
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement-group", "style"),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune-group", "style"),
    Output(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value", allow_duplicate=True),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "value", allow_duplicate=True),
    Input(f"{FILTER_BAR_ID_PREFIX}-niveau-geo", "value"),
    prevent_initial_call=True,
)
def toggle_niveau_geo(niveau):
    """
    Affiche/masque les 3 dropdowns selon le niveau choisi (drill-down :
    Département visible dès "departement", Arrondissement dès
    "arrondissement", Commune uniquement à "commune"), et réinitialise à None
    la valeur de chaque dropdown qui redevient masqué — sinon un filtre choisi
    puis "caché" en remontant de niveau resterait appliqué silencieusement.
    """
    visible = {"display": "flex", "flexDirection": "column", "gap": "6px"}
    hidden = {"display": "none"}

    show_dept = niveau in ("departement", "arrondissement", "commune")
    show_arr = niveau in ("arrondissement", "commune")
    show_com = niveau == "commune"

    return (
        visible if show_dept else hidden,
        visible if show_arr else hidden,
        visible if show_com else hidden,
        no_update if show_dept else None,
        no_update if show_arr else None,
        no_update if show_com else None,
    )


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "options"),
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value", allow_duplicate=True),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    prevent_initial_call=True,
)
def update_arrondissement_options(departement):
    """Restreint la liste des arrondissements proposés au département choisi
    (ou tous les arrondissements si aucun département n'est sélectionné)."""
    try:
        df = get_matrice_carte()
    except DataLoadError:
        return [], None

    if departement:
        df = df[df[DEPARTEMENT_COL] == departement]
    arrondissements = sorted(df[ARRONDISSEMENT_COL].dropna().unique())
    return [{"label": a, "value": a} for a in arrondissements], None


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "options"),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "value", allow_duplicate=True),
    Input(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value"),
    State(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    prevent_initial_call=True,
)
def update_commune_options(arrondissement, departement):
    """Restreint la liste des communes proposées à l'arrondissement choisi
    (à défaut, au département choisi ; à défaut, toutes les communes)."""
    try:
        df = get_matrice_carte()
    except DataLoadError:
        return [], None

    if arrondissement:
        df = df[df[ARRONDISSEMENT_COL] == arrondissement]
    elif departement:
        df = df[df[DEPARTEMENT_COL] == departement]
    communes = sorted(df[NOM_COMMUNE_COL].dropna().unique())
    return [{"label": c, "value": c} for c in communes], None


# ---------------------------------------------------------------------------
# Carte principale
# ---------------------------------------------------------------------------

@callback(
    Output("carte-choropleth", "figure"),
    Output(f"{FILTER_BAR_ID_PREFIX}-total", "children"),
    Output(f"{FILTER_BAR_ID_PREFIX}-selectionne", "children"),
    Output("selection-store", "data"),
    Input("carte-indicateur", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-commune", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-cluster", "value"),
    Input("carte-choropleth", "clickData"),
    State("selection-store", "data"),
)
def update_carte(indicateur, departement, arrondissement, commune, cluster, click_data, selection):
    try:
        df = get_matrice_carte()
        geojson = load_geojson_communes()
    except DataLoadError:
        return go.Figure(), "—", "—", selection or {"commune": None, "cluster": "all"}

    total = len(df)
    df_filtre = df
    if departement:
        df_filtre = df_filtre[df_filtre[DEPARTEMENT_COL] == departement]
    if arrondissement:
        df_filtre = df_filtre[df_filtre[ARRONDISSEMENT_COL] == arrondissement]
    if commune:
        df_filtre = df_filtre[df_filtre[NOM_COMMUNE_COL] == commune]
    if cluster and cluster != "all":
        df_filtre = df_filtre[df_filtre["cluster_kmeans"] == str(cluster)]
    n_selection = len(df_filtre)

    # Un clic direct sur la carte met à jour le store partagé avec la commune
    # cliquée (indépendamment des dropdowns) — c'est ce que lit l'onglet Fiche
    # commune pour se pré-remplir automatiquement.
    nouvelle_selection = selection or {"commune": None, "cluster": "all"}
    if ctx.triggered_id == "carte-choropleth" and click_data:
        try:
            adm2_name_clique = click_data["points"][0]["location"]
            match = df[df["adm2_name"] == adm2_name_clique]
            if not match.empty:
                nouvelle_selection = {
                    **nouvelle_selection,
                    "commune": match.iloc[0][NOM_COMMUNE_COL],
                }
        except (KeyError, IndexError):
            pass

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
            category_orders={"classe_IIFT": CLASSE_IIFT_ORDER},
            color_discrete_sequence=CLASSE_IIFT_COLORS,
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

    return fig, str(total), str(n_selection), nouvelle_selection
