"""Page 6 — Fiche commune : recherche et détail individuel par commune."""

import dash
from dash import html, dcc, callback, Output, Input

from components.kpi_card import build_kpi_row
from data.loaders import load_matrice_globale, DataLoadError
from data.config import NOM_COMMUNE_COL, INDICATOR_LABELS

dash.register_page(__name__, path="/fiche-commune", name="Fiche commune", order=6)


def layout():
    try:
        df = load_matrice_globale()
    except DataLoadError as e:
        return html.Div(
            className="page-container",
            children=[
                html.H1("Fiche commune"),
                html.Div(className="error-banner", children=str(e)),
            ],
        )

    options = [
        {"label": f"{nom} ({dept})", "value": nom}
        for nom, dept in sorted(
            zip(df[NOM_COMMUNE_COL], df["departement"]), key=lambda x: x[0]
        )
    ]

    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="page-header-row",
                children=[
                    html.H1("Fiche commune"),
                    html.Span("Recherchez une commune pour ses indicateurs détaillés", className="page-header-sub"),
                ],
            ),
            dcc.Dropdown(
                id="fiche-commune-search",
                options=options,
                placeholder="Rechercher une commune...",
                style={"maxWidth": "420px", "marginBottom": "24px"},
            ),
            html.Div(id="fiche-commune-detail"),
        ],
    )


@callback(
    Output("fiche-commune-detail", "children"),
    Input("fiche-commune-search", "value"),
)
def update_fiche(commune):
    if not commune:
        return html.Div(
            className="loading-placeholder",
            children="Sélectionnez une commune ci-dessus pour afficher sa fiche détaillée.",
        )

    try:
        df = load_matrice_globale()
    except DataLoadError as e:
        return html.Div(className="error-banner", children=str(e))

    match = df[df[NOM_COMMUNE_COL] == commune]
    if match.empty:
        return html.Div(className="error-banner", children="Commune introuvable dans la matrice.")
    row = match.iloc[0]

    # --- KPIs d'en-tête ---
    population = row.get("population_totale")
    population_fmt = f"{int(population):,}".replace(",", " ") if population == population else "n/d"

    kpis = build_kpi_row(
        [
            {"label": "Département", "value": str(row.get("departement", "n/d"))},
            {"label": "Arrondissement", "value": str(row.get("arrondissement", "n/d"))},
            {"label": "Population totale", "value": population_fmt},
            {
                "label": "Profil de services financiers",
                "value": str(row.get("profil_services_financiers", "n/d")),
                "accent": True,
            },
        ]
    )

    # --- Comparaison au national (sur les indicateurs clés) ---
    moyennes_nationales = df[list(INDICATOR_LABELS.keys())].mean(numeric_only=True)

    table_rows = []
    for col, label in INDICATOR_LABELS.items():
        if col not in row or pd_isna(row[col]):
            continue
        val = row[col]
        moyenne = moyennes_nationales.get(col)
        val_str = f"{val:,.2f}".replace(",", " ") if isinstance(val, float) else str(val)
        if moyenne is not None and moyenne == moyenne:
            delta = val - moyenne
            delta_str = f"{'+' if delta >= 0 else ''}{delta:.2f} vs moyenne nationale ({moyenne:.2f})"
            delta_class = "delta-positive" if delta >= 0 else "delta-negative"
        else:
            delta_str, delta_class = "", ""

        table_rows.append(
            html.Tr(
                [
                    html.Td(label, className="fiche-table-label"),
                    html.Td(val_str, className="fiche-table-value"),
                    html.Td(delta_str, className=f"fiche-table-delta {delta_class}"),
                ]
            )
        )

    table = html.Table(
        className="fiche-table",
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th("Indicateur"),
                        html.Th("Valeur"),
                        html.Th("Comparaison nationale"),
                    ]
                )
            ),
            html.Tbody(table_rows),
        ],
    )

    return html.Div([kpis, table])


def pd_isna(val) -> bool:
    """Petit helper local pour éviter d'importer pandas juste pour isna()."""
    return val is None or val != val  # val != val n'est True que pour les floats NaN
