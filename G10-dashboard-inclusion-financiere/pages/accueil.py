"""Page 0 — Accueil : enjeu, résultats, priorités d'action et crédibilité."""

from dash import html

from components.kpi_card import build_kpi_row
from data.config import PROJECT_TITLE, EQUIPE, N_COMMUNES, N_CLUSTERS


RESULTATS = [
    (
        "Une fracture territoriale nette",
        "Les communes du profil le plus inclus atteignent un IIFT moyen de 75 (17 communes), contre 13 pour le profil le plus exposé (74 communes). L'écart de 1 à 5,6 montre que les besoins ne peuvent pas être traités avec une politique uniforme.",
    ),
    (
        "Trois profils, donc trois réponses",
        "La segmentation K-Means distingue des territoires à inclusion faible, intermédiaire et élevée. Elle transforme une carte de disparités en une grille de priorisation opérationnelle.",
    ),
    (
        "Un indice interprétable et cohérent",
        "L'ACP, l'AFCM et la modélisation convergent vers une même structure des profils communaux. La modélisation mesure une cohérence interne de l'IIFT — elle ne remplace pas une validation externe.",
    ),
]

PRIORITES = [
    (
        "Priorité 1 — Réduire l'exclusion",
        "Communes à IIFT faible : concentrer l'extension des points de service, l'interopérabilité de la finance mobile, l'information financière et l'accompagnement des usagers.",
    ),
    (
        "Priorité 2 — Convertir le potentiel",
        "Communes intermédiaires : transformer l'accès existant en usage actif, notamment par l'épargne, le paiement numérique et des produits adaptés aux ménages et aux petites activités.",
    ),
    (
        "Priorité 3 — Consolider et diffuser",
        "Communes à IIFT élevé : consolider les acquis, tester des innovations et identifier les pratiques reproductibles dans les territoires moins inclus.",
    ),
]


def layout():
    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="page-header-row",
                children=[
                    html.H1(PROJECT_TITLE, style={"maxWidth": "700px", "fontSize": "18px"}),
                ],
            ),
            html.P(EQUIPE, className="page-header-sub", style={"marginBottom": "16px"}),

            html.Div(
                className="impact-hero",
                children=[
                    html.Span("POURQUOI CE TABLEAU COMPTE", className="impact-eyebrow"),
                    html.H2("Passer d'un constat national à des décisions territoriales ciblées"),
                    html.P(
                        "Ce tableau identifie les disparités d'accès aux services financiers entre les 140 communes d'Haïti, "
                        "afin d'aider les institutions, les décideurs et les partenaires de développement à cibler les territoires prioritaires "
                        "et à adapter leurs interventions à chaque profil communal."
                    ),
                    html.P(
                        "Question directrice : quelles communes cumulent les obstacles à l'inclusion financière, et quelles actions doivent être priorisées pour réduire ces inégalités ?",
                        className="impact-question",
                    ),
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

            html.H3("Ce que l'analyse démontre", className="section-title"),
            html.Div(
                className="impact-grid",
                children=[
                    html.Article(className="impact-card", children=[html.H4(titre), html.P(texte)])
                    for titre, texte in RESULTATS
                ],
            ),

            html.H3("Comment les résultats orientent l'action", className="section-title"),
            html.Div(
                className="impact-grid",
                children=[
                    html.Article(className="impact-card impact-card-action", children=[html.H4(titre), html.P(texte)])
                    for titre, texte in PRIORITES
                ],
            ),

            html.Div(
                className="credibility-note",
                children=[
                    html.H3("Pourquoi notre solution est crédible"),
                    html.Ul(children=[
                        html.Li("Couverture exhaustive des 140 communes et croisement de sources institutionnelles : BRH, IHSI, OCHA et Banque mondiale / BID."),
                        html.Li("Méthodes complémentaires : ACP pour construire l'IIFT, K-Means pour segmenter, AFCM pour interpréter les profils et modélisation pour vérifier la cohérence interne."),
                        html.Li("Résultats transparents et auditables : sources, choix méthodologiques et limites sont documentés dans l'onglet Méthodologie."),
                    ]),
                    html.P("Les indicateurs issus de collecte manuelle ou de proxys sont explicitement signalés : le tableau constitue un outil d'aide à la décision, à compléter par des données institutionnelles actualisées.", className="credibility-caveat"),
                ],
            ),
        ],
    )
