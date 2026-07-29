"""
Page 2 — Carte interactive : choroplèthe IIFT / clusters K-Means / indicateurs bruts.

Utilise get_matrice_carte() qui enrichit la matrice globale avec :
- adm2_name (jointure geojson par nom, cf. build_nom_commune_to_adm2name)
- IIFT + classe_IIFT (notebook 3 — G10_iift_communes.csv)
- cluster_kmeans (notebook 4 — G10_clusters_kmeans.csv)

Le filtre "Cluster K-Means" est actif (cluster_available=True) : les 3 clusters
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

[Correctif] Le filtre par clic/double-clic sur la légende (isoler une
catégorie Cluster K-Means / Classe IIFT) est retiré : le filtre "Cluster
K-Means" de la barre de filtres couvre déjà ce besoin, et la légende répond
désormais au survol — passer la souris sur une entrée met en avant toutes
les communes de cette catégorie sur la carte, comme le fait déjà le survol
d'une commune.
"""

import dash
from dash import html, dcc, callback, clientside_callback, Output, Input, State, ctx, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.filter_bar import build_filter_bar, FILTER_BAR_ID_PREFIX, TOUT_LABEL, MULTI_SELECT_LABELS
from data.loaders import (
    get_matrice_carte,
    load_geojson_communes,
    load_geojson_departements,
    load_geojson_arrondissements,
    load_geojson_pays,
    build_nom_departement_to_adm1name,
    build_zone_stats,
    DataLoadError,
)
from data.config import (
    COLORS,
    INDICATOR_LABELS,
    CATEGORICAL_INDICATORS,
    CLUSTER_COLORS,
    CLUSTER_LABELS,
    CLUSTER_LABELS_COURT,
    CLASSE_IIFT_ORDER,
    CLASSE_IIFT_COLORS,
    DEFAULT_MAP_INDICATOR,
    BRH_SERVICE_INDICATOR_LABELS,
    OFFER_INDICATOR_LABELS,
    DEMAND_INDICATOR_LABELS,
    TYPE_PRESTATAIRE_LABELS,
    SUM_INDICATORS,
    GEOJSON_NAME_PROPERTY,
    GEOJSON_DEPT_NAME_PROPERTY,
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

    # [Correctif] "Choisir un indicateur de demande" et "Autre indicateur
    # d'analyse" sont désormais UN SEUL dropdown : les options de l'ancien
    # sélecteur "analyse" (catégoriels + indicateurs génériques) sont
    # simplement ajoutées à la suite des indicateurs de demande. {**a, **b}
    # dédoublonne automatiquement les clés communes aux deux dicts
    # (population_totale, taille_moyenne_menage) — pas d'entrée en double
    # dans la liste déroulante.
    demande_options = [{"label": lbl, "value": col} for col, lbl in CATEGORICAL_INDICATORS.items()] + [
        {"label": lbl, "value": col} for col, lbl in {**INDICATOR_LABELS, **DEMAND_INDICATOR_LABELS}.items()
    ]

    offre_dropdown = dcc.Dropdown(
        id="carte-offre-indicateur",
        options=[{"label": lbl, "value": col} for col, lbl in OFFER_INDICATOR_LABELS.items()],
        value="brh_total_effectif",
        placeholder="Sélectionner un indicateur d'offre",
        clearable=False,
        style={"maxWidth": "230px"},
    )
    demande_dropdown = dcc.Dropdown(
        id="carte-demande-indicateur",
        options=demande_options,
        # [Correctif] "Indice IIFT (0-100)" par défaut, plutôt que "Cluster
        # K-Means" — cohérent avec DEFAULT_MAP_INDICATOR ("IIFT") déjà utilisé
        # ailleurs comme indicateur de repli.
        value="IIFT",
        placeholder="Sélectionner un indicateur de demande",
        clearable=False,
        style={"maxWidth": "230px"},
    )
    # [Ajout] "(Tout)" par défaut = les 6 types sélectionnés explicitement
    # (plutôt qu'une case vide reposant sur le placeholder) : cohérent avec
    # le badge "N sélectionnés" et le bouton "Tout sélectionner" du menu.
    type_prestataire_dropdown = dcc.Dropdown(
        id="carte-type-prestataire",
        options=[{"label": lbl, "value": col} for col, lbl in TYPE_PRESTATAIRE_LABELS.items()],
        value=list(TYPE_PRESTATAIRE_LABELS),
        multi=True,
        placeholder=TOUT_LABEL,
        clearable=False,
        labels=MULTI_SELECT_LABELS,
        style={"maxWidth": "230px"},
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
                offre_dropdown=offre_dropdown,
                demande_dropdown=demande_dropdown,
                type_prestataire_dropdown=type_prestataire_dropdown,
            ),
            html.Div(
                className="map-analysis-grid",
                children=[
                    html.Div(
                        className="chart-panel",
                        children=[
                            html.Div("Carte des communes sélectionnées", className="chart-panel-header"),
                            dcc.Loading(
                                type="circle",
                                color=COLORS["terracotta_500"],
                                children=dcc.Graph(id="carte-choropleth", style={"height": "650px"}),
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-panel map-side-chart",
                        children=[
                            html.Div(id="carte-bar-title", className="chart-panel-header"),
                            html.Div(
                                className="map-side-chart-body",
                                children=[
                                    # [Ajout] Visible uniquement quand l'indicateur d'offre pilote
                                    # la carte (aucun indicateur de demande/analyse sélectionné) :
                                    # répartition en nb de points par type de prestataire, sur la
                                    # sélection géographique/cluster courante. Toujours masqué/
                                    # affiché par update_carte() via son style, jamais retiré du DOM.
                                    html.Div(
                                        id="carte-barres-type-container",
                                        style={"display": "none"},
                                        children=[
                                            html.Div(
                                                id="carte-barres-type-title",
                                                className="chart-panel-caption",
                                                style={"fontWeight": 600, "marginBottom": "4px"},
                                            ),
                                            dcc.Loading(
                                                type="circle",
                                                color=COLORS["terracotta_500"],
                                                children=dcc.Graph(
                                                    id="carte-barres-type", config={"displayModeBar": False}
                                                ),
                                            ),
                                            html.Hr(style={"margin": "12px 0", "borderColor": COLORS["border"]}),
                                        ],
                                    ),
                                    dcc.Loading(
                                        type="circle",
                                        color=COLORS["terracotta_500"],
                                        children=dcc.Graph(id="carte-barres", config={"displayModeBar": False}),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # [Correctif] Store transitoire mémorisant la zone précise visée par
            # un clic sur une barre (departement/arrondissement/commune ciblés).
            # Sans lui, un clic sur une barre "commune" déclenche quand même la
            # cascade normale des dropdowns (update_arrondissement_options /
            # update_commune_options, réagissant au changement de département),
            # qui réinitialise ensuite arrondissement/commune à "tout sélectionné"
            # et écrase la sélection précise voulue par le clic — d'où la carte
            # qui retombe sur tout le département au lieu de la seule commune
            # cliquée. Les deux callbacks de cascade lisent ce store pour
            # restreindre leur valeur à la zone ciblée au lieu de tout sélectionner,
            # puis le réinitialisent à None une fois consommé.
            dcc.Store(id="carte-bar-click-target", data=None),
            # [Ajout] Survol synchronisé carte <-> diagramme en barre :
            # "carte-zone-location-map" fait le pont entre le nom de zone tel
            # qu'affiché sur l'axe des barres ("zone", ex. nom de commune/
            # arrondissement/département) et l'identifiant utilisé par le
            # tracé choroplèthe pour cette même zone (location du geojson,
            # qui peut différer — ex. adm2_name pour une commune). Recalculée
            # à chaque update_carte(), donc toujours cohérente avec la carte
            # et les barres affichées à l'instant du survol.
            dcc.Store(id="carte-zone-location-map", data={}),
            # Sortie factice, requise par Dash pour tout clientside_callback
            # (non utilisée ailleurs) : le callback JS associé restyle
            # directement les deux graphes (carte-choropleth, carte-barres)
            # via Plotly.restyle plutôt que de passer par un Output réel.
            dcc.Store(id="carte-hover-sync-dummy", data=None),
            # [Ajout] Sortie factice pour le clientside_callback qui gère le
            # clic sur la légende des indicateurs catégoriels (Cluster
            # K-Means / Classe IIFT) : permet de cliquer sur une entrée de
            # légende pour n'afficher que cette catégorie sur la carte
            # (isoler/désisoler), comme le permettait auparavant
            # px.choropleth_mapbox (un trace par catégorie) avant le
            # correctif du survol qui l'a remplacé par un seul trace.
            dcc.Store(id="carte-legend-filter-dummy", data=None),
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
        no_update if show_dept else [],
        no_update if show_arr else [],
        no_update if show_com else [],
    )


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "options"),
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value", allow_duplicate=True),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    State("carte-bar-click-target", "data"),
    prevent_initial_call=True,
)
def update_arrondissement_options(departement, click_target):
    """Restreint la liste des arrondissements proposés au département choisi
    (ou tous les arrondissements si aucun département n'est sélectionné), et
    sélectionne par défaut tous les arrondissements de la nouvelle liste
    (cohérent avec "(Tout)" = tout coché).

    [Correctif] Exception : si ce changement de département provient d'un clic
    sur une barre ciblant précisément un arrondissement (ou une commune, qui
    appartient elle-même à un seul arrondissement), on ne sélectionne QUE cet
    arrondissement-là plutôt que tous ceux du département — sinon la cascade
    écrase la sélection fine voulue par le clic (cf. carte-bar-click-target)."""
    try:
        df = get_matrice_carte()
    except DataLoadError:
        return [], []

    if departement:
        df = df[df[DEPARTEMENT_COL].isin(departement)]
    arrondissements = sorted(df[ARRONDISSEMENT_COL].dropna().unique())
    options = [{"label": a, "value": a} for a in arrondissements]

    cible = (click_target or {}).get("arrondissement")
    if click_target and click_target.get("departement") in (departement or []) and cible in arrondissements:
        return options, [cible]
    return options, list(arrondissements)


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "options"),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "value", allow_duplicate=True),
    Output("carte-bar-click-target", "data", allow_duplicate=True),
    Input(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value"),
    State(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    State("carte-bar-click-target", "data"),
    prevent_initial_call=True,
)
def update_commune_options(arrondissement, departement, click_target):
    """Restreint la liste des communes proposées à l'arrondissement choisi
    (à défaut, au département choisi ; à défaut, toutes les communes), et
    sélectionne par défaut toutes les communes de la nouvelle liste (cohérent
    avec "(Tout)" = tout coché).

    [Correctif] Même exception que update_arrondissement_options : si ce
    changement provient d'un clic sur une barre ciblant précisément une
    commune, on ne sélectionne QUE cette commune-là. Ce callback est le
    dernier maillon de la cascade déclenchée par un clic sur une barre : une
    fois la cible consommée (utilisée ou non), le store est remis à None pour
    ne pas fausser une future sélection manuelle des dropdowns."""
    try:
        df = get_matrice_carte()
    except DataLoadError:
        return [], [], None

    if arrondissement:
        df = df[df[ARRONDISSEMENT_COL].isin(arrondissement)]
    elif departement:
        df = df[df[DEPARTEMENT_COL].isin(departement)]
    communes = sorted(df[NOM_COMMUNE_COL].dropna().unique())
    options = [{"label": c, "value": c} for c in communes]

    cible = (click_target or {}).get("commune")
    if click_target and click_target.get("arrondissement") in (arrondissement or []) and cible in communes:
        return options, [cible], None
    return options, list(communes), None


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-departement", "value", allow_duplicate=True),
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value", allow_duplicate=True),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "value", allow_duplicate=True),
    Output("carte-bar-click-target", "data", allow_duplicate=True),
    Input("carte-barres", "clickData"),
    State(f"{FILTER_BAR_ID_PREFIX}-niveau-geo", "value"),
    prevent_initial_call=True,
)
def filtrer_depuis_barre(click_data, niveau):
    """Un clic sur une barre applique la zone correspondante aux filtres.

    [Correctif] En plus des 3 dropdowns, on mémorise la zone exacte visée
    dans "carte-bar-click-target" : c'est ce qui permet à la cascade
    (update_arrondissement_options / update_commune_options), déclenchée en
    chaîne par le changement de département ci-dessous, de restreindre sa
    sélection à cette seule zone au lieu de tout re-sélectionner par défaut.
    Sans cela, un clic sur une barre "commune" par exemple finissait par
    sélectionner tout le département de cette commune sur la carte."""
    if not click_data or niveau == "pays":
        return no_update, no_update, no_update, no_update

    try:
        zone = click_data["points"][0]["y"]
        df = get_matrice_carte()
    except (KeyError, IndexError, DataLoadError):
        return no_update, no_update, no_update, no_update

    if niveau == "departement":
        return [zone], [], [], {"departement": zone, "arrondissement": None, "commune": None}
    if niveau == "arrondissement":
        match = df[df[ARRONDISSEMENT_COL] == zone]
        if match.empty:
            return no_update, no_update, no_update, no_update
        dept = match.iloc[0][DEPARTEMENT_COL]
        return [dept], [zone], [], {"departement": dept, "arrondissement": zone, "commune": None}
    if niveau == "commune":
        match = df[df[NOM_COMMUNE_COL] == zone]
        if match.empty:
            return no_update, no_update, no_update, no_update
        dept = match.iloc[0][DEPARTEMENT_COL]
        arr = match.iloc[0][ARRONDISSEMENT_COL]
        return [dept], [arr], [zone], {"departement": dept, "arrondissement": arr, "commune": zone}
    return no_update, no_update, no_update, no_update


@callback(
    Output(f"{FILTER_BAR_ID_PREFIX}-departement", "value", allow_duplicate=True),
    Output(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value", allow_duplicate=True),
    Output(f"{FILTER_BAR_ID_PREFIX}-commune", "value", allow_duplicate=True),
    Output("carte-bar-click-target", "data", allow_duplicate=True),
    Input("carte-choropleth", "clickData"),
    State(f"{FILTER_BAR_ID_PREFIX}-niveau-geo", "value"),
    prevent_initial_call=True,
)
def filtrer_depuis_carte(click_data, niveau):
    """[Ajout] Un clic DIRECTEMENT sur la carte (commune, arrondissement ou
    département selon le niveau géographique actif) isole cette zone, exactement
    comme un clic sur la barre correspondante (cf. filtrer_depuis_barre) : la
    carte ne montre plus ensuite QUE la zone cliquée. Sa délimitation est déjà
    mise en avant dès que la souris la survole (survol synchronisé carte <->
    barres) — ce clic ajoute l'isolement effectif sur la carte, qui persiste
    après le clic (contrairement au survol qui se relâche en sortant).

    "location" (l'identifiant géojson du point cliqué, différent du nom de
    zone affiché) est retraduit en nom de zone matrice :
    - "commune" : location = adm2_name -> retrouvé via get_matrice_carte() ;
    - "arrondissement" : location = nom d'arrondissement directement (identité,
      cf. load_geojson_arrondissements()) ;
    - "departement" : location = adm1_name1 (nom du geojson OCHA) -> retraduit
      en nom de département de la matrice via l'inverse de
      build_nom_departement_to_adm1name().
    Réutilise "carte-bar-click-target" (même mécanisme que filtrer_depuis_barre)
    pour empêcher la cascade département -> arrondissement -> commune d'écraser
    cette sélection précise."""
    if not click_data or niveau == "pays":
        return no_update, no_update, no_update, no_update

    try:
        location = click_data["points"][0]["location"]
        df = get_matrice_carte()
    except (KeyError, IndexError, DataLoadError):
        return no_update, no_update, no_update, no_update

    if niveau == "departement":
        adm1_to_dept = {v: k for k, v in build_nom_departement_to_adm1name().items() if v}
        dept = adm1_to_dept.get(location)
        if dept is None:
            return no_update, no_update, no_update, no_update
        return [dept], [], [], {"departement": dept, "arrondissement": None, "commune": None}
    if niveau == "arrondissement":
        match = df[df[ARRONDISSEMENT_COL] == location]
        if match.empty:
            return no_update, no_update, no_update, no_update
        dept = match.iloc[0][DEPARTEMENT_COL]
        return [dept], [location], [], {"departement": dept, "arrondissement": location, "commune": None}
    if niveau == "commune" or niveau is None:
        match = df[df["adm2_name"] == location]
        if match.empty:
            return no_update, no_update, no_update, no_update
        commune = match.iloc[0][NOM_COMMUNE_COL]
        dept = match.iloc[0][DEPARTEMENT_COL]
        arr = match.iloc[0][ARRONDISSEMENT_COL]
        return [dept], [arr], [commune], {"departement": dept, "arrondissement": arr, "commune": commune}
    return no_update, no_update, no_update, no_update


def build_choropleth_agrege(df_filtre, niveau, indicateur, indicator_label):
    """
    Choroplèthe pour les niveaux agrégés "pays" / "departement" / "arrondissement" :
    - fond de carte : contour national (admin0), contours départementaux OCHA
      (admin1), ou contours d'arrondissement obtenus par dissolve des communes ;
    - couleur : cluster/classe IIFT majoritaire de la zone si l'indicateur choisi
      est catégoriel, sinon somme/moyenne de l'indicateur (même règle que le
      graphique en barres) ;
    - survol : toujours population totale, IIFT moyen, nombre de communes et la
      composition (%) en clusters K-Means de la zone, quel que soit l'indicateur
      affiché en couleur.
    """
    zone_stats = build_zone_stats(df_filtre, niveau)
    if zone_stats.empty:
        fig = go.Figure()
        fig.add_annotation(text="Aucune zone ne correspond à cette sélection.", showarrow=False)
        fig.update_layout(paper_bgcolor=COLORS["surface"])
        return fig, indicator_label

    cluster_cols = [c for c in CLUSTER_LABELS_COURT.values() if c in zone_stats.columns]
    group_col = {"departement": DEPARTEMENT_COL, "arrondissement": ARRONDISSEMENT_COL, "pays": None}.get(niveau)

    if niveau == "pays":
        geojson = load_geojson_pays()
        featureidkey = "properties.adm0_name1"
        zone_stats["zone_geojson"] = zone_stats["zone"]
    elif niveau == "departement":
        geojson = load_geojson_departements()
        featureidkey = f"properties.{GEOJSON_DEPT_NAME_PROPERTY}"
        zone_stats["zone_geojson"] = zone_stats["zone"].map(build_nom_departement_to_adm1name())
    else:
        geojson = load_geojson_arrondissements()
        featureidkey = "properties.arrondissement"
        zone_stats["zone_geojson"] = zone_stats["zone"]

    hover_data = {
        "zone_geojson": False,
        "n_communes": True,
        "population_totale": ":,.0f",
        "IIFT_moyen": ":.1f",
        **{c: ":.1f" for c in cluster_cols},
    }
    common_kwargs = dict(
        geojson=geojson,
        locations="zone_geojson",
        featureidkey=featureidkey,
        mapbox_style="carto-positron",
        zoom=6.7,
        center={"lat": 18.97, "lon": -72.5},
        opacity=0.85,
        hover_name="zone",
        hover_data=hover_data,
    )

    if indicateur == "cluster_kmeans":
        zone_stats["couleur"] = zone_stats[cluster_cols].idxmax(axis=1) if cluster_cols else "—"
        # [Correctif survol, cohérent avec le niveau "commune"] Un seul trace
        # go.Choroplethmapbox (z entier + colorscale à paliers via
        # _discrete_colorscale) plutôt que px.choropleth_mapbox(color=...) qui
        # créait un trace PAR cluster — c'est ce multi-trace qui empêchait la
        # mise en surbrillance au survol de fonctionner pour ces deux
        # indicateurs (cluster_kmeans / classe_IIFT), y compris à ce niveau
        # agrégé (pays/département/arrondissement), avant ce correctif.
        ordre = list(CLUSTER_LABELS_COURT.keys())
        labels = [CLUSTER_LABELS_COURT[k] for k in ordre]
        palette = [CLUSTER_COLORS[k] for k in ordre]
        zone_stats["_z"] = zone_stats["couleur"].map({lbl: i for i, lbl in enumerate(labels)})
        fig = go.Figure(
            go.Choroplethmapbox(
                geojson=geojson,
                locations=zone_stats["zone_geojson"],
                z=zone_stats["_z"],
                featureidkey=featureidkey,
                colorscale=_discrete_colorscale(palette),
                zmin=-0.5,
                zmax=len(labels) - 0.5,
                marker_opacity=0.85,
                marker_line_width=0.5,
                showscale=False,
                showlegend=False,
                hovertext=zone_stats["zone"],
                customdata=zone_stats[["n_communes", "population_totale", "IIFT_moyen"]],
                hovertemplate=(
                    "<b>%{hovertext}</b><br>"
                    "Communes : %{customdata[0]}<br>"
                    "Population : %{customdata[1]:,.0f}<br>"
                    "IIFT moyen : %{customdata[2]:.1f}<extra></extra>"
                ),
            )
        )
        _add_legend_traces(fig, labels, palette, zone_stats["_z"])
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=6.7,
            mapbox_center={"lat": 18.97, "lon": -72.5},
        )
        legend_title = ""
    elif indicateur == "classe_IIFT":
        temp = df_filtre.copy()
        if group_col is None:
            temp["_zone"] = "Haïti"
            group_col_local = "_zone"
        else:
            group_col_local = group_col
        counts = temp.groupby([group_col_local, "classe_IIFT"]).size().rename("n").reset_index()
        counts["pct"] = counts.groupby(group_col_local)["n"].transform(lambda s: s / s.sum() * 100)
        majoritaire = (
            counts.loc[counts.groupby(group_col_local)["pct"].idxmax()]
            .rename(columns={group_col_local: "zone", "classe_IIFT": "couleur"})[["zone", "couleur"]]
        )
        zone_stats = zone_stats.merge(majoritaire, on="zone", how="left")
        # [Correctif survol] même principe que cluster_kmeans ci-dessus : un
        # seul trace au lieu d'un trace par classe IIFT.
        ordre = CLASSE_IIFT_ORDER
        palette = CLASSE_IIFT_COLORS
        zone_stats["_z"] = zone_stats["couleur"].map({k: i for i, k in enumerate(ordre)})
        fig = go.Figure(
            go.Choroplethmapbox(
                geojson=geojson,
                locations=zone_stats["zone_geojson"],
                z=zone_stats["_z"],
                featureidkey=featureidkey,
                colorscale=_discrete_colorscale(palette),
                zmin=-0.5,
                zmax=len(ordre) - 0.5,
                marker_opacity=0.85,
                marker_line_width=0.5,
                showscale=False,
                showlegend=False,
                hovertext=zone_stats["zone"],
                customdata=zone_stats[["n_communes", "population_totale", "IIFT_moyen"]],
                hovertemplate=(
                    "<b>%{hovertext}</b><br>"
                    "Communes : %{customdata[0]}<br>"
                    "Population : %{customdata[1]:,.0f}<br>"
                    "IIFT moyen : %{customdata[2]:.1f}<extra></extra>"
                ),
            )
        )
        _add_legend_traces(fig, ordre, palette, zone_stats["_z"])
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=6.7,
            mapbox_center={"lat": 18.97, "lon": -72.5},
        )
        legend_title = "Classe IIFT majoritaire"
    else:
        aggregation = "sum" if indicateur in SUM_INDICATORS else "mean"
        if group_col is None:
            valeur_df = pd.DataFrame({"zone": ["Haïti"], "valeur": [getattr(df_filtre[indicateur], aggregation)()]})
        else:
            valeur_df = (
                df_filtre.groupby(group_col, as_index=False)[indicateur]
                .agg(aggregation)
                .rename(columns={group_col: "zone", indicateur: "valeur"})
            )
        zone_stats = zone_stats.merge(valeur_df, on="zone", how="left")
        fig = px.choropleth_mapbox(
            zone_stats,
            color="valeur",
            color_continuous_scale=[COLORS["petrole_200"], COLORS["petrole_500"], COLORS["petrole_900"]],
            labels={"valeur": indicator_label},
            **common_kwargs,
        )
        legend_title = indicator_label

    return fig, legend_title


def _discrete_colorscale(colors):
    """Construit une colorscale Plotly à PALIERS NETS (pas de dégradé) à
    partir d'une liste de couleurs — une couleur par catégorie, indexée par
    un entier consécutif (0, 1, 2, ...). Chaque couleur occupe une bande de
    largeur 1 centrée sur son entier ; à utiliser avec zmin=-0.5 et
    zmax=len(colors)-0.5 sur le trace go.Choroplethmapbox correspondant.

    [Correctif survol carte] Utilisé pour "Cluster K-Means" et "Classe IIFT"
    afin de forcer un SEUL trace Choroplethmapbox (z entier + cette
    colorscale à paliers) au lieu de laisser Plotly Express créer un trace
    PAR CATÉGORIE, comme il le fait par défaut dès que `color=` pointe vers
    une colonne catégorielle (px.choropleth_mapbox(df, color="...")). Avec
    plusieurs traces choroplethmapbox superposées sur la même carte Mapbox
    GL, le survol de la souris (hoverData) ne se déclenchait de façon
    fiable/cohérente que pour une partie des traces — d'où la mise en
    surbrillance au survol (cf. clientside_callback plus bas) qui ne
    fonctionnait plus UNIQUEMENT pour ces deux indicateurs (les seuls
    catégoriels de la page), alors qu'elle marchait pour tous les
    indicateurs continus (un seul trace généré par Plotly Express dans ce
    cas). Revenir à un seul trace, comme pour les indicateurs continus,
    élimine ce cas particulier."""
    n = len(colors)
    scale = []
    for i, color in enumerate(colors):
        scale.append([i / n, color])
        scale.append([(i + 1) / n, color])
    return scale


def _add_legend_traces(fig, labels, palette, z_values):
    """Ajoute au graphique une trace de légende (invisible sur la carte,
    juste puce de couleur + libellé) par catégorie, à partir des libellés/
    couleurs déjà ordonnés (index i = catégorie i dans z_values).

    [Ajout] Une catégorie peut n'avoir AUCUNE zone au niveau géographique /
    filtre courant (ex. "Pôles d'inclusion financière avancée" au niveau
    Département : aucun département où ce cluster est majoritaire). Comme la
    légende sert désormais uniquement de description statique des catégories
    (et non plus de filtre interactif), on rend ce cas explicite plutôt que
    de laisser deviner pourquoi aucune zone de cette couleur n'apparaît sur
    la carte : puce atténuée (opacity 0.35, cohérent avec le griséage déjà
    appliqué ailleurs) ET mention "(aucune zone)" ajoutée au libellé lui-même
    — visible sans avoir à survoler quoi que ce soit."""
    presentes = pd.Series(z_values).dropna().astype(int).value_counts()
    for i, (label, color) in enumerate(zip(labels, palette)):
        a_une_zone = int(presentes.get(i, 0)) > 0
        nom_legende = label if a_une_zone else f"{label} <i>(aucune zone)</i>"
        fig.add_trace(
            go.Scattermapbox(
                lat=[None],
                lon=[None],
                mode="markers",
                marker=dict(size=10, color=color, opacity=1 if a_une_zone else 0.35),
                name=nom_legende,
                showlegend=True,
                hoverinfo="skip",
            )
        )


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in rgb))


def _interpoler_couleur(t, paliers):
    """Interpole une couleur hex le long d'un dégradé à plusieurs paliers
    (ex. [petrole_200, petrole_500, petrole_900]), t entre 0 et 1 — même
    logique que le dégradé continu (color_continuous_scale) utilisé sur la
    carte, pour que le diagramme en barre reprenne visuellement les mêmes
    teintes."""
    t = min(max(t, 0), 1)
    n = len(paliers) - 1
    segment = t * n
    i = min(int(segment), n - 1)
    t_local = segment - i
    c0, c1 = _hex_to_rgb(paliers[i]), _hex_to_rgb(paliers[i + 1])
    return _rgb_to_hex(tuple(c0[k] + (c1[k] - c0[k]) * t_local for k in range(3)))


def build_zone_colors(df_filtre, niveau, indicateur):
    """
    Calcule, pour chaque zone (commune, ou département/arrondissement/pays si
    agrégé), la couleur à utiliser pour le diagramme en barre — LA MÊME que
    celle utilisée pour cette zone sur la carte choroplèthe, quel que soit
    l'indicateur de demande choisi :
    - "Cluster K-Means" / "Classe IIFT" (catégoriels) : couleur discrète de
      la catégorie (identique à build_choropleth_agrege pour les niveaux
      agrégés).
    - tout autre indicateur (continu) : couleur interpolée sur le même
      dégradé pétrole (petrole_200 -> 500 -> 900) que la carte, normalisée
      sur le min/max de la sélection courante — la même normalisation que
      Plotly applique par défaut sur la carte.

    Au niveau commune, la couleur/valeur vient directement de la commune.
    Aux niveaux agrégés, on reprend la même règle d'agrégation que la carte
    et le diagramme (majorité pour les catégoriels, somme/moyenne selon
    SUM_INDICATORS pour les continus).
    """
    if df_filtre.empty:
        return None

    if indicateur not in ("cluster_kmeans", "classe_IIFT"):
        # --- Indicateur continu : dégradé interpolé, normalisé sur la sélection ---
        paliers = [COLORS["petrole_200"], COLORS["petrole_500"], COLORS["petrole_900"]]
        if niveau in (None, "commune"):
            if indicateur not in df_filtre.columns:
                return None
            valeurs = dict(zip(df_filtre[NOM_COMMUNE_COL], df_filtre[indicateur]))
        else:
            group_col = {"departement": DEPARTEMENT_COL, "arrondissement": ARRONDISSEMENT_COL, "pays": None}.get(
                niveau
            )
            aggregation = "sum" if indicateur in SUM_INDICATORS else "mean"
            if group_col is None:
                valeurs = {"Haïti": getattr(df_filtre[indicateur], aggregation)()}
            else:
                valeurs = df_filtre.groupby(group_col)[indicateur].agg(aggregation).to_dict()

        nombres = [v for v in valeurs.values() if pd.notna(v)]
        if not nombres:
            return {}
        vmin, vmax = min(nombres), max(nombres)
        etendue = (vmax - vmin) or 1
        return {
            zone: _interpoler_couleur((v - vmin) / etendue, paliers)
            for zone, v in valeurs.items()
            if pd.notna(v)
        }

    classe_couleur = dict(zip(CLASSE_IIFT_ORDER, CLASSE_IIFT_COLORS))

    if niveau in (None, "commune"):
        if indicateur == "cluster_kmeans":
            return {
                row[NOM_COMMUNE_COL]: CLUSTER_COLORS.get(str(row["cluster_kmeans"]))
                for _, row in df_filtre.iterrows()
            }
        return {row[NOM_COMMUNE_COL]: classe_couleur.get(row["classe_IIFT"]) for _, row in df_filtre.iterrows()}

    group_col = {"departement": DEPARTEMENT_COL, "arrondissement": ARRONDISSEMENT_COL, "pays": None}.get(niveau)

    if indicateur == "cluster_kmeans":
        zone_stats = build_zone_stats(df_filtre, niveau)
        cluster_cols = [c for c in CLUSTER_LABELS_COURT.values() if c in zone_stats.columns]
        if not cluster_cols:
            return {}
        label_to_id = {v: k for k, v in CLUSTER_LABELS_COURT.items()}
        zone_stats = zone_stats.copy()
        zone_stats["_majoritaire"] = zone_stats[cluster_cols].idxmax(axis=1)
        return {
            row["zone"]: CLUSTER_COLORS.get(label_to_id.get(row["_majoritaire"]))
            for _, row in zone_stats.iterrows()
        }

    # classe_IIFT, niveaux agrégés
    temp = df_filtre.copy()
    if group_col is None:
        temp["_zone"] = "Haïti"
        group_col_local = "_zone"
    else:
        group_col_local = group_col
    counts = temp.groupby([group_col_local, "classe_IIFT"]).size().rename("n").reset_index()
    counts["pct"] = counts.groupby(group_col_local)["n"].transform(lambda s: s / s.sum() * 100)
    majoritaire = counts.loc[counts.groupby(group_col_local)["pct"].idxmax()]
    return {row[group_col_local]: classe_couleur.get(row["classe_IIFT"]) for _, row in majoritaire.iterrows()}


# ---------------------------------------------------------------------------
# Carte principale
# ---------------------------------------------------------------------------

@callback(
    Output("carte-choropleth", "figure"),
    Output("carte-barres", "figure"),
    Output("carte-bar-title", "children"),
    Output("carte-barres-type", "figure"),
    Output("carte-barres-type-title", "children"),
    Output("carte-barres-type-container", "style"),
    Output(f"{FILTER_BAR_ID_PREFIX}-total", "children"),
    Output(f"{FILTER_BAR_ID_PREFIX}-selectionne", "children"),
    Output(f"{FILTER_BAR_ID_PREFIX}-total-points", "children"),
    Output(f"{FILTER_BAR_ID_PREFIX}-points-selectionne", "children"),
    Output("selection-store", "data"),
    Output("carte-zone-location-map", "data"),
    Input("carte-offre-indicateur", "value"),
    Input("carte-demande-indicateur", "value"),
    Input("carte-type-prestataire", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-niveau-geo", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-departement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-arrondissement", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-commune", "value"),
    Input(f"{FILTER_BAR_ID_PREFIX}-cluster", "value"),
    Input("carte-choropleth", "clickData"),
    State("selection-store", "data"),
)
def update_carte(
    offre_indicateur,
    demande_indicateur,
    type_prestataire,
    niveau,
    departement,
    arrondissement,
    commune,
    cluster,
    click_data,
    selection,
):
    # "carte-demande-indicateur" couvre maintenant aussi les indicateurs
    # d'analyse génériques (cluster K-Means, classe IIFT, IIFT...) — fusionnés
    # dans ce même dropdown. Un indicateur de demande/analyse choisi remplace
    # temporairement l'indicateur d'offre afin de comparer facilement l'offre
    # et les caractéristiques de la population avec les mêmes filtres
    # territoriaux.
    indicateur = demande_indicateur or offre_indicateur or DEFAULT_MAP_INDICATOR
    try:
        df = get_matrice_carte()
        geojson = load_geojson_communes()
    except DataLoadError:
        return (
            go.Figure(),
            go.Figure(),
            "Graphique indisponible",
            go.Figure(),
            "",
            {"display": "none"},
            "—",
            "—",
            "—",
            "—",
            selection or {"commune": None, "cluster": "all"},
            {},
        )

    total = len(df)
    df_filtre = df
    if departement:
        df_filtre = df_filtre[df_filtre[DEPARTEMENT_COL].isin(departement)]
    if arrondissement:
        df_filtre = df_filtre[df_filtre[ARRONDISSEMENT_COL].isin(arrondissement)]
    if commune:
        df_filtre = df_filtre[df_filtre[NOM_COMMUNE_COL].isin(commune)]
    if cluster:
        df_filtre = df_filtre[df_filtre["cluster_kmeans"].isin([str(c) for c in cluster])]
    n_selection = len(df_filtre)

    # [Correctif] "Type prestataire" est multi-choix (crochets), "(Tout)" par
    # défaut = les 6 types cochés explicitement. types_selectionnes est
    # normalisé à une liste vide quand rien n'est choisi OU que les 6 types
    # sont cochés (les deux cas sont équivalents à "tous confondus") :
    # vide -> tous les types confondus (brh_total_effectif), un seul type ->
    # ce type précis, plusieurs types (mais pas tous) -> somme des types
    # choisis. cols_pour_total sert au calcul des KPI "Total points / type"
    # (somme colonne par colonne, quel que soit le nombre de types
    # sélectionnés).
    types_bruts = [t for t in (type_prestataire or []) if t in TYPE_PRESTATAIRE_LABELS]
    types_selectionnes = [] if not types_bruts or set(types_bruts) == set(TYPE_PRESTATAIRE_LABELS) else types_bruts
    cols_pour_total = types_selectionnes or ["brh_total_effectif"]
    total_points = f"{int(df[cols_pour_total].sum(axis=1).sum()):,}".replace(",", " ")
    points_selectionnes = f"{int(df_filtre[cols_pour_total].sum(axis=1).sum()):,}".replace(",", " ")

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
    indicator_label = (
        OFFER_INDICATOR_LABELS.get(indicateur)
        or DEMAND_INDICATOR_LABELS.get(indicateur)
        or BRH_SERVICE_INDICATOR_LABELS.get(indicateur)
        or INDICATOR_LABELS.get(indicateur, indicateur)
    )

    if niveau == "commune" or niveau is None:
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
            # [Correctif] Légende simplifiée : on utilise CLUSTER_LABELS_COURT
            # ("Zones d'exclusion financière", etc.) plutôt que CLUSTER_LABELS
            # (qui inclut le détail statistique complet "— Cluster K-Means
            # Très faible (IIFT moy. 13 ; Dim1 moy. -1,95 ; n=74)") — beaucoup
            # trop long pour une légende de carte. Le détail statistique
            # complet reste disponible ailleurs (ex. clustering_afcm.py).
            #
            # [Correctif survol] cf. docstring de _discrete_colorscale : un
            # seul trace go.Choroplethmapbox (z entier + colorscale à
            # paliers), PAS px.choropleth_mapbox(color=...) qui créerait un
            # trace par cluster et cassait la surbrillance au survol.
            ordre = list(CLUSTER_LABELS_COURT.keys())  # ["0", "2", "1"] — sévérité croissante
            labels = [CLUSTER_LABELS_COURT[k] for k in ordre]
            palette = [CLUSTER_COLORS[k] for k in ordre]
            df_plot = df_filtre.copy()
            df_plot["_z"] = df_plot["cluster_kmeans"].astype(str).map({k: i for i, k in enumerate(ordre)})
            fig = go.Figure(
                go.Choroplethmapbox(
                    geojson=geojson,
                    locations=df_plot["adm2_name"],
                    z=df_plot["_z"],
                    featureidkey=f"properties.{GEOJSON_NAME_PROPERTY}",
                    colorscale=_discrete_colorscale(palette),
                    zmin=-0.5,
                    zmax=len(ordre) - 0.5,
                    marker_opacity=0.85,
                    marker_line_width=0.5,
                    showscale=False,
                    showlegend=False,
                    hovertext=df_plot["nom_commune"],
                    customdata=df_plot[["departement", "IIFT"]],
                    hovertemplate=(
                        "<b>%{hovertext}</b><br>"
                        "Département : %{customdata[0]}<br>"
                        "IIFT : %{customdata[1]:.1f}<extra></extra>"
                    ),
                )
            )
            # Légende manuelle : traces scattermapbox invisibles (point à
            # coordonnées None -> jamais dessinés), uniquement pour afficher
            # les puces de couleur + libellés dans la légende.
            _add_legend_traces(fig, labels, palette, df_plot["_z"])
            fig.update_layout(
                mapbox_style="carto-positron",
                mapbox_zoom=6.7,
                mapbox_center={"lat": 18.97, "lon": -72.5},
            )
            legend_title = ""
        elif indicateur == "classe_IIFT":
            # [Correctif survol] même principe que pour cluster_kmeans
            # ci-dessus : un seul trace au lieu d'un trace par classe IIFT.
            ordre = CLASSE_IIFT_ORDER
            palette = CLASSE_IIFT_COLORS
            df_plot = df_filtre.copy()
            df_plot["_z"] = df_plot["classe_IIFT"].map({k: i for i, k in enumerate(ordre)})
            fig = go.Figure(
                go.Choroplethmapbox(
                    geojson=geojson,
                    locations=df_plot["adm2_name"],
                    z=df_plot["_z"],
                    featureidkey=f"properties.{GEOJSON_NAME_PROPERTY}",
                    colorscale=_discrete_colorscale(palette),
                    zmin=-0.5,
                    zmax=len(ordre) - 0.5,
                    marker_opacity=0.85,
                    marker_line_width=0.5,
                    showscale=False,
                    showlegend=False,
                    hovertext=df_plot["nom_commune"],
                    customdata=df_plot[["departement", "IIFT"]],
                    hovertemplate=(
                        "<b>%{hovertext}</b><br>"
                        "Département : %{customdata[0]}<br>"
                        "IIFT : %{customdata[1]:.1f}<extra></extra>"
                    ),
                )
            )
            _add_legend_traces(fig, ordre, palette, df_plot["_z"])
            fig.update_layout(
                mapbox_style="carto-positron",
                mapbox_zoom=6.7,
                mapbox_center={"lat": 18.97, "lon": -72.5},
            )
            legend_title = "Classe IIFT"
        else:
            fig = px.choropleth_mapbox(
                df_filtre,
                color=indicateur,
                color_continuous_scale=[
                    COLORS["petrole_200"],
                    COLORS["petrole_500"],
                    COLORS["petrole_900"],
                ],
                hover_data={indicateur: ":.2f", "departement": True, "adm2_name": False},
                labels={indicateur: indicator_label},
                **common_kwargs,
            )
            legend_title = indicator_label
    else:
        # Niveaux agrégés (pays / département / arrondissement) : le fond de
        # carte, la colonne de jointure et le nom de zone changent tous les
        # trois selon "niveau" ; les indicateurs bruts par commune n'existent
        # plus tels quels ici, ils sont recalculés zone par zone (somme ou
        # moyenne selon SUM_INDICATORS, comme pour le graphique en barres).
        fig, legend_title = build_choropleth_agrege(df_filtre, niveau, indicateur, indicator_label)

    # [Correctif] La légende (indicateurs catégoriels) et la barre de couleur
    # (indicateurs continus) s'affichaient auparavant à côté/par-dessus la
    # carte (à droite, x=0.98) — désormais toutes deux affichées EN DESSOUS de
    # la carte, à l'horizontale et raccourcies (len=0.55 / une seule ligne de
    # légende), via une marge basse (b=70) qui leur réserve la place.
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=70),
        font_family="Inter, sans-serif",
        paper_bgcolor=COLORS["surface"],
        legend=dict(
            title=dict(text=legend_title, font=dict(size=11)),
            orientation="h",
            yanchor="top",
            y=-0.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
            font=dict(size=10),
        ),
    )
    if not is_categorical:
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=dict(text=legend_title, font=dict(size=11)),
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.05,
                yanchor="top",
                len=0.55,
                thickness=10,
            )
        )

    # [Correctif] Le diagramme en barre (panneau à côté de la carte) affiche
    # désormais TOUJOURS les valeurs de l'indicateur d'offre — jamais celles
    # de l'indicateur de demande/analyse, même quand celui-ci pilote la
    # couleur de la carte. Seule la carte (fig, ci-dessus) continue de suivre
    # la règle de priorité demande > offre ; le panneau de droite reste
    # entièrement dédié à l'offre (nb de points d'accès, par type et par
    # niveau géographique). "brh_total_effectif" sert de repli tant qu'aucun
    # indicateur d'offre n'est explicitement choisi (dropdown clearable).
    offre_pour_graphique = offre_indicateur or "brh_total_effectif"
    label_override = None
    # [Ajout] "Nb de points d'accès" (choix par défaut de l'indicateur d'offre)
    # est influencé par le "Type prestataire" choisi : si un ou plusieurs
    # types précis sont sélectionnés (autre que "(Tout)"), le graphique par
    # niveau géographique bascule sur ce(s) type(s) plutôt que sur le total
    # tous types confondus (un seul type -> sa colonne directement ; plusieurs
    # types -> somme des colonnes choisies, calculée à la volée). Un
    # indicateur d'offre différent choisi explicitement (ex. densité
    # bancaire) reste, lui, inchangé par ce filtre.
    if offre_pour_graphique == "brh_total_effectif":
        if len(types_selectionnes) == 1:
            offre_pour_graphique = types_selectionnes[0]
        elif len(types_selectionnes) > 1:
            df_filtre = df_filtre.copy()
            df_filtre["_prestataire_selection"] = df_filtre[types_selectionnes].sum(axis=1)
            offre_pour_graphique = "_prestataire_selection"
            label_override = " + ".join(TYPE_PRESTATAIRE_LABELS[c] for c in types_selectionnes)
    bar_fig, bar_title = build_bar_chart(
        df_filtre,
        offre_pour_graphique,
        niveau,
        label_override=label_override,
        zone_colors=build_zone_colors(df_filtre, niveau, indicateur),
    )

    # [Ajout] Le diagramme du haut (répartition par type de prestataire) est
    # lui aussi influencé par la sélection : "(Tout)" affiche les 6 familles
    # habituelles, un seul type sélectionné affiche une seule barre, plusieurs
    # types affichent uniquement les barres correspondantes.
    top_fig = build_bar_chart_type_prestataire(df_filtre, types_selectionnes)
    if len(types_selectionnes) == 1:
        top_title = f"Nb de points d'accès — {TYPE_PRESTATAIRE_LABELS[types_selectionnes[0]]}"
    elif len(types_selectionnes) > 1:
        top_title = "Nb de points d'accès par type sélectionné"
    else:
        top_title = "Nb de points d'accès par type de prestataire"
    top_style = {"display": "block"}

    # [Ajout] Correspondance nom de zone (axe des barres) -> identifiant de
    # localisation sur la carte (locations du tracé choroplèthe), pour le
    # survol synchronisé carte <-> barres. Recalculée sur df_filtre, donc
    # limitée aux zones effectivement affichées.
    if niveau == "departement":
        adm1_map = build_nom_departement_to_adm1name()
        zone_location_map = {
            d: adm1_map.get(d, d) for d in df_filtre[DEPARTEMENT_COL].dropna().unique()
        }
    elif niveau == "arrondissement":
        zone_location_map = {a: a for a in df_filtre[ARRONDISSEMENT_COL].dropna().unique()}
    elif niveau == "commune" or niveau is None:
        zone_location_map = (
            df_filtre.drop_duplicates(subset=[NOM_COMMUNE_COL])
            .set_index(NOM_COMMUNE_COL)["adm2_name"]
            .to_dict()
        )
    else:
        # "pays" : une seule zone affichée, le survol synchronisé n'apporte
        # rien de plus — pas de correspondance à construire.
        zone_location_map = {}

    return (
        fig,
        bar_fig,
        bar_title,
        top_fig,
        top_title,
        top_style,
        str(total),
        str(n_selection),
        total_points,
        points_selectionnes,
        nouvelle_selection,
        zone_location_map,
    )


