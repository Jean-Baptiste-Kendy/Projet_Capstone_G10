"""Carte KPI réutilisable — affichage d'un indicateur chiffré avec label et contexte optionnel."""

from dash import html


def build_kpi_card(label: str, value: str, sublabel: str = "", accent: bool = False):
    """
    Construit une carte KPI unique.

    Parameters
    ----------
    label : intitulé court de l'indicateur (ex. "Communes analysées")
    value : valeur affichée en grand (ex. "140")
    sublabel : texte de contexte optionnel sous la valeur (ex. "sur tout le territoire")
    accent : si True, utilise la couleur terracotta au lieu du bleu-pétrole
    """
    classes = "kpi-card kpi-card-accent" if accent else "kpi-card"
    children = [
        html.Div(value, className="kpi-card-value"),
        html.Div(label, className="kpi-card-label"),
    ]
    if sublabel:
        children.append(html.Div(sublabel, className="kpi-card-sublabel"))

    return html.Div(className=classes, children=children)


def build_kpi_row(kpis: list[dict]):
    """
    Construit une rangée de plusieurs KPI cards.

    Parameters
    ----------
    kpis : liste de dicts avec clés 'label', 'value', et optionnellement
        'sublabel' et 'accent'.
    """
    return html.Div(
        className="kpi-row",
        children=[build_kpi_card(**kpi) for kpi in kpis],
    )
