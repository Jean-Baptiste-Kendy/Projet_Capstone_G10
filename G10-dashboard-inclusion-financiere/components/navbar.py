"""Navbar de marque — la navigation elle-même est gérée par components/tabbar.py."""

from dash import html


def build_navbar():
    """Bandeau de marque en haut de l'application single-page (pas de liens)."""
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
                                "Analyse territoriale de l'inclusion financière en Haïti",
                                className="navbar-brand-text",
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
