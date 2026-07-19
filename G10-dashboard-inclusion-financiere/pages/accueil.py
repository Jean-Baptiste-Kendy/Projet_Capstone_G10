"""Page 0 — Accueil : contexte projet, KPIs nationaux, storytelling (3 insights)."""

import dash
from dash import html, dcc, callback, Output, Input, State

from components.kpi_card import build_kpi_row
from data.loaders import get_table, DataLoadError
from data.config import PROJECT_TITLE, EQUIPE, N_COMMUNES, N_CLUSTERS, COLORS

dash.register_page(__name__, path="/", name="Accueil", order=0)

# Insights construits à partir des vraies sorties des notebooks 3 et 4
# (cf. tests directs des callbacks en Phase 3 — chiffres vérifiés, pas estimés)
SLIDES = [
    {
        "titre": "Un écart de 1 à 5,6 entre les communes les mieux et les moins bien loties",
        "texte": (
            "Le cluster K-Means des communes les plus incluses affiche un IIFT moyen de 75 "
            "(17 communes), contre 13 pour le cluster le plus défavorisé (74 communes) — "
            "soit un écart multiplié par 5,6. L'IIFT lui-même couvre toute l'échelle 0-100."
        ),
    },
    {
        "titre": "L'AFCM révèle une structure cachée après correction Benzécri",
        "texte": (
            "La variance brute expliquée par le premier axe de l'AFCM n'est que de 12,3 %, "
            "un chiffre trompeur typique de l'AFCM. Après correction de Benzécri, elle "
            "atteint 66,3 % — confirmant que le premier axe capture bien une structure "
            "dominante du profil qualitatif des communes."
        ),
    },
    {
        "titre": "La modélisation supervisée valide la cohérence de l'indice IIFT",
        "texte": (
            "Random Forest — le seul des trois modèles à ne pas voir la formule exacte de "
            "l'IIFT — le prédit avec un R² de 0,93 sur l'échantillon de test à partir des "
            "seules variables explicatives d'origine : la structure que capture l'IIFT est "
            "donc bien réelle, pas un artefact de construction. Ridge et Lasso, eux, "
            "atteignent 1,00 — un résultat attendu et non une performance à mettre en avant, "
            "puisque l'IIFT est par construction une combinaison linéaire de ces mêmes "
            "variables : ces deux modèles ne font que retrouver exactement la formule "
            "d'origine, ils ne valident rien de plus que Random Forest ne valide déjà."
        ),
    },
]


def layout():
    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="hero-block",
                children=[
                    html.H1(PROJECT_TITLE, style={"maxWidth": "900px"}),
                    html.P(EQUIPE, style={"color": "var(--text-secondary)"}),
                ],
            ),

            build_kpi_row([
                {
                    "label": "Communes analysées",
                    "value": str(N_COMMUNES),
                    "sublabel": "sur l'ensemble du territoire haïtien",
                },
                {
                    "label": "Typologie identifiée",
                    "value": f"K = {N_CLUSTERS}",
                    "sublabel": "validée par score de silhouette",
                    "accent": True,
                },
                {
                    "label": "Variables mobilisées",
                    "value": "56",
                    "sublabel": "après réduction depuis 57 variables sources",
                },
                {
                    "label": "Sources croisées",
                    "value": "4",
                    "sublabel": "BRH, IHSI, OCHA, BID/World Bank",
                },
            ]),

            html.H3("Principales conclusions", style={"marginTop": "8px"}),
            _build_carousel(),
        ],
    )


def _build_carousel():
    return html.Div(
        className="carousel",
        children=[
            html.Div(
                className="carousel-nav",
                children=[
                    html.Button("‹", id="accueil-slide-prev", className="carousel-btn", n_clicks=0),
                    html.Div(id="accueil-slide-dots", className="carousel-dots"),
                    html.Button("›", id="accueil-slide-next", className="carousel-btn", n_clicks=0),
                ],
            ),
            dcc.Store(id="accueil-slide-index", data=0),
            html.Div(id="accueil-slide-content", className="carousel-content"),
        ],
    )


@callback(
    Output("accueil-slide-index", "data"),
    Input("accueil-slide-prev", "n_clicks"),
    Input("accueil-slide-next", "n_clicks"),
    State("accueil-slide-index", "data"),
    prevent_initial_call=True,
)
def _navigate_slides(n_prev, n_next, current_index):
    triggered = dash.ctx.triggered_id
    if triggered == "accueil-slide-prev":
        return (current_index - 1) % len(SLIDES)
    if triggered == "accueil-slide-next":
        return (current_index + 1) % len(SLIDES)
    return current_index


@callback(
    Output("accueil-slide-content", "children"),
    Output("accueil-slide-dots", "children"),
    Input("accueil-slide-index", "data"),
)
def _render_slide(index):
    index = index or 0
    slide = SLIDES[index]

    content = html.Div(
        className="carousel-card",
        children=[
            html.H4(slide["titre"]),
            html.P(slide["texte"]),
        ],
    )

    dots = [
        html.Span(className="carousel-dot" + (" carousel-dot-active" if i == index else ""))
        for i in range(len(SLIDES))
    ]

    return content, dots