# ---------------------------------------------------------------------------
# Survol synchronisé carte <-> diagramme en barre
# ---------------------------------------------------------------------------
# [Ajout] Callback 100% côté client (aucun aller-retour serveur, donc réactif
# au pixel près) : quand la souris survole une zone sur la carte OU la barre
# correspondante, les DEUX sont mises en évidence en même temps (bordure
# foncée + zones non survolées atténuées). "carte-zone-location-map" (recalculé
# par update_carte à chaque changement de niveau/filtre) fait le lien entre le
# nom de zone affiché sur l'axe des barres et l'identifiant de localisation
# utilisé par le tracé choroplèthe pour cette même zone.
clientside_callback(
    """
    function(hoverMap, hoverBar, zoneLocMap) {
        // [Correctif] Selon la version de Dash, l'id posé sur dcc.Graph peut
        // se retrouver soit directement sur le div géré par Plotly (a une
        // propriété .data), soit sur un div englobant qui CONTIENT le vrai
        // div Plotly (reconnaissable à sa classe "js-plotly-plot") — d'où
        // cette fonction de recherche au lieu d'un simple getElementById.
        function findPlotlyDiv(id) {
            var el = document.getElementById(id);
            if (!el) { return null; }
            if (el.data) { return el; }
            var inner = el.querySelector ? el.querySelector('.js-plotly-plot') : null;
            if (inner && inner.data) { return inner; }
            return null;
        }

        var mapDiv = findPlotlyDiv('carte-choropleth');
        var barDiv = findPlotlyDiv('carte-barres');
        if (!mapDiv || !barDiv) {
            console.warn(
                '[hover-sync] graphique Plotly introuvable — mapDiv=', !!mapDiv, 'barDiv=', !!barDiv,
                '(vérifier que les ids carte-choropleth / carte-barres existent bien dans le DOM et sont déjà rendus par Plotly)'
            );
            return window.dash_clientside.no_update;
        }
        zoneLocMap = zoneLocMap || {};

        // [Ajout] Logique de surbrillance mise en commun (carte + barres),
        // réutilisée à la fois par le survol normal (via hoverData, ci-dessous)
        // et par les écouteurs "plotly_unhover" natifs branchés plus bas —
        // ces derniers sont nécessaires car, sur les cartes mapbox, Plotly ne
        // déclenche pas toujours l'événement qui remettrait "hoverData" à vide
        // côté Dash quand la souris quitte la carte : sans eux, la surbrillance
        // pouvait rester bloquée sur la dernière zone survolée.
        function appliquerSurbrillance(hoveredLocation, hoveredZone) {
            try {
                // [Historique] "_hiddenZ" n'est plus jamais posé (le filtre
                // par clic sur la légende a été retiré, cf. plus bas —
                // remplacé par une mise en avant au survol). Cette lecture
                // reste en place par sécurité : elle vaudra toujours `null`,
                // donc sans effet sur la logique de survol carte/barres.
                var hiddenZ = mapDiv._hiddenZ || null;
                mapDiv.data.forEach(function(trace, traceIdx) {
                    if (!trace.locations) { return; }
                    var n = trace.locations.length;
                    var opacities = new Array(n).fill(hoveredLocation ? 0.45 : 0.85);
                    var lineWidths = new Array(n).fill(0.5);
                    var lineColors = new Array(n).fill('#4A4A4A');
                    for (var i = 0; i < n; i++) {
                        if (hiddenZ && trace.z && hiddenZ.has(trace.z[i])) {
                            opacities[i] = 0.05;
                            continue;
                        }
                        if (hoveredLocation && trace.locations[i] === hoveredLocation) {
                            opacities[i] = 1;
                            lineWidths[i] = 3;
                            lineColors[i] = '#111111';
                        }
                    }
                    Plotly.restyle(mapDiv, {
                        'marker.opacity': [opacities],
                        'marker.line.width': [lineWidths],
                        'marker.line.color': [lineColors]
                    }, [traceIdx]);
                });
            } catch (e) { console.error('[hover-sync] erreur restyle carte:', e); }

            try {
                barDiv.data.forEach(function(trace, traceIdx) {
                    if (!trace.y) { return; }
                    var n = trace.y.length;
                    var widths = new Array(n).fill(0);
                    var colors = new Array(n).fill('rgba(0,0,0,0)');
                    for (var i = 0; i < n; i++) {
                        if (hoveredZone && trace.y[i] === hoveredZone) {
                            widths[i] = 3;
                            colors[i] = '#111111';
                        }
                    }
                    Plotly.restyle(barDiv, {
                        'marker.line.width': [widths],
                        'marker.line.color': [colors]
                    }, [traceIdx]);
                });
            } catch (e) { console.error('[hover-sync] erreur restyle barres:', e); }
        }

        // [Ajout] Écouteurs natifs Plotly, branchés une seule fois par div
        // (flag _hoverSyncBound pour éviter les doublons à chaque re-rendu) :
        // dès que la souris quitte réellement la carte ou les barres, on
        // revient à l'état par défaut, sans dépendre du cycle hoverData de Dash.
        if (!mapDiv._hoverSyncBound && mapDiv.on) {
            mapDiv._hoverSyncBound = true;
            mapDiv.on('plotly_unhover', function() { appliquerSurbrillance(null, null); });
        }
        if (!barDiv._hoverSyncBound && barDiv.on) {
            barDiv._hoverSyncBound = true;
            barDiv.on('plotly_unhover', function() { appliquerSurbrillance(null, null); });
        }

        var triggered = (window.dash_clientside.callback_context.triggered || [])[0];
        var triggerId = triggered ? triggered.prop_id.split('.')[0] : null;

        var hoveredLocation = null;
        var hoveredZone = null;

        if (triggerId === 'carte-choropleth' && hoverMap && hoverMap.points && hoverMap.points.length) {
            hoveredLocation = hoverMap.points[0].location;
            for (var z in zoneLocMap) {
                if (zoneLocMap[z] === hoveredLocation) { hoveredZone = z; break; }
            }
        } else if (triggerId === 'carte-barres' && hoverBar && hoverBar.points && hoverBar.points.length) {
            hoveredZone = hoverBar.points[0].y;
            hoveredLocation = zoneLocMap[hoveredZone] || null;
        }

        console.log('[hover-sync] trigger=', triggerId, 'zone=', hoveredZone, 'location=', hoveredLocation, 'mapDivFound=', !!mapDiv, 'barDivFound=', !!barDiv);

        appliquerSurbrillance(hoveredLocation, hoveredZone);

        return window.dash_clientside.no_update;
    }
    """,
    Output("carte-hover-sync-dummy", "data"),
    Input("carte-choropleth", "hoverData"),
    Input("carte-barres", "hoverData"),
    State("carte-zone-location-map", "data"),
    prevent_initial_call=True,

)


