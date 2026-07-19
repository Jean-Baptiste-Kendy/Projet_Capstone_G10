"""Page 4 — Clustering & AFCM : robustesse méthodologique de la typologie K=3."""

import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from components.kpi_card import build_kpi_row
from data.loaders import get_table, DataLoadError
from data.config import COLORS, CLUSTER_COLORS, CLUSTER_LABELS

dash.register_page(__name__, path="/clustering-afcm", name="Clustering & AFCM", order=4)


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

    # --- KPIs ---
    kpis = build_kpi_row([
        {"label": "K retenu", "value": "3", "accent": True},
        {"label": "Silhouette (K=3)", "value": f"{silhouette_k3:.3f}"},
        {
            "label": "Répartition des clusters",
            "value": " / ".join(str(v) for v in tailles.values),
            "sublabel": "communes par cluster (0, 1, 2)",
        },
        {
            "label": "Variance Axe 1 AFCM (corrigée Benzécri)",
            "value": f"{afcm_vp.iloc[0]['pct_of_variance_benzecri']:.1f}%",
        },
    ])

    # --- Courbe silhouette / inertie vs K ---
    fig_k = go.Figure()
    fig_k.add_scatter(
        x=choix_k["k"], y=choix_k["silhouette"], mode="lines+markers",
        name="Silhouette", line=dict(color=COLORS["petrole_700"], width=2),
    )
    fig_k.add_scatter(
        x=choix_k["k"], y=choix_k["silhouette"].where(choix_k["k"] == 3),
        mode="markers", marker=dict(size=14, color=COLORS["terracotta_500"]),
        name="K retenu = 3", showlegend=True,
    )
    fig_k.update_layout(
        xaxis_title="Nombre de clusters (K)", yaxis_title="Score de silhouette",
        margin=dict(l=10, r=10, t=10, b=10), height=340,
        font_family="Inter, sans-serif", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    # --- AFCM valeurs propres (Benzécri) ---
    fig_afcm = go.Figure(
        go.Bar(
            x=afcm_vp["axe"], y=afcm_vp["pct_of_variance_benzecri"],
            marker_color=COLORS["petrole_700"],
        )
    )
    fig_afcm.update_layout(
        yaxis_title="Variance expliquée corrigée Benzécri (%)",
        margin=dict(l=10, r=10, t=10, b=10), height=340,
        font_family="Inter, sans-serif", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
    )

    # --- Profil quantitatif des clusters (Dim1-Dim6) ---
    dims = [c for c in profil_quanti.columns if c.startswith("Dim")]
    profil_long = profil_quanti.melt(id_vars="cluster_kmeans", value_vars=dims, var_name="axe", value_name="valeur")
    profil_long["cluster_label"] = profil_long["cluster_kmeans"].astype(str).map(CLUSTER_LABELS)
    fig_profil = px.bar(
        profil_long, x="axe", y="valeur", color="cluster_label", barmode="group",
        color_discrete_map={v: CLUSTER_COLORS[k] for k, v in CLUSTER_LABELS.items()},
        category_orders={"cluster_label": list(CLUSTER_LABELS.values())},
    )
    fig_profil.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=360,
        font_family="Inter, sans-serif", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        legend=dict(title="Cluster"),
    )

    # --- Top modalités qualitatives par cluster ---
    top_modalites_rows = []
    for cl in sorted(profil_quali["cluster_kmeans"].unique()):
        sub = profil_quali[profil_quali["cluster_kmeans"] == cl].nlargest(3, "pct_dans_cluster")
        for _, row in sub.iterrows():
            top_modalites_rows.append(
                html.Tr([
                    html.Td(CLUSTER_LABELS.get(str(cl), f"Cluster {cl}")),
                    html.Td(row["variable"]),
                    html.Td(row["modalite"]),
                    html.Td(f"{row['pct_dans_cluster']:.1f}%"),
                ])
            )
    table_quali = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Cluster"), html.Th("Variable"), html.Th("Modalité"), html.Th("% dans le cluster")])),
            html.Tbody(top_modalites_rows),
        ],
    )

    # --- Communes représentatives ---
    repr_rows = [
        html.Tr([
            html.Td(CLUSTER_LABELS.get(str(row["cluster"]), f"Cluster {row['cluster']}")),
            html.Td(row["nom_commune"]),
            html.Td(f"{row['distance']:.2f}"),
        ])
        for _, row in representatives.sort_values(["cluster", "distance"]).iterrows()
    ]
    table_repr = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Cluster"), html.Th("Commune représentative"), html.Th("Distance au centroïde")])),
            html.Tbody(repr_rows),
        ],
    )

    # --- Tableau croisé K-Means x quartiles IIFT ---
    tc = tableau_croise.copy()
    tc["cluster_kmeans"] = tc["cluster_kmeans"].astype(str).map(CLUSTER_LABELS)
    table_croise_html = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Cluster K-Means")] + [html.Th(c) for c in tc.columns[1:]])),
            html.Tbody([
                html.Tr([html.Td(row["cluster_kmeans"])] + [html.Td(str(row[c])) for c in tc.columns[1:]])
                for _, row in tc.iterrows()
            ]),
        ],
    )

    synthese_html = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Critère"), html.Th("K-Means"), html.Th("Quartiles IIFT")])),
            html.Tbody([
                html.Tr([html.Td(row["critere"]), html.Td(str(row["kmeans"])), html.Td(str(row["quartiles_iift"]))])
                for _, row in synthese.iterrows()
            ]),
        ],
    )

    return html.Div(
        className="page-container",
        children=[
            html.H1("Clustering & AFCM"),
            html.P(
                "Validation de la typologie K-Means (K=3) et profilage qualitatif/quantitatif "
                "des clusters via l'AFCM officielle (correction Benzécri).",
                style={"color": "var(--text-secondary)"},
            ),
            kpis,

            html.H3("Choix de K : score de silhouette"),
            dcc.Graph(figure=fig_k, config={"displayModeBar": False}),

            html.H3("AFCM — variance expliquée par axe (correction Benzécri)", style={"marginTop": "24px"}),
            dcc.Graph(figure=fig_afcm, config={"displayModeBar": False}),

            html.H3("Profil quantitatif des clusters (axes ACP retenus)", style={"marginTop": "24px"}),
            dcc.Graph(figure=fig_profil, config={"displayModeBar": False}),

            html.H3("Profil qualitatif — 3 modalités dominantes par cluster", style={"marginTop": "24px"}),
            table_quali,

            html.H3("Communes représentatives (les plus proches du centroïde)", style={"marginTop": "24px"}),
            table_repr,

            html.H3("Validation : K-Means vs quartiles de l'IIFT", style={"marginTop": "24px"}),
            html.P(
                "Comparaison de la typologie non supervisée (K-Means) à un modèle de "
                "référence simple (découpage en quartiles de l'IIFT).",
                style={"color": "var(--text-secondary)", "fontSize": "13px"},
            ),
            synthese_html,
            html.Div(style={"height": "12px"}),
            table_croise_html,
        ],
    )
