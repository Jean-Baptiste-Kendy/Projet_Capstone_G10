"""Page 6 — Fiche commune : recherche et détail individuel par commune."""

import pandas as pd

import dash
from dash import html, dcc, callback, Output, Input, no_update

from components.kpi_card import build_kpi_row
from data.loaders import load_matrice_globale, get_table, DataLoadError
from data.config import (
    ID_COMMUNE_COL,
    NOM_COMMUNE_COL,
    INDICATOR_LABELS,
    INVERSE_INDICATORS,
    CLUSTER_LABELS,
    CLUSTER_LABELS_COURT,
)



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
            zip(df[NOM_COMMUNE_COL].dropna(), df.loc[df[NOM_COMMUNE_COL].notna(), "departement"]),
            key=lambda x: str(x[0]),
        )
    ]

    try:
        cluster_table = build_cluster_accordion(df)
    except DataLoadError as e:
        cluster_table = html.Div(
            className="error-banner",
            children=f"La liste des clusters est indisponible : {e}",
        )

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
            html.Div(
                className="fiche-clusters-section",
                children=[
                    html.H2("Communes par cluster", className="fiche-clusters-title"),
                    html.P(
                        "Ouvrez un cluster pour consulter les communes qui le composent.",
                        className="fiche-clusters-caption",
                    ),
                    cluster_table,
                ],
            ),
        ],
    )


def build_cluster_accordion(communes_df):
    """Construit une liste déroulante, séparée pour chacun des trois clusters."""
    clusters = get_table("clustering_resultats")[[ID_COMMUNE_COL, "cluster_kmeans"]].copy()
    clusters["cluster_kmeans"] = clusters["cluster_kmeans"].astype("Int64").astype(str)
    columns = [ID_COMMUNE_COL, NOM_COMMUNE_COL, "departement", "arrondissement"]
    data = clusters.merge(communes_df[columns], on=ID_COMMUNE_COL, how="left")

    sections = []
    # Ordre analytique : faible, intermédiaire, élevé.
    for cluster_id in ("0", "2", "1"):
        subset = data[data["cluster_kmeans"] == cluster_id].sort_values(NOM_COMMUNE_COL)
        rows = [
            html.Tr(
                [
                    html.Td(row[NOM_COMMUNE_COL]),
                    html.Td(row["departement"]),
                    html.Td(row["arrondissement"]),
                ]
            )
            for _, row in subset.iterrows()
        ]
        table = html.Table(
            className="fiche-table fiche-cluster-table",
            children=[
                html.Thead(html.Tr([html.Th("Commune"), html.Th("Département"), html.Th("Arrondissement")])),
                html.Tbody(rows),
            ],
        )
        sections.append(
            html.Details(
                className="cluster-details",
                children=[
                    html.Summary(
                        [
                            html.Span(CLUSTER_LABELS_COURT[cluster_id], className="cluster-summary-id"),
                            html.Span(CLUSTER_LABELS[cluster_id], className="cluster-summary-label"),
                            html.Span(f"{len(subset)} communes", className="cluster-summary-count"),
                        ]
                    ),
                    html.Div(table, className="cluster-table-wrap"),
                ],
            )
        )
    return html.Div(sections, className="cluster-accordion")


@callback(
    Output("fiche-commune-search", "value"),
    Input("selection-store", "data"),
)
def preremplir_depuis_selection(selection):
    """Pré-remplit la recherche si une commune a été cliquée sur la carte
    (selection-store, monté globalement dans app.py — survit au changement
    d'onglet). Ne fait rien si le store est vide, pour ne pas écraser une
    recherche déjà en cours si l'utilisateur revient sur cet onglet."""
    if not selection or not selection.get("commune"):
        return no_update
    return selection["commune"]


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
    population_fmt = f"{int(population):,}".replace(",", " ") if pd.notna(population) else "n/d"

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
    indicateurs_disponibles = [col for col in INDICATOR_LABELS if col in df.columns]
    moyennes_nationales = df[indicateurs_disponibles].apply(pd.to_numeric, errors="coerce").mean()

    table_rows = []
    for col, label in INDICATOR_LABELS.items():
        if col not in row or pd.isna(row[col]):
            continue
        val = pd.to_numeric(row[col], errors="coerce")
        if pd.isna(val):
            continue
        moyenne = moyennes_nationales.get(col)
        val_str = f"{val:,.2f}".replace(",", " ")
        if moyenne is not None and pd.notna(moyenne):
            delta = val - moyenne
            delta_str = f"{'+' if delta >= 0 else ''}{delta:.2f} vs moyenne nationale ({moyenne:.2f})"
            # Pour les indicateurs "inverses" (ex. pauvreté, privation spatiale),
            # être au-dessus de la moyenne nationale est défavorable — la
            # couleur doit donc être inversée par rapport aux indicateurs
            # d'inclusion classiques (où au-dessus de la moyenne est favorable).
            est_favorable = (delta < 0) if col in INVERSE_INDICATORS else (delta >= 0)
            delta_class = "delta-positive" if est_favorable else "delta-negative"
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
