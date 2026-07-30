"""
Barre de filtres partagée, façon Tableau/Power BI : niveau géographique en
radio (Pays -> Département -> Arrondissement -> Commune), sélecteurs en
cascade, et blocs KPI toujours visibles.

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

[Correctif] Toutes les options "toutes/tous les ..." (départements,
arrondissements, communes, clusters) sont renommées "(Tout)" — un seul mot
court, pour ne pas prendre trop de place dans une barre déjà dense en 5
colonnes.

[Correctif] Barre réorganisée en 5 COLONNES :
(1) indicateur d'offre + de demande + type de prestataire, empilés
(2) niveau géographique (radio, inchangé)
(3) département + arrondissement + commune, empilés (3 lignes)
(4) cluster K-Means + KPI Total communes / Sélectionné
(5) KPI Total points (type de prestataire) / Sélectionné
"""

from dash import html, dcc

from data.config import CLUSTER_LABELS_COURT


FILTER_BAR_ID_PREFIX = "filter-bar"

NIVEAUX_GEO = [
    {"label": " Pays", "value": "pays"},
    {"label": " Département", "value": "departement"},
    {"label": " Arrondissement", "value": "arrondissement"},
    {"label": " Commune", "value": "commune"},
]

TOUT_LABEL = "(Tout)"

# [Ajout] Libellés français du sélecteur multi-choix natif de Dash (badge de
# comptage "N sélectionnés", boutons "Tout sélectionner"/"Tout désélectionner"
# dans le menu déroulant, message de recherche vide) — partagés par tous les
# filtres multi-choix (cluster, département, arrondissement, commune, type
# prestataire) pour rester cohérents dans toute la barre de filtres.
MULTI_SELECT_LABELS = {
    "select_all": "Tout sélectionner",
    "deselect_all": "Tout désélectionner",
    "selected_count": "{num_selected} sélectionnés",
    "clear_selection": "Effacer",
    "no_options_found": "Aucune option trouvée",
    "search": "Rechercher...",
}


def _kpi_block(label, value_id, initial_value, accent=False):
    classes = "filter-kpi-block filter-kpi-block-accent" if accent else "filter-kpi-block"
    return html.Div(
        className=classes,
        children=[
            html.Span(label, className="filter-kpi-label"),
            html.Span(initial_value, id=value_id, className="filter-kpi-value"),
        ],
    )


