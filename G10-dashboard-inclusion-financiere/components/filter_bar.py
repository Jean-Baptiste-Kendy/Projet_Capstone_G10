"""
Barre de filtres partagée, façon Tableau/Power BI : niveau géographique en
radio (Pays -> Département -> Arrondissement -> Commune), sélecteurs en
cascade, et bloc Total/Sélectionné toujours visible.

Cette barre est un COMPOSANT DE PRÉSENTATION uniquement : les callbacks qui
réagissent à ces filtres (cascade des options, filtrage de la carte, mise à
jour des KPI) sont définis dans la page qui l'utilise (carte.py), pas ici,
pour éviter les imports circulaires entre pages.

[Correctif] Le radio "Niveau géographique" ne pilotait auparavant aucun
callback (les clics ne faisaient rien). Il pilote maintenant réellement
l'affichage des 3 dropdowns dépendants (visibles/masqués selon le niveau
choisi) et le filtrage effectif de la carte — cf. pages/carte.py.

[Correctif] dcc.Store("selection-store") a été RETIRÉ d'ici et déplacé dans
le layout global de app.py : cette barre est reconstruite à chaque fois que
l'onglet Carte est réaffiché (l'app est single-page à onglets, pas multi-URL),
donc un Store défini ici perdrait son contenu à chaque changement d'onglet.
"""

from dash import html, dcc


FILTER_BAR_ID_PREFIX = "filter-bar"

NIVEAUX_GEO = [
    {"label": " Pays", "value": "pays"},
    {"label": " Département", "value": "departement"},
    {"label": " Arrondissement", "value": "arrondissement"},
    {"label": " Commune", "value": "commune"},
]


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
    departements, arrondissements, communes : listes initiales pour peupler
        les 3 dropdowns en cascade. `arrondissements` et `communes` peuvent
        être passés vides ici : ils sont repeuplés dynamiquement par les
        callbacks de cascade dans carte.py dès qu'un niveau parent est choisi.
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
                        options=NIVEAUX_GEO,
                        value="pays",
                        className="filter-radio",
                        labelClassName="filter-radio-label",
                    ),
                ],
            ),
            # Les 3 dropdowns suivants existent toujours dans le DOM (pour que
            # Dash puisse les cibler en callback), mais leur groupe est
            # affiché/masqué par toggle_niveau_geo() dans carte.py selon le
            # niveau géographique choisi : Département visible dès le niveau
            # "Département", Arrondissement dès "Arrondissement", Commune
            # uniquement au niveau "Commune" — comme un vrai drill-down.
            html.Div(
                id=f"{FILTER_BAR_ID_PREFIX}-departement-group",
                className="filter-group",
                style={"display": "none"},
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
                style={"display": "none"},
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
                style={"display": "none"},
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
