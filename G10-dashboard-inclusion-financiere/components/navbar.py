"""Navbar persistante — présente sur toutes les pages via le layout global de app.py."""

import dash
from dash import html, dcc


def build_navbar():
    """
    Construit la barre de navigation. Utilise dash.page_registry pour lister
    automatiquement les pages enregistrées via dash.register_page(), avec
    l'ordre défini par le champ `order` de chaque page.
    """
    pages = sorted(
        dash.page_registry.values(), key=lambda p: p.get("order", 99)
    )

    nav_links = [
        dcc.Link(
            page["name"],
            href=page["relative_path"],
            className="nav-link",
            id={"type": "nav-link", "path": page["relative_path"]},
        )
        for page in pages
    ]

    return html.Nav(
        className="navbar",
        children=[
            html.Div(
                className="navbar-inner",
                children=[
                    html.Div(
                        className="navbar-brand",
                        children=[
                            html.Span("G10", className="navbar-brand-mark"),
                            html.Span(
                                "Inclusion Financière — Haïti",
                                className="navbar-brand-text",
                            ),
                        ],
                    ),
                    html.Div(className="navbar-links", children=nav_links),
                ],
            )
        ],
    )