# ---------------------------------------------------------------------------
# Survol de la légende (indicateurs catégoriels) : mettre en avant une
# catégorie
# ---------------------------------------------------------------------------
# [Retiré] Le filtre par clic/double-clic sur la légende (isoler une
# catégorie, cf. anciennes versions) est abandonné : trop de conflits avec le
# rendu Mapbox GL pour un gain limité, d'autant que le filtre "Cluster
# K-Means" en haut de la barre de filtres couvre déjà ce besoin.
# [Ajout] À la place, survoler une entrée de la légende (Cluster K-Means /
# Classe IIFT) met en avant sur la carte toutes les communes de cette
# catégorie — même logique visuelle (opacité pleine + bordure foncée pour le
# groupe visé, opacité réduite pour le reste) que le survol d'une commune sur
# la carte elle-même (cf. callback [hover-sync] plus haut). Comme Plotly.js
# n'expose pas d'événement natif de survol sur les entrées de légende, on
# écoute directement les éléments DOM SVG (".legend .traces") : leur ordre
# correspond à celui des traces scattermapbox invisibles qui composent la
# légende (trace 1 -> catégorie 0, trace 2 -> catégorie 1, etc.).
# [Correctif] Le trace go.Choroplethmapbox lui-même a "showlegend=False" —
# sans quoi Plotly lui ajoute par défaut sa propre entrée (vide) EN
# PREMIÈRE position dans la légende, ce qui décalait d'un cran la
# correspondance entre l'ordre des entrées de légende dans le DOM et
# l'index de catégorie (z) : plus aucune commune ne correspondait à la
# catégorie survolée, d'où toute la carte atténuée au lieu de la mise en
# avant attendue.
# [Ajout] Certaines catégories n'ont AUCUNE zone au niveau géographique /
# filtre courant (ex. "Pôles d'inclusion financière avancée" : 0 département
# sur 10 n'y est majoritaire ; niveau Pays : une seule zone au total, donc 4
# des 5 classes IIFT sont forcément vides). Ce n'est pas un bug — juste une
# absence réelle dans les données à ce niveau d'agrégation — mais survoler
# une telle entrée éteignait quand même toute la carte (aucune correspondance
# à mettre en avant), ce qui ressemblait à un plantage. Ces entrées sont donc
# déjà grisées ET explicitement libellées "(aucune zone)" au niveau Python
# (cf. _add_legend_traces) ; le JS ci-dessous se contente de désactiver leur
# survol (pointeur normal, pas de mise en avant possible).
clientside_callback(
    """
    function(figure) {
        function findPlotlyDiv(id) {
            var el = document.getElementById(id);
            if (!el) { return null; }
            if (el.data) { return el; }
            var inner = el.querySelector ? el.querySelector('.js-plotly-plot') : null;
            if (inner && inner.data) { return inner; }
            return null;
        }

        // [Correctif] Au moment où Dash déclenche ce callback (mise à jour
        // de la prop "figure"), le graphique Plotly (et son SVG de légende)
        // n'est pas toujours encore monté dans le DOM (React/Plotly.react()
        // rendent de façon asynchrone) — surtout au premier affichage de
        // l'onglet Carte. On retente plusieurs fois avant d'abandonner.
        function tenterBinding(essaisRestants) {
            var mapDiv = findPlotlyDiv('carte-choropleth');
            if (!mapDiv || !mapDiv.data || !mapDiv.data.length) {
                if (essaisRestants > 0) {
                    setTimeout(function() { tenterBinding(essaisRestants - 1); }, 150);
                } else {
                    console.warn('[legend-hover] graphique carte-choropleth introuvable après plusieurs tentatives.');
                }
                return;
            }

            var legendEl = mapDiv.querySelector ? mapDiv.querySelector('g.legend') : null;
            var traceGroups = legendEl ? legendEl.querySelectorAll('.traces') : [];
            if (!legendEl || !traceGroups.length) {
                if (essaisRestants > 0) {
                    setTimeout(function() { tenterBinding(essaisRestants - 1); }, 150);
                } else {
                    console.warn('[legend-hover] entrées de légende introuvables dans le DOM après plusieurs tentatives (indicateur continu, sans légende catégorielle ?).');
                }
                return;
            }

            // [Ajout] Empêche le comportement par défaut de Plotly au clic
            // sur la légende (masquer/afficher la trace cliquée), qui
            // provoquait une erreur Mapbox — sans rien tenter d'autre à la
            // place (le filtre par clic est abandonné, cf. commentaire
            // ci-dessus).
            if (!mapDiv._legendClickBlocked) {
                mapDiv._legendClickBlocked = true;
                mapDiv.on('plotly_legendclick', function() { return false; });
                mapDiv.on('plotly_legenddoubleclick', function() { return false; });
            }

            function surbrillerCategorie(zi) {
                try {
                    var choroTrace = mapDiv.data[0];
                    if (!choroTrace || !choroTrace.locations || !choroTrace.z) { return; }
                    var n = choroTrace.locations.length;
                    var opacities = new Array(n);
                    var lineWidths = new Array(n);
                    var lineColors = new Array(n);
                    for (var i = 0; i < n; i++) {
                        if (zi === null) {
                            opacities[i] = 0.85;
                            lineWidths[i] = 0.5;
                            lineColors[i] = '#4A4A4A';
                        } else if (Number(choroTrace.z[i]) === zi) {
                            opacities[i] = 1;
                            lineWidths[i] = 3;
                            lineColors[i] = '#111111';
                        } else {
                            opacities[i] = 0.15;
                            lineWidths[i] = 0.5;
                            lineColors[i] = '#4A4A4A';
                        }
                    }
                    Plotly.restyle(mapDiv, {
                        'marker.opacity': [opacities],
                        'marker.line.width': [lineWidths],
                        'marker.line.color': [lineColors]
                    }, [0]);
                } catch (e) { console.error('[legend-hover] erreur restyle carte:', e); }
            }

            // [Ajout] Certaines catégories (ex. "Pôles d'inclusion financière
            // avancée" au niveau Département, ou n'importe quelle catégorie
            // autre que celle de l'unique zone au niveau Pays) n'ont AUCUNE
            // zone au niveau géographique / filtre courant — ce n'est pas un
            // bug, juste une absence réelle dans les données à ce niveau
            // d'agrégation. Les survoler mettrait quand même toute la carte
            // en retrait (aucune correspondance à mettre en avant), ce qui
            // ressemble à un plantage plutôt qu'à une absence normale de
            // données. On grise donc ces entrées à l'avance (estompées,
            // curseur normal) et on désactive leur survol, plutôt que de
            // laisser l'utilisateur déclencher un "toute la carte s'éteint"
            // sans explication. Recalculé à CHAQUE mise à jour de la figure
            // (les catégories présentes changent avec le niveau géographique
            // et les filtres), même pour des éléments DOM déjà liés.
            var choroTrace = mapDiv.data[0];
            var categoriesPresentes = new Set();
            if (choroTrace && choroTrace.z) {
                for (var k = 0; k < choroTrace.z.length; k++) {
                    var valeurZ = choroTrace.z[k];
                    if (valeurZ !== null && valeurZ !== undefined && !Number.isNaN(Number(valeurZ))) {
                        categoriesPresentes.add(Number(valeurZ));
                    }
                }
            }

            traceGroups.forEach(function(g, zi) {
                var presente = categoriesPresentes.has(zi);
                // [Ajout] Mémorisé sur l'élément lui-même et RAFRAÎCHI à
                // chaque appel (même pour un élément déjà lié) : c'est cette
                // valeur, pas un nouveau calcul, que le survol relira plus
                // bas — les éléments DOM de la légende peuvent être réutilisés
                // par Plotly.react() d'une figure à l'autre sans redéclencher
                // les écouteurs si le nombre de traces ne change pas.
                // [Correctif] Ne plus fixer g.style.opacity ici : la puce de
                // légende est déjà atténuée nativement côté Python
                // (marker.opacity du trace Scattermapbox invisible, cf.
                // _add_legend_traces) pour les catégories sans zone — la
                // fixer aussi ici doublait l'atténuation (0.35 * 0.35), la
                // rendant presque invisible.
                g._categoriePresente = presente;
                g.style.cursor = presente ? 'pointer' : 'default';
                g.title = presente ? '' : 'Aucune zone dans cette catégorie pour la sélection actuelle';

                if (g._legendHoverBound) { return; }
                g._legendHoverBound = true;
                g.addEventListener('mouseenter', function() {
                    if (!g._categoriePresente) { return; }
                    surbrillerCategorie(zi);
                });
                g.addEventListener('mouseleave', function() { surbrillerCategorie(null); });
            });

            console.log('[legend-hover] survol activé sur', traceGroups.length, 'entrées de légende (', categoriesPresentes.size, 'avec données).');
        }

        tenterBinding(10);
        return window.dash_clientside.no_update;
    }
    """,
    Output("carte-legend-filter-dummy", "data"),
    Input("carte-choropleth", "figure"),
    prevent_initial_call=True,
)


