"""
Page 1 — Présentation : vidéo de la soutenance orale.

Stratégie de robustesse (cf. plan directeur) :
- Source principale : embed YouTube non-listé (léger, pas de poids sur le repo)
- Fallback : fichier local dans assets/ si <100 Mo, pour fonctionner hors-ligne
  le jour de la soutenance en cas de wifi défaillant.

⚠️ À COMPLÉTER : remplacer YOUTUBE_VIDEO_ID par l'ID réel une fois la vidéo
   mise en ligne, et déposer presentation.mp4 dans assets/ si vous gardez le fallback local.
"""

import dash
from dash import html

from data.config import DATE_SOUTENANCE, GITHUB_USER, GITHUB_REPO


YOUTUBE_VIDEO_ID = ""  # ⚠️ à renseigner : ID de la vidéo YouTube non-listée
LOCAL_VIDEO_PATH = "/assets/presentation.mp4"  # fallback local


def layout():
    video_block = _build_video_block()

    return html.Div(
        className="page-container",
        children=[
            html.H1("Présentation de la soutenance"),
            html.P(
                f"Soutenance orale du projet — {DATE_SOUTENANCE}.",
                style={"color": "var(--text-secondary)"},
            ),
            video_block,
            html.Div(
                style={"marginTop": "24px", "display": "flex", "gap": "16px"},
                children=[
                    html.A(
                        "Voir le dépôt GitHub complet",
                        href=f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}",
                        target="_blank",
                        className="footer-link",
                        style={"color": "var(--petrole-700)", "fontWeight": "600"},
                    ),
                    # TODO : ajouter le lien vers le rapport PDF final une fois déposé
                ],
            ),
        ],
    )


def _build_video_block():
    if YOUTUBE_VIDEO_ID:
        return html.Div(
            style={"maxWidth": "900px"},
            children=[
                html.Iframe(
                    src=f"https://www.youtube.com/embed/{YOUTUBE_VIDEO_ID}",
                    style={
                        "width": "100%",
                        "height": "500px",
                        "border": "none",
                        "borderRadius": "8px",
                    },
                ),
            ],
        )

    # Fallback : pas d'ID YouTube renseigné -> tente la vidéo locale
    return html.Div(
        style={"maxWidth": "900px"},
        children=[
            html.Div(
                className="error-banner",
                children=(
                    "Aucune vidéo YouTube configurée pour l'instant "
                    "(YOUTUBE_VIDEO_ID vide dans pages/presentation.py). "
                    "Tentative d'affichage du fichier local de secours."
                ),
            ),
            html.Video(
                src=LOCAL_VIDEO_PATH,
                controls=True,
                style={"width": "100%", "borderRadius": "8px"},
            ),
        ],
    )
