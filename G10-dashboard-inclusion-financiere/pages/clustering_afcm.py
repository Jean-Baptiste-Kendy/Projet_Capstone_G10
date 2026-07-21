"""Page 4 — Clustering & AFCM : layout en grille, pas un rapport linéaire."""

import dash
from dash import html
import plotly.express as px
import plotly.graph_objects as go

from components.kpi_card import build_kpi_row
from components.chart_panel import build_chart_panel, build_grid
from data.loaders import get_table, DataLoadError
from data.config import COLORS, CLUSTER_COLORS, CLUSTER_LABELS


PANEL_HEIGHT = 280


def layout():
    try:
        choix_k = get_table("choix_k_kmeans")
        afcm_vp = get_table("afcm_valeurs_propres")
        profil_quanti = get_table("profil_quantitatif_clusters")
        profil_quali = get_table("profil_qualitatif_clusters")
        representatives = get_table("communes_representatives_par_cluster")
        clusters = get_table("clustering_resultats")
        tableau_croise = get_table("tableau_croise_kmeans_quartiles")
        synthese = get_table("synthese_kmeans_vs_quartiles")
    except DataLoadError as e:
        return html.Div(
            className="page-container",
            children=[html.H1("Clustering & AFCM"), html.Div(className="error-banner", children=str(e))],
        )

    silhouette_k3 = choix_k.loc[choix_k["k"] == 3, "silhouette"].iloc[0]
    tailles = clusters["cluster_kmeans"].value_counts().sort_index()

    kpis = build_kpi_row([
        {"label": "K retenu", "value": "3", "accent": True},
        {"label": "Silhouette (K=3)", "value": f"{silhouette_k3:.3f}"},
        {"label": "Répartition clusters", "value": " / ".join(str(v) for v in tailles.values), "sublabel": "communes (0,1,2)"},
        {"label": "Variance Axe1 AFCM (Benzécri)", "value": f"{afcm_vp.iloc[0]['pct_of_variance_benzecri']:.1f}%"},
    ])

    # --- Silhouette vs K ---
    fig_k = go.Figure()
    fig_k.add_scatter(x=choix_k["k"], y=choix_k["silhouette"], mode="lines+markers", name="Silhouette",
                       line=dict(color=COLORS["petrole_700"], width=2))
    fig_k.add_scatter(x=choix_k["k"], y=choix_k["silhouette"].where(choix_k["k"] == 3), mode="markers",
                       marker=dict(size=13, color=COLORS["terracotta_500"]), name="K=3")
    fig_k.update_layout(
        xaxis_title="K", yaxis_title="Silhouette", margin=dict(l=10, r=10, t=10, b=10), height=PANEL_HEIGHT,
        font_family="Inter, sans-serif", font_size=10, paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=9)),
    )

    # --- AFCM valeurs propres ---
    fig_afcm = go.Figure(go.Bar(x=afcm_vp["axe"], y=afcm_vp["pct_of_variance_benzecri"], marker_color=COLORS["petrole_700"]))
    fig_afcm.update_layout(
        yaxis_title="Variance corrigée (%)", margin=dict(l=10, r=10, t=10, b=10), height=PANEL_HEIGHT,
        font_family="Inter, sans-serif", font_size=10, paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
    )

    # --- Profil quantitatif ---
    dims = [c for c in profil_quanti.columns if c.startswith("Dim")]
    profil_long = profil_quanti.melt(id_vars="cluster_kmeans", value_vars=dims, var_name="axe", value_name="valeur")
    profil_long["cluster_label"] = profil_long["cluster_kmeans"].astype(str).map(CLUSTER_LABELS)
    fig_profil = px.bar(
        profil_long, x="axe", y="valeur", color="cluster_label", barmode="group",
        color_discrete_map={v: CLUSTER_COLORS[k] for k, v in CLUSTER_LABELS.items()},
        category_orders={"cluster_label": list(CLUSTER_LABELS.values())},
    )
    fig_profil.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=PANEL_HEIGHT,
        font_family="Inter, sans-serif", font_size=10, paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        legend=dict(title="", font=dict(size=8), orientation="h", yanchor="bottom", y=1.02),
    )

    # --- Top modalités qualitatives ---
    rows = []
    for cl in sorted(profil_quali["cluster_kmeans"].unique()):
        sub = profil_quali[profil_quali["cluster_kmeans"] == cl].nlargest(3, "pct_dans_cluster")
        for _, row in sub.iterrows():
            rows.append(html.Tr([
                html.Td(CLUSTER_LABELS.get(str(cl), f"C{cl}").split("—")[0].strip()),
                html.Td(row["variable"]), html.Td(row["modalite"]), html.Td(f"{row['pct_dans_cluster']:.0f}%"),
            ]))
    table_quali = html.Table(
        className="fiche-table",
        children=[html.Thead(html.Tr([html.Th("Cluster"), html.Th("Variable"), html.Th("Modalité"), html.Th("%")])), html.Tbody(rows)],
    )

    # --- Communes représentatives ---
    repr_rows = [
        html.Tr([
            html.Td(CLUSTER_LABELS.get(str(row["cluster"]), f"C{row['cluster']}").split("—")[0].strip()),
            html.Td(row["nom_commune"]), html.Td(f"{row['distance']:.2f}"),
        ])
        for _, row in representatives.sort_values(["cluster", "distance"]).iterrows()
    ]
    table_repr = html.Table(
        className="fiche-table",
        children=[html.Thead(html.Tr([html.Th("Cluster"), html.Th("Commune"), html.Th("Distance")])), html.Tbody(repr_rows)],
    )

    # --- Synthèse K-Means vs quartiles ---
    synthese_html = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Critère"), html.Th("K-Means"), html.Th("Quartiles")])),
            html.Tbody([
                html.Tr([html.Td(row["critere"]), html.Td(str(row["kmeans"])), html.Td(str(row["quartiles_iift"]))])
                for _, row in synthese.iterrows()
            ]),
        ],
    )

    tc = tableau_croise.copy()
    tc["cluster_kmeans"] = tc["cluster_kmeans"].astype(str).map(lambda x: CLUSTER_LABELS.get(x, x).split("—")[0].strip())
    table_croise_html = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Cluster")] + [html.Th(c) for c in tc.columns[1:]])),
            html.Tbody([
                html.Tr([html.Td(row["cluster_kmeans"])] + [html.Td(str(row[c])) for c in tc.columns[1:]])
                for _, row in tc.iterrows()
            ]),
        ],
    )

    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="page-header-row",
                children=[
                    html.H1("Clustering & AFCM"),
                    html.Span("Validation K=3, profilage des clusters, comparaison à un modèle de référence", className="page-header-sub"),
                ],
            ),
            kpis,
            build_grid([
                build_chart_panel("Choix de K — silhouette", fig_k),
                build_chart_panel("AFCM — variance par axe (Benzécri)", fig_afcm),
                build_chart_panel("Profil quantitatif des clusters", fig_profil, span="full"),
                build_chart_panel("Top 3 modalités qualitatives / cluster", table_quali),
                build_chart_panel("Communes représentatives", table_repr),
                build_chart_panel("Synthèse : K-Means vs quartiles IIFT", synthese_html),
                build_chart_panel("Tableau croisé : K-Means × quartiles IIFT", table_croise_html),
            ]),
        ],
    )
