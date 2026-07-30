"""
Barre d'onglets principale de l'application single-page.

Remplace l'ancienne navigation multi-page (URLs séparées) par une barre
d'onglets unique, façon Power BI / Tableau : une seule page HTML, le contenu
change via callback quand on clique un onglet.
"""

from dash import dcc

from data.config import COLORS

TABS = [
    ("accueil", "Accueil"),
    ("presentation", "Présentation"),
    ("carte", "Carte interactive"),
    ("acp-iift", "ACP & IIFT"),
    ("clustering-afcm", "Clustering & AFCM"),
    ("modelisation", "Modélisation"),
    ("fiche-commune", "Fiche commune"),
    ("methodologie", "Méthodologie"),
]

# Onglet inactif : texte gris secondaire sur fond blanc (se fond dans la barre).
TAB_STYLE = {
    "padding": "12px 20px",
    "fontSize": "13px",
    "fontWeight": "500",
    "border": "none",
    "borderBottom": "3px solid transparent",
    "color": COLORS["text_secondary"],
    "background": COLORS["surface"],
}

# Onglet actif : fond teinté bleu-pétrole clair (bien visible sur le blanc de
# la barre, contrairement à l'ancien fond crème quasi identique au fond de
# page), texte gras foncé + soulignement terracotta — 3 signaux cumulés pour
# que l'onglet actif reste repérable en un coup d'œil, y compris une fois
# qu'on est resté un moment sur la page.
TAB_SELECTED_STYLE = {
    "padding": "12px 20px",
    "fontSize": "13px",
    "fontWeight": "700",
    "border": "none",
    "borderBottom": f"3px solid {COLORS['terracotta_500']}",
    "color": COLORS["petrole_900"],
    "background": COLORS["petrole_200"],
}


def build_tabbar(default_value: str = "accueil"):
    return dcc.Tabs(
        id="main-tabs",
        value=default_value,
        className="main-tabbar",
        children=[
            dcc.Tab(label=label, value=val, style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE)
            for val, label in TABS
        ],
    )
