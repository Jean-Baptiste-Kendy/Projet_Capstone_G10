"""Footer persistant — présent sur toutes les pages, liens vers les livrables du projet."""

from dash import html

from data.config import EQUIPE, SUPERVISEUR, COHORTE, GITHUB_USER, GITHUB_REPO


def build_footer():
    github_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"

    return html.Footer(
        className="footer",
        children=[
            html.Div(
                className="footer-inner",
                children=[
                    html.Div(
                        className="footer-col",
                        children=[
                            html.P(COHORTE, className="footer-cohorte"),
                            html.P(EQUIPE, className="footer-equipe"),
                            html.P(
                                f"Supervision : {SUPERVISEUR}",
                                className="footer-superviseur",
                            ),
                        ],
                    ),
                    html.Div(
                        className="footer-col footer-col-links",
                        children=[
                            html.A(
                                "Dépôt GitHub",
                                href=github_url,
                                target="_blank",
                                className="footer-link",
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
