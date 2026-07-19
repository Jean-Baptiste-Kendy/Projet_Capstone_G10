"""
Page 2 — Carte interactive : choroplèthe IIFT / clusters K-Means / indicateurs bruts.

Utilise get_matrice_carte() qui enrichit la matrice globale avec :
- adm2_name (jointure geojson par nom, cf. build_nom_commune_to_adm2name)
- IIFT + classe_IIFT (notebook 3 — G10_iift_communes.csv)
- cluster_kmeans (notebook 4 — G10_clusters_kmeans.csv)

Filtre géographique en cascade : Pays -> Département -> Arrondissement -> Commune.
Le radio "Niveau géographique" pilote la VISIBILITÉ des 3 dropdowns dépendants ;
chaque dropdown, une fois affiché, filtre réellement la carte (ce n'était pas le
cas dans une version précédente, où ce radio ne déclenchait aucun callback).

La commune sélectionnée (via le dropdown "Commune" OU un clic direct sur la
carte) est écrite dans le Store global `selection-store` (monté dans app.py,
persistant entre les pages) pour pré-remplir automatiquement la page
Fiche commune — cf. pages/fiche_commune.py.
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
    DEFAULT_MAP_INDICATOR,
    GEOJSON_NAME_PROPERTY,
    DEPARTEMENT_COL,
    ARRONDISSEMENT_COL,
    NOM_COMMUNE_COL,
)

dash.register_page(__name__, path="/carte", name="Carte interactive", order=2)

_GROUP_VISIBLE = {"display": "flex", "flexDirection": "column", "gap": "4px"}
_GROUP_HIDDEN = {"display": "none"}


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
            html.H1("Carte interactive"),
            html.P(
                "Exploration géospatiale de l'indice IIFT, de la typologie K-Means "
                "(3 clusters) et des indicateurs bruts d'inclusion financière — "
                "140 communes. Cliquez sur une commune pour ouvrir sa fiche détaillée.",
                style={"color": "var(--text-secondary)"},
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
            html.P(
                id="carte-selection-info",
                style={"color": "var(--text-secondary)", "fontSize": "13px", "marginTop": "8px"},
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Cascade Département -> Arrondissement -> Commune (+ visibilité du niveau géo)
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
    Affiche uniquement les dropdowns pertinents pour le niveau choisi, et
    réinitialise la sélection de ceux qui redeviennent masqués (évite qu'un
    filtre "Arrondissement" reste appliqué en silence après être repassé en
    vue "Département").
    """
    show_dept = niveau in ("departement", "arrondissement", "commune")
    show_arr = niveau in ("arrondissement", "commune")
    show_com = niveau == "commune"
    return (
        _GROUP_VISIBLE if show_dept else _GROUP_HIDDEN,
        _GROUP_VISIBLE if show_arr else _GROUP_HIDDEN,
        _GROUP_VISIBLE if show_com else _GROUP_HIDDEN,
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
    """Restreint la liste des arrondissements au département choisi (ou liste
    nationale complète si aucun département n'est sélectionné)."""
    try:
        df = get_matrice_carte()
    except DataLoadError:
        return [], None
    subset = df if not departement else df[df[DEPARTEMENT_COL] == departement]
    arrondissements = sorted(subset[ARRONDISSEMENT_COL].dropna().unique())
    return [{"label": a, "value": a} for a in arrondissements], None


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "options"),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "value", allow_duplicate=True),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value"),
    prevent_initial_call=True,
)
def update_commune_options(departement, arrondissement):
    """Restreint la liste des communes au département et/ou à l'arrondissement
    déjà choisis (cascade à deux niveaux)."""
    try:
        df = get_matrice_carte()
    except DataLoadError:
        return [], None
    subset = df
    if departement:
        subset = subset[subset[DEPARTEMENT_COL] == departement]
    if arrondissement:
        subset = subset[subset[ARRONDISSEMENT_COL] == arrondissement]
    communes = sorted(subset[NOM_COMMUNE_COL].dropna().unique())
    return [{"label": c, "value": c} for c in communes], None


# ---------------------------------------------------------------------------
# Carte principale
# ---------------------------------------------------------------------------

@callback(
    Output("carte-choropleth", "figure"),
    Output(f"{FILTER_BAR_ID_PREFIX}-total", "children"),
    Output(f"{FILTER_BAR_ID_PREFIX}-selectionne", "children"),
    Output("selection-store", "data"),
    Output("carte-selection-info", "children"),
    Input("carte-indicateur", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-commune", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-cluster", "value"),
    Input("carte-choropleth", "clickData"),
    State("selection-store", "data"),
)
def update_carte(indicateur, departement, arrondissement, commune, cluster, click_data, store_data):
    try:
        df = get_matrice_carte()
        geojson = load_geojson_communes()
    except DataLoadError:
        return go.Figure(), "—", "—", store_data or {"commune": None}, ""

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

    # --- Sélection pour la fiche commune (dropdown "Commune" prioritaire, sinon
    #     un clic direct sur la carte) — écrite dans le Store partagé global.
    commune_cliquee = None
    if ctx.triggered_id == "carte-choropleth" and click_data:
        try:
            adm2 = click_data["points"][0]["location"]
            match = df[df["adm2_name"] == adm2]
            if not match.empty:
                commune_cliquee = match.iloc[0][NOM_COMMUNE_COL]
        except (KeyError, IndexError, TypeError):
            commune_cliquee = None

    commune_selectionnee = commune or commune_cliquee
    if commune_selectionnee:
        store_out = {"commune": commune_selectionnee}
        info = f"Commune sélectionnée : {commune_selectionnee} — ouvrez l'onglet « Fiche commune » pour le détail."
    else:
        store_out = store_data or {"commune": None}
        info = ""

    is_categorical = indicateur in CATEGORICAL_INDICATORS

    common_kwargs = dict(
        geojson=geojson,
        locations="adm2_name",
        featureidkey=f"properties.{GEOJSON_NAME_PROPERTY}",
        mapbox_style="carto-positron",
        zoom=6.7,
        center={"lat": 18.97, "lon": -72.5},
        opacity=0.85,
        hover_name=NOM_COMMUNE_COL,
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
            hover_data={DEPARTEMENT_COL: True, "IIFT": ":.1f", "adm2_name": False},
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
            hover_data={DEPARTEMENT_COL: True, "IIFT": ":.1f", "adm2_name": False},
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
            hover_data={indicateur: ":.2f", DEPARTEMENT_COL: True, "adm2_name": False},
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

    return fig, str(total), str(n_selection), store_out, info
