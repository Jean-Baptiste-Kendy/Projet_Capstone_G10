"""Page 3 — ACP & IIFT : construction et justification de l'indice composite."""

import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go

from components.kpi_card import build_kpi_row
from data.loaders import get_table, DataLoadError
from data.config import COLORS

dash.register_page(__name__, path="/acp-iift", name="ACP & IIFT", order=3)

CLASSE_ORDER = ["Très faible", "Faible", "Moyen", "Élevé", "Très élevé"]
CLASSE_COLORS = [
    COLORS["terracotta_700"],
    COLORS["terracotta_500"],
    COLORS["petrole_200"],
    COLORS["petrole_500"],
    COLORS["petrole_900"],
]


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

    # --- Scree plot (10 premiers axes) ---
    vp_top = valeurs_propres.head(10)
    fig_scree = go.Figure()
    fig_scree.add_bar(
        x=vp_top["axe"], y=vp_top["variance_expliquee_pct"],
        marker_color=COLORS["petrole_700"], name="Variance expliquée (%)",
    )
    fig_scree.add_scatter(
        x=vp_top["axe"], y=vp_top["variance_cumulee_pct"],
        mode="lines+markers", name="Variance cumulée (%)",
        line=dict(color=COLORS["terracotta_500"], width=2),
        yaxis="y2",
    )
    fig_scree.update_layout(
        yaxis=dict(title="Variance expliquée (%)"),
        yaxis2=dict(title="Variance cumulée (%)", overlaying="y", side="right", range=[0, 100]),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        font_family="Inter, sans-serif",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        height=380,
    )

    # --- Distribution de l'IIFT par classe ---
    fig_dist = px.histogram(
        iift, x="IIFT", color="classe_IIFT",
        category_orders={"classe_IIFT": CLASSE_ORDER},
        color_discrete_sequence=CLASSE_COLORS,
        nbins=28,
    )
    fig_dist.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        font_family="Inter, sans-serif",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        legend=dict(title="Classe IIFT"),
        height=380,
        bargap=0.05,
    )

    # --- Top 10 contributions à Dim1 ---
    top_contrib = contributions.nlargest(10, "Dim1")[["variable", "Dim1"]].sort_values("Dim1")
    fig_contrib = go.Figure(
        go.Bar(
            x=top_contrib["Dim1"], y=top_contrib["variable"],
            orientation="h", marker_color=COLORS["petrole_700"],
        )
    )
    fig_contrib.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Contribution à Dim1 (%)",
        font_family="Inter, sans-serif",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        height=380,
    )

    dict_table = html.Table(
        className="fiche-table",
        children=[
            html.Thead(html.Tr([html.Th("Variable"), html.Th("Interprétation"), html.Th("Méthode")])),
            html.Tbody([
                html.Tr([html.Td(row["variable"]), html.Td(row["interpretation"]), html.Td(row["methode"])])
                for _, row in dictionnaire.iterrows()
            ]),
        ],
    )

    return html.Div(
        className="page-container",
        children=[
            html.H1("ACP & Indice IIFT"),
            html.P(
                "L'indice IIFT (Indice d'Inclusion Financière Territoriale) est construit "
                "à partir du score ACP Dim1, orienté puis normalisé sur une échelle 0-100.",
                style={"color": "var(--text-secondary)"},
            ),
            build_kpi_row([
                {"label": "Variance expliquée par Dim1", "value": f"{dim1_variance:.1f}%"},
                {
                    "label": "Variance cumulée (5 premiers axes)",
                    "value": f"{top5_cumulee:.1f}%" if top5_cumulee else "n/d",
                },
                {"label": "IIFT moyen national", "value": f"{moyenne_iift:.1f}", "accent": True},
                {"label": "Communes classe 'Très élevé'", "value": str(n_tres_eleve)},
            ]),

            html.H3("Éboulis des valeurs propres (scree plot)"),
            dcc.Graph(figure=fig_scree, config={"displayModeBar": False}),

            html.H3("Distribution de l'IIFT par classe", style={"marginTop": "24px"}),
            dcc.Graph(figure=fig_dist, config={"displayModeBar": False}),

            html.H3("Variables les plus contributives à Dim1", style={"marginTop": "24px"}),
            dcc.Graph(figure=fig_contrib, config={"displayModeBar": False}),

            html.H3("Dictionnaire IIFT", style={"marginTop": "24px"}),
            dict_table,
        ],
    )
