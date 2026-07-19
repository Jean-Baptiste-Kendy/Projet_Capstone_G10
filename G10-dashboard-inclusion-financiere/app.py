"""
Point d'entrée du dashboard.

Structure :
- Charge toutes les données UNE FOIS au démarrage (data/loaders.load_all)
- Enregistre le layout global (navbar + zone de page + footer)
- dash.page_registry gère automatiquement les 8 pages via register_page()
  dans chaque fichier de pages/

Lancement local : python app.py
Déploiement (Render/Railway/Gunicorn) : le serveur WSGI cible `app.server`
"""

import logging

import dash
from dash import html, dcc

from components.navbar import build_navbar
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
# Initialisation de l'app Dash avec pages multiples
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
    title="Inclusion Financière en Haïti — Dashboard Capstone G10",
    update_title=None,
)

server = app.server  # nécessaire pour le déploiement (gunicorn ciblera app:server)

# ---------------------------------------------------------------------------
# Layout global : navbar persistante + zone de page + footer
# ---------------------------------------------------------------------------
app.layout = html.Div(
    children=[
        build_navbar(),
        # Store partagé entre TOUTES les pages (contrairement à un Store placé
        # dans un composant de page, qui serait détruit à chaque navigation) :
        # sert à synchroniser la commune sélectionnée sur la Carte avec la
        # Fiche commune (cf. components/filter_bar.py et pages/carte.py).
        dcc.Store(id="selection-store", storage_type="session", data={"commune": None}),
        html.Main(dash.page_container),
        build_footer(),
    ]
)


if __name__ == "__main__":
    # debug=True uniquement en développement local — le désactiver au déploiement
    app.run(debug=True, host="0.0.0.0", port=8050)
