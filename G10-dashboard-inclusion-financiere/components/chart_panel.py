"""Panneau de visualisation réutilisable — en-tête court + graphique, style Power BI/Tableau."""

from dash import html, dcc


def build_chart_panel(title: str, figure_or_component, span: str = "half", caption: str = ""):
    """
    Encapsule un graphique dans un panneau avec en-tête compact.

    Parameters
    ----------
    title : titre court du panneau (pas de phrase explicative longue).
    figure_or_component : soit une figure Plotly (sera enveloppée dans dcc.Graph),
        soit un composant Dash déjà construit (ex. un html.Table).
    span : "half" (2 panneaux par ligne) ou "full" (pleine largeur).
    caption : légende optionnelle d'une ligne max, affichée en petit sous le titre.
    """
    is_figure = hasattr(figure_or_component, "to_dict")
    content = (
        dcc.Graph(figure=figure_or_component, config={"displayModeBar": False})
        if is_figure
        else figure_or_component
    )

    classes = "chart-panel chart-panel-full" if span == "full" else "chart-panel"

    header_children = [html.Span(title, className="chart-panel-title")]
    if caption:
        header_children.append(html.Span(caption, className="chart-panel-caption"))

    return html.Div(
        className=classes,
        children=[
            html.Div(className="chart-panel-header", children=header_children),
            html.Div(className="chart-panel-body", children=content),
        ],
    )


def build_grid(panels: list):
    """Assemble une liste de panneaux dans une grille responsive."""
    return html.Div(className="dash-grid", children=panels)