# Couleur fixe par type de prestataire (diagramme "Nb de points d'accès par
# type de prestataire") — une teinte par famille, choisies pour rester
# distinctes des couleurs cluster/classe IIFT utilisées ailleurs sur la page
# (CLUSTER_COLORS, CLASSE_IIFT_COLORS) afin d'éviter toute confusion.
TYPE_PRESTATAIRE_COLORS = {
    "brh_agent_non_bancaire": "#B2C9AB",
    "brh_banque": "#E07A5F",
    "brh_maison_de_transfert": "#2F4F4F",
    "brh_atm": "#F2C14E",
    "brh_microfinance": "#6C8EBF",
    "brh_caisse_populaire": "#A78BFA",
}


def build_bar_chart_type_prestataire(df, types_selectionnes=None):
    """
    Diagramme en barres du panneau du haut, visible uniquement quand
    l'indicateur d'offre pilote la carte : nb de points par type de
    prestataire (les 6 familles BRH par défaut), toujours ces mêmes
    catégories quel que soit le niveau géographique choisi — seule la
    sélection géographique/cluster courante (df déjà filtré) fait varier les
    totaux.

    [Ajout] Le filtre "Type prestataire" (multi-choix) restreint désormais
    les barres affichées : liste vide -> les 6 familles habituelles, une
    seule valeur -> une seule barre, plusieurs valeurs -> uniquement les
    barres correspondantes.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Aucune zone ne correspond à cette sélection.", showarrow=False)
        fig.update_layout(height=260, margin=dict(l=15, r=15, t=10, b=10), paper_bgcolor=COLORS["surface"])
        return fig

    colonnes = [c for c in (types_selectionnes or []) if c in TYPE_PRESTATAIRE_LABELS] or list(
        TYPE_PRESTATAIRE_LABELS
    )
    values = pd.DataFrame(
        {
            "type": [TYPE_PRESTATAIRE_LABELS[col] for col in colonnes],
            "value": [df[col].sum() for col in colonnes],
            "colonne": colonnes,
        }
    ).sort_values("value", ascending=True)

    fig = px.bar(
        values,
        x="value",
        y="type",
        orientation="h",
        text="value",
        labels={"value": "Nb de points", "type": ""},
    )
    # [Correctif] Une couleur fixe par type de prestataire (au lieu d'une
    # teinte unique) — associée à la colonne, pas à la position de la barre,
    # pour que chaque type garde toujours la même couleur quel que soit
    # l'ordre de tri ou le sous-ensemble affiché.
    fig.update_traces(marker_color=[TYPE_PRESTATAIRE_COLORS.get(c, COLORS["terracotta_700"]) for c in values["colonne"]])
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=50, t=6, b=30),
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font_family="Inter, sans-serif",
        showlegend=False,
        yaxis={"automargin": True},
        xaxis={"gridcolor": COLORS["border"], "zerolinecolor": COLORS["border"]},
    )
    return fig


def build_bar_chart(df, indicateur, niveau, label_override=None, zone_colors=None):
    """Construit le graphique adjacent, agrégé au niveau administratif choisi.

    label_override : utilisé quand `indicateur` est une colonne calculée à la
    volée (ex. "_prestataire_selection", somme de plusieurs types de
    prestataire choisis) et qui n'a donc pas de libellé propre dans les
    dictionnaires de config — on passe alors directement le libellé à
    afficher (ex. "Agent non bancaire + ATM").

    zone_colors : dict optionnel {nom_zone: couleur_hex} — quand fourni
    (indicateur de demande catégoriel choisi : Cluster K-Means / Classe
    IIFT), chaque barre reprend la couleur de sa zone sur la carte plutôt
    que la couleur unique par défaut.
    """
    level_columns = {
        "pays": (None, "Haïti"),
        "departement": (DEPARTEMENT_COL, "département"),
        "arrondissement": (ARRONDISSEMENT_COL, "arrondissement"),
        "commune": (NOM_COMMUNE_COL, "commune"),
    }
    group_col, level_label = level_columns.get(niveau, (NOM_COMMUNE_COL, "commune"))
    indicator_label = label_override or CATEGORICAL_INDICATORS.get(
        indicateur,
        OFFER_INDICATOR_LABELS.get(
            indicateur,
            DEMAND_INDICATOR_LABELS.get(
                indicateur,
                BRH_SERVICE_INDICATOR_LABELS.get(indicateur, INDICATOR_LABELS.get(indicateur, indicateur)),
            ),
        ),
    )

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Aucune zone ne correspond à cette sélection.", showarrow=False)
        fig.update_layout(height=360, margin=dict(l=15, r=15, t=20, b=20), paper_bgcolor=COLORS["surface"])
        return fig, f"{indicator_label} par {level_label}"

    if indicateur in CATEGORICAL_INDICATORS:
        values = df.groupby(group_col).size().reset_index(name="value") if group_col else pd.DataFrame({"zone": ["Haïti"], "value": [len(df)]})
        if group_col:
            values = values.rename(columns={group_col: "zone"})
        value_label = "Nombre de communes"
    elif group_col:
        aggregation = "sum" if indicateur in SUM_INDICATORS or indicateur == "_prestataire_selection" else "mean"
        values = df.groupby(group_col, as_index=False)[indicateur].agg(aggregation).rename(columns={group_col: "zone", indicateur: "value"})
        value_label = "Total" if aggregation == "sum" else "Moyenne"
    else:
        aggregation = "sum" if indicateur in SUM_INDICATORS or indicateur == "_prestataire_selection" else "mean"
        values = pd.DataFrame({"zone": ["Haïti"], "value": [getattr(df[indicateur], aggregation)()]})
        value_label = "Total" if aggregation == "sum" else "Moyenne"

    values = values.sort_values("value", ascending=True)
    height = max(360, min(26 * len(values) + 110, 2500))
    fig = px.bar(
        values,
        x="value",
        y="zone",
        orientation="h",
        text="value",
        color_discrete_sequence=[COLORS["petrole_700"]],
        labels={"value": value_label, "zone": ""},
    )
    if zone_colors:
        # [Ajout] Chaque barre reprend la couleur de sa zone sur la carte
        # (cluster K-Means / classe IIFT majoritaire) au lieu de la teinte
        # unique par défaut — repli sur petrole_700 pour toute zone absente
        # du mapping (ex. donnée manquante).
        fig.update_traces(marker_color=[zone_colors.get(z, COLORS["petrole_700"]) for z in values["zone"]])
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=60, t=12, b=35),
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font_family="Inter, sans-serif",
        showlegend=False,
        yaxis={"automargin": True},
        xaxis={"gridcolor": COLORS["border"], "zerolinecolor": COLORS["border"]},
    )
    return fig, f"{indicator_label} par {level_label}"
