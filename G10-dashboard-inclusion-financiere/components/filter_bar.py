"""
Barre de filtres partagée, façon Tableau BRH : niveau géographique en radio
(Pays -> Département -> Commune), sélecteurs dépendants, et bloc
Total/Sélectionné toujours visible.

Cette barre est un COMPOSANT DE PRÉSENTATION uniquement : les callbacks qui
réagissent à ces filtres sont définis dans chaque page (carte.py, etc.), pas
ici, pour éviter les imports circulaires entre pages.
"""

from dash import html, dcc


FILTER_BAR_ID_PREFIX = "filter-bar"


def build_filter_bar(departements: list[str] | None = None, cluster_available: bool = False):
    """
    Construit la barre de filtres partagée.

    Parameters
    ----------
    departements : liste des noms de départements pour peupler le dropdown.
    cluster_available : si False (par défaut tant que la Phase 3 — clustering —
        n'est pas branchée), le filtre cluster est désactivé avec une info-bulle
        plutôt que de proposer un filtre qui ne fait rien.
    """
    departements = departements or []

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
            else [{"label": "Disponible en Phase 3", "value": "all"}]
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
                            {"label": " Commune", "value": "commune"},
                        ],
                        value="pays",
                        className="filter-radio",
                        labelClassName="filter-radio-label",
                    ),
                ],
            ),
            html.Div(
                className="filter-group",
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
            # Store partagé : contient la sélection courante (commune cliquée,
            # cluster filtré...) pour synchroniser plusieurs pages/graphiques
            dcc.Store(id="selection-store", data={"commune": None, "cluster": "all"}),
        ],
    )
