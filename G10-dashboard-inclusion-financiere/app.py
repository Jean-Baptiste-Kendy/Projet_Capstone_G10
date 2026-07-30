"""
Point d'entrée du dashboard — application SINGLE-PAGE avec barre d'onglets.

Architecture : une seule page HTML, une barre d'onglets (components/tabbar.py)
pilote quel module de pages/ est affiché dans la zone de contenu. Chaque
module de pages/ garde sa fonction layout() (et ses éventuels callbacks
@callback définis au niveau module) exactement comme avant — seul le
mécanisme de navigation a changé (plus de routing par URL).

Lancement local : python app.py
Déploiement (Render/Railway/Gunicorn) : le serveur WSGI cible `app.server`
"""

import logging

import dash
from dash import html, dcc, callback, Output, Input

from components.navbar import build_navbar
from components.tabbar import build_tabbar
from components.footer import build_footer
from data.loaders import load_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# ---------------------------------------------------------------------------
# Chargement des données au démarrage (une seule fois pour tout le process)
# ---------------------------------------------------------------------------
logger.info("Chargement des données...")
DATA = load_all()
logger.info("Chargement terminé.")

# ---------------------------------------------------------------------------
# Initialisation de l'app Dash (single-page, PAS de use_pages)
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Analyse territoriale de l'inclusion financière en Haïti",
    update_title=None,
)

server = app.server  # nécessaire pour le déploiement (gunicorn ciblera app:server)

# ---------------------------------------------------------------------------
# Import des modules de pages APRÈS la création de `app` : leurs @callback
# doivent s'enregistrer sur une app déjà instanciée.
# ---------------------------------------------------------------------------
from pages import accueil as page_accueil
from pages import presentation as page_presentation
from pages import carte as page_carte
from pages import acp_iift as page_acp_iift
from pages import clustering_afcm as page_clustering_afcm
from pages import modelisation as page_modelisation
from pages import fiche_commune as page_fiche_commune
from pages import methodologie as page_methodologie

PAGE_MODULES = {
    "accueil": page_accueil,
    "presentation": page_presentation,
    "carte": page_carte,
    "acp-iift": page_acp_iift,
    "clustering-afcm": page_clustering_afcm,
    "modelisation": page_modelisation,
    "fiche-commune": page_fiche_commune,
    "methodologie": page_methodologie,
}

# ---------------------------------------------------------------------------
# Layout global : navbar + barre d'onglets + zone de contenu + footer
#
# [Correctif] "selection-store" est monté ICI (au niveau global), pas dans
# filter_bar.py comme avant : le contenu de "tab-content" est entièrement
# recréé à chaque changement d'onglet (cf. render_active_tab ci-dessous), donc
# un Store défini à l'intérieur d'une page perdrait sa valeur à chaque clic
# sur un onglet. Monté ici, il survit à la navigation et permet une vraie
# synchronisation inter-onglets (ex. cliquer une commune sur la carte, puis
# retrouver cette même commune pré-remplie en allant sur l'onglet Fiche
# commune).
# ---------------------------------------------------------------------------
app.layout = html.Div(
    children=[
        build_navbar(),
        build_tabbar(default_value="accueil"),
        dcc.Store(id="selection-store", data={"commune": None, "cluster": "all"}),
        html.Div(id="tab-content"),
        build_footer(),
    ]
)


@callback(Output("tab-content", "children"), Input("main-tabs", "value"))
def render_active_tab(tab_value):
    module = PAGE_MODULES.get(tab_value)
    if module is None:
        return html.Div(
            className="page-container error-banner",
            children=f"Onglet inconnu : {tab_value}",
        )
    return module.layout()


if __name__ == "__main__":
    # debug=True uniquement en développement local — le désactiver au déploiement
    app.run(debug=True, host="0.0.0.0", port=8050)
