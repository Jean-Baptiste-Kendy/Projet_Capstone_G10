"""
Barre de filtres partagée, façon Tableau BRH : niveau géographique en radio
(Pays -> Département -> Arrondissement -> Commune), sélecteurs dépendants
(cascade), et bloc Total/Sélectionné toujours visible.

Cette barre est un COMPOSANT DE PRÉSENTATION uniquement : les callbacks qui
réagissent à ces filtres sont définis dans chaque page (carte.py, etc.), pas
ici, pour éviter les imports circulaires entre pages.

[Correctif] Le radio "Niveau géographique" et le Store de sélection partagée
étaient présents dans le HTML mais n'étaient écoutés par AUCUN callback (des
contrôles visibles qui ne faisaient rien). Les 3 dropdowns dépendants (dept/
arrondissement/commune) sont maintenant réellement pilotés par ce radio, en
cascade (cf. les callbacks de pages/carte.py) ; le Store partagé a été déplacé
dans app.py pour persister entre les pages (voir pages/fiche_commune.py).
"""

from dash import html, dcc


FILTER_BAR_ID_PREFIX = "filter-bar"

_GROUP_VISIBLE_STYLE = {"display": "flex", "flexDirection": "column", "gap": "4px"}
_GROUP_HIDDEN_STYLE = {"display": "none"}


def build_filter_bar(
    departements: list[str] | None = None,
    arrondissements: list[str] | None = None,
    communes: list[str] | None = None,
    cluster_available: bool = False,
):
    """
    Construit la barre de filtres partagée.

    Parameters
    ----------
    departements : liste des noms de départements pour peupler le dropdown
        (liste nationale complète ; le dropdown Arrondissement, lui, est
        repeuplé dynamiquement selon le département choisi — cf. carte.py).
    arrondissements : liste nationale des arrondissements (état initial, avant
        toute sélection de département).
    communes : liste nationale des communes (état initial, avant toute
        sélection de département/arrondissement).
    cluster_available : si False, le filtre cluster est désactivé avec une
        info-bulle plutôt que de proposer un filtre qui ne fait rien.
    """
    departements = departements or []
    arrondissements = arrondissements or []
    communes = communes or []

    cluster_dropdown = dcc.Dropdown(
        id=f"{FILTER_BAR_ID_PREFIX}-cluster",
        options=(
            [
                {"label": "Tous les clusters", "value": "all"},
                {"label": "Cluster 0", "value": 0},
                {"label": "Cluster 1", "value": 1},
                {"label": "Cluster 2", "value": 2},
            ]
            if cluster_available
            else [{"label": "Indisponible", "value": "all"}]
        ),
        value="all",
        clearable=False,
        disabled=not cluster_available,
    )

    return html.Div(
        className="filter-bar",
        children=[
            html.Div(
                className="filter-group",
                children=[
                    html.Label("Niveau géographique", className="filter-label"),
                    dcc.RadioItems(
                        id=f"{FILTER_BAR_ID_PREFIX}-niveau-geo",
                        options=[
                            {"label": " Pays", "value": "pays"},
                            {"label": " Département", "value": "departement"},
                            {"label": " Arrondissement", "value": "arrondissement"},
                            {"label": " Commune", "value": "commune"},
                        ],
                        value="pays",
                        className="filter-radio",
                        labelClassName="filter-radio-label",
                    ),
                ],
            ),
            # Les 3 groupes suivants démarrent masqués (niveau par défaut =
            # "pays") ; leur style et leurs options sont pilotés par les
            # callbacks de pages/carte.py en fonction du niveau choisi.
            html.Div(
                id=f"{FILTER_BAR_ID_PREFIX}-departement-group",
                className="filter-group",
                style=_GROUP_HIDDEN_STYLE,
                children=[
                    html.Label("Département", className="filter-label"),
                    dcc.Dropdown(
                        id=f"{FILTER_BAR_ID_PREFIX}-departement",
                        options=[{"label": d, "value": d} for d in departements],
                        placeholder="Tous",
                        clearable=True,
                    ),
                ],
            ),
            html.Div(
                id=f"{FILTER_BAR_ID_PREFIX}-arrondissement-group",
                className="filter-group",
                style=_GROUP_HIDDEN_STYLE,
                children=[
                    html.Label("Arrondissement", className="filter-label"),
                    dcc.Dropdown(
                        id=f"{FILTER_BAR_ID_PREFIX}-arrondissement",
                        options=[{"label": a, "value": a} for a in arrondissements],
                        placeholder="Tous",
                        clearable=True,
                    ),
                ],
            ),
            html.Div(
                id=f"{FILTER_BAR_ID_PREFIX}-commune-group",
                className="filter-group",
                style=_GROUP_HIDDEN_STYLE,
                children=[
                    html.Label("Commune", className="filter-label"),
                    dcc.Dropdown(
                        id=f"{FILTER_BAR_ID_PREFIX}-commune",
                        options=[{"label": c, "value": c} for c in communes],
                        placeholder="Toutes",
                        clearable=True,
                    ),
                ],
            ),
            html.Div(
                className="filter-group",
                children=[
                    html.Label("Cluster IIFT", className="filter-label"),
                    cluster_dropdown,
                ],
            ),
            html.Div(
                className="filter-group filter-group-kpi",
                children=[
                    html.Div(
                        className="filter-kpi-block",
                        children=[
                            html.Span("Total communes", className="filter-kpi-label"),
                            html.Span(
                                id=f"{FILTER_BAR_ID_PREFIX}-total",
                                className="filter-kpi-value",
                                children="140",
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-kpi-block filter-kpi-block-accent",
                        children=[
                            html.Span("Sélectionné", className="filter-kpi-label"),
                            html.Span(
                                id=f"{FILTER_BAR_ID_PREFIX}-selectionne",
                                className="filter-kpi-value",
                                children="140",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