def build_filter_bar(
    departements: list[str] | None = None,
    arrondissements: list[str] | None = None,
    communes: list[str] | None = None,
    cluster_available: bool = False,
    offre_dropdown=None,
    demande_dropdown=None,
    type_prestataire_dropdown=None,
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
    offre_dropdown, demande_dropdown, type_prestataire_dropdown : composants
        dcc.Dropdown déjà construits par la page appelante (leurs options
        viennent d'indicateurs propres à carte.py) — ce composant générique
        ne les importe pas lui-même, il se contente de les placer dans la
        1ʳᵉ colonne.
    """
    departements = departements or []
    arrondissements = arrondissements or []
    communes = communes or []

    # [Correctif] Les libellés de clusters étaient recopiés en dur ici, avec
    # leur propre terminologie — en pratique, désynchronisés dès que
    # CLUSTER_LABELS a changé dans config.py (c'est exactement ce qui vient
    # de se produire). On lit maintenant CLUSTER_LABELS_COURT, source unique
    # de vérité pour la terminologie des clusters, dans l'ordre 0 -> 2 -> 1
    # (sévérité croissante, cohérent avec les graphiques des autres pages).
    #
    # [Ajout] "(Tout)" par défaut = les 3 clusters sélectionnés explicitement
    # (plutôt qu'une case vide qui reposait uniquement sur le placeholder) :
    # cohérent avec le badge "N sélectionnés" et le bouton "Tout sélectionner"
    # du menu, et le filtrage par la carte donne le même résultat dans les
    # deux cas (aucun cluster exclu).
    cluster_ids = ["0", "2", "1"] if cluster_available else []
    cluster_dropdown = dcc.Dropdown(
        id=f"{FILTER_BAR_ID_PREFIX}-cluster",
        options=[{"label": CLUSTER_LABELS_COURT[cid], "value": int(cid)} for cid in cluster_ids],
        value=[int(cid) for cid in cluster_ids],
        multi=True,
        placeholder=TOUT_LABEL if cluster_available else "Indisponible",
        clearable=False,
        disabled=not cluster_available,
        labels=MULTI_SELECT_LABELS,
        style={"maxWidth": "230px"},
    )

    colonnes = []

    # --- Colonne 1 : indicateurs (offre, demande, type de prestataire) -----
    indicateur_children = []
    if offre_dropdown is not None:
        indicateur_children.append(
            html.Div(
                className="filter-group",
                children=[html.Label("Indicateur d'offre", className="filter-label"), offre_dropdown],
            )
        )
    if demande_dropdown is not None:
        indicateur_children.append(
            html.Div(
                className="filter-group",
                children=[html.Label("Indicateur de demande", className="filter-label"), demande_dropdown],
            )
        )
    if type_prestataire_dropdown is not None:
        indicateur_children.append(
            html.Div(
                className="filter-group",
                children=[html.Label("Type prestataire", className="filter-label"), type_prestataire_dropdown],
            )
        )
    if indicateur_children:
        colonnes.append(html.Div(className="filter-column", children=indicateur_children))

    # --- Colonne 2 : niveau géographique (inchangé) ------------------------
    colonnes.append(
        html.Div(
            className="filter-column",
            children=[
                html.Div(
                    className="filter-group",
                    children=[
                        html.Label("Niveau géographique", className="filter-label"),
                        dcc.RadioItems(
                            id=f"{FILTER_BAR_ID_PREFIX}-niveau-geo",
                            options=NIVEAUX_GEO,
                            value="commune",
                            className="filter-radio",
                            labelClassName="filter-radio-label",
                        ),
                    ],
                ),
            ],
        )
    )

    # --- Colonne 3 : département + arrondissement + commune (3 lignes) ----
    # Les 3 dropdowns existent toujours dans le DOM (pour que Dash puisse les
    # cibler en callback), mais leur groupe est affiché/masqué par
    # toggle_niveau_geo() dans carte.py selon le niveau géographique choisi :
    # Département visible dès le niveau "Département", Arrondissement dès
    # "Arrondissement", Commune uniquement au niveau "Commune" — comme un
    # vrai drill-down. Les regrouper tous les 3 dans une même colonne ne
    # change rien à cette logique : les IDs ciblés par le callback sont les
    # mêmes, seule l'imbrication visuelle change.
    colonnes.append(
        html.Div(
            className="filter-column",
            children=[
                html.Div(
                    id=f"{FILTER_BAR_ID_PREFIX}-departement-group",
                    className="filter-group",
                    # [Correctif] Visible dès le chargement : le niveau géo
                    # par défaut est désormais "commune", qui affiche les 3
                    # dropdowns (cf. toggle_niveau_geo dans carte.py) — ce
                    # callback a prevent_initial_call=True et ne s'exécute
                    # donc pas au premier rendu, d'où ce style initial cohérent.
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Label("Département", className="filter-label"),
                        dcc.Dropdown(
                            id=f"{FILTER_BAR_ID_PREFIX}-departement",
                            options=[{"label": d, "value": d} for d in departements],
                            value=list(departements),
                            placeholder=TOUT_LABEL,
                            multi=True,
                            clearable=False,
                            labels=MULTI_SELECT_LABELS,
                            style={"maxWidth": "230px"},
                        ),
                    ],
                ),
                html.Div(
                    id=f"{FILTER_BAR_ID_PREFIX}-arrondissement-group",
                    className="filter-group",
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Label("Arrondissement", className="filter-label"),
                        dcc.Dropdown(
                            id=f"{FILTER_BAR_ID_PREFIX}-arrondissement",
                            options=[{"label": a, "value": a} for a in arrondissements],
                            value=list(arrondissements),
                            placeholder=TOUT_LABEL,
                            multi=True,
                            clearable=False,
                            labels=MULTI_SELECT_LABELS,
                            style={"maxWidth": "230px"},
                        ),
                    ],
                ),
                html.Div(
                    id=f"{FILTER_BAR_ID_PREFIX}-commune-group",
                    className="filter-group",
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Label("Commune", className="filter-label"),
                        dcc.Dropdown(
                            id=f"{FILTER_BAR_ID_PREFIX}-commune",
                            options=[{"label": c, "value": c} for c in communes],
                            value=list(communes),
                            placeholder=TOUT_LABEL,
                            multi=True,
                            clearable=False,
                            labels=MULTI_SELECT_LABELS,
                            style={"maxWidth": "230px"},
                        ),
                    ],
                ),
            ],
        )
    )

    # --- Colonne 4 : Cluster K-Means + KPI Total communes / Sélectionné ----
    colonnes.append(
        html.Div(
            className="filter-column",
            children=[
                html.Div(
                    className="filter-group",
                    children=[html.Label("Cluster K-Means", className="filter-label"), cluster_dropdown],
                ),
                html.Div(
                    className="filter-group filter-group-kpi",
                    children=[
                        _kpi_block("Total communes", f"{FILTER_BAR_ID_PREFIX}-total", "140"),
                        _kpi_block("Sélectionné", f"{FILTER_BAR_ID_PREFIX}-selectionne", "140", accent=True),
                    ],
                ),
            ],
        )
    )

    # --- Colonne 5 : KPI Total points (type prestataire) / Sélectionné ----
    colonnes.append(
        html.Div(
            className="filter-column",
            children=[
                html.Div(
                    className="filter-group filter-group-kpi-stack",
                    children=[
                        _kpi_block("Total points / type", f"{FILTER_BAR_ID_PREFIX}-total-points", "—"),
                        _kpi_block(
                            "Sélectionné", f"{FILTER_BAR_ID_PREFIX}-points-selectionne", "—", accent=True
                        ),
                    ],
                ),
            ],
        )
    )

    return html.Div(className="filter-bar", children=colonnes)
