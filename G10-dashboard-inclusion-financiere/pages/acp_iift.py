"""Page 3 — ACP & IIFT : layout en grille (panneaux côte à côte, pas un rapport linéaire)."""

import dash
from dash import html
import plotly.express as px
import plotly.graph_objects as go

from components.kpi_card import build_kpi_row
from components.chart_panel import build_chart_panel, build_grid
from data.loaders import get_table, DataLoadError
from data.config import COLORS, CLASSE_IIFT_ORDER, CLASSE_IIFT_COLORS


PANEL_HEIGHT = 300


def layout():
    try:
        valeurs_propres = get_table("acp_valeurs_propres")
        iift = get_table("iift_communes")
        contributions = get_table("acp_contributions_variables")
        dictionnaire = get_table("dictionnaire_iift")
    except DataLoadError as e:
        return html.Div(
            className="page-container",
            children=[html.H1("ACP & IIFT"), html.Div(className="error-banner", children=str(e))],
        )

    dim1_variance = valeurs_propres.loc[valeurs_propres["axe"] == "Dim1", "variance_expliquee_pct"].iloc[0]
    top5_cumulee = valeurs_propres.iloc[4]["variance_cumulee_pct"] if len(valeurs_propres) >= 5 else None
    moyenne_iift = iift["IIFT"].mean()
    n_tres_eleve = (iift["classe_IIFT"] == "Très élevé").sum()

    # --- Scree plot ---
    vp_top = valeurs_propres.head(10)
    fig_scree = go.Figure()
    fig_scree.add_bar(x=vp_top["axe"], y=vp_top["variance_expliquee_pct"], marker_color=COLORS["petrole_700"], name="Variance (%)")
    fig_scree.add_scatter(x=vp_top["axe"], y=vp_top["variance_cumulee_pct"], mode="lines+markers", name="Cumulée (%)",
                           line=dict(color=COLORS["terracotta_500"], width=2), yaxis="y2")
    fig_scree.update_layout(
        yaxis=dict(title="Variance (%)"), yaxis2=dict(title="Cumulée (%)", overlaying="y", side="right", range=[0, 100]),
        margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        font_family="Inter, sans-serif", font_size=11, paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        height=PANEL_HEIGHT,
    )

    # --- Distribution IIFT ---
    fig_dist = px.histogram(iift, x="IIFT", color="classe_IIFT", category_orders={"classe_IIFT": CLASSE_IIFT_ORDER},
                             color_discrete_sequence=CLASSE_IIFT_COLORS, nbins=24)
    fig_dist.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), font_family="Inter, sans-serif", font_size=11,
        paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        legend=dict(title="", font=dict(size=9), orientation="h", yanchor="bottom", y=1.02),
        height=PANEL_HEIGHT, bargap=0.05,
    )

    # --- Top contributions Dim1 ---
    top_contrib = contributions.nlargest(8, "Dim1")[["variable", "Dim1"]].sort_values("Dim1")
    fig_contrib = go.Figure(go.Bar(x=top_contrib["Dim1"], y=top_contrib["variable"], orientation="h", marker_color=COLORS["petrole_700"]))
    fig_contrib.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), xaxis_title="Contribution à Dim1 (%)",
        font_family="Inter, sans-serif", font_size=10, paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        height=PANEL_HEIGHT,
    )

    dict_table = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Variable"), html.Th("Interprétation")])),
            html.Tbody([
                html.Tr([html.Td(row["variable"]), html.Td(row["interpretation"])])
                for _, row in dictionnaire.iterrows()
            ]),
        ],
    )

    return html.Div(
        className="page-container",
        children=[
            html.Div(
                className="page-header-row",
                children=[
                    html.H1("ACP & Indice IIFT"),
                    html.Span("Construction de l'indice composite (score ACP Dim1, 0-100)", className="page-header-sub"),
                ],
            ),
            build_kpi_row([
                {"label": "Variance Dim1", "value": f"{dim1_variance:.1f}%"},
                {"label": "Variance cumulée (5 axes)", "value": f"{top5_cumulee:.1f}%" if top5_cumulee else "n/d"},
                {"label": "IIFT moyen national", "value": f"{moyenne_iift:.1f}", "accent": True},
                {"label": "Communes 'Très élevé'", "value": str(n_tres_eleve)},
            ]),
            build_grid([
                build_chart_panel("Éboulis des valeurs propres", fig_scree),
                build_chart_panel("Distribution de l'IIFT par classe", fig_dist),
                build_chart_panel("Top 8 variables contributives à Dim1", fig_contrib),
                build_chart_panel("Dictionnaire IIFT", dict_table, caption=f"{len(dictionnaire)} variables"),
            ]),
        ],
    )
