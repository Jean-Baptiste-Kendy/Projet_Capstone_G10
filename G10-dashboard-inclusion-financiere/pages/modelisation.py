"""Page 5 — Modélisation supervisée : Ridge / Lasso / Random Forest."""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go

from components.kpi_card import build_kpi_row
from data.loaders import get_table, DataLoadError
from data.config import COLORS

dash.register_page(__name__, path="/modelisation", name="Modélisation", order=5)

MODEL_COLUMNS = {
    "IIFT_predit_ridge": "Ridge",
    "IIFT_predit_lasso": "Lasso",
    "IIFT_predit_rf": "Random Forest",
}


def layout():
    try:
        comparaison = get_table("modelisation_comparaison")
        importance = get_table("modelisation_importance")
        predictions = get_table("modelisation_predictions")
        variables_retirees = get_table("modelisation_variables_lasso_retirees")
    except DataLoadError as e:
        return html.Div(
            className="page-container",
            children=[html.H1("Modélisation supervisée"), html.Div(className="error-banner", children=str(e))],
        )

    meilleur = comparaison.loc[comparaison["R2_test"].idxmax()]

    kpis = build_kpi_row([
        {"label": "Meilleur modèle (R² test)", "value": meilleur["modele"], "accent": True},
        {"label": "R² test", "value": f"{meilleur['R2_test']:.3f}"},
        {"label": "RMSE test", "value": f"{meilleur['RMSE_test']:.2f}"},
        {
            "label": "Variable retirée (Lasso)",
            "value": ", ".join(variables_retirees["variable"].tolist()),
        },
    ])

    # --- Comparaison des modèles ---
    fig_comp = go.Figure()
    fig_comp.add_bar(
        x=comparaison["modele"], y=comparaison["R2_test"],
        name="R² test", marker_color=COLORS["petrole_700"], yaxis="y1",
    )
    fig_comp.add_bar(
        x=comparaison["modele"], y=comparaison["RMSE_test"],
        name="RMSE test", marker_color=COLORS["terracotta_500"], yaxis="y2",
    )
    fig_comp.update_layout(
        barmode="group",
        yaxis=dict(title="R² (test)", range=[0, 1.05]),
        yaxis2=dict(title="RMSE (test)", overlaying="y", side="right"),
        margin=dict(l=10, r=10, t=10, b=10), height=360,
        font_family="Inter, sans-serif", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    # --- Feature importance (moyenne des 4 méthodes) ---
    top_importance = importance.nlargest(12, "moyenne_4_methodes").sort_values("moyenne_4_methodes")
    fig_importance = go.Figure(
        go.Bar(
            x=top_importance["moyenne_4_methodes"], y=top_importance["variable"],
            orientation="h", marker_color=COLORS["petrole_700"],
        )
    )
    fig_importance.update_layout(
        xaxis_title="Importance moyenne (%) — Ridge / Lasso / RF impureté / RF permutation",
        margin=dict(l=10, r=10, t=10, b=10), height=420,
        font_family="Inter, sans-serif", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
    )

    return html.Div(
        className="page-container",
        children=[
            html.H1("Modélisation supervisée"),
            html.P(
                "Comparaison Ridge / Lasso / Random Forest pour la prédiction de l'IIFT, "
                "et analyse de l'importance des variables.",
                style={"color": "var(--text-secondary)"},
            ),
            kpis,

            html.H3("Comparaison des modèles"),
            dcc.Graph(figure=fig_comp, config={"displayModeBar": False}),

            html.H3("IIFT prédit vs réel", style={"marginTop": "24px"}),
            html.Div(
                style={"maxWidth": "280px", "marginBottom": "8px"},
                children=[
                    dcc.Dropdown(
                        id="modelisation-choix-modele",
                        options=[{"label": v, "value": k} for k, v in MODEL_COLUMNS.items()],
                        value="IIFT_predit_rf",
                        clearable=False,
                    ),
                ],
            ),
            dcc.Graph(id="modelisation-scatter-predit-reel", config={"displayModeBar": False}),

            html.H3("Importance des variables (top 12)", style={"marginTop": "24px"}),
            dcc.Graph(figure=fig_importance, config={"displayModeBar": False}),
        ],
    )


@callback(
    Output("modelisation-scatter-predit-reel", "figure"),
    Input("modelisation-choix-modele", "value"),
)
def update_scatter(modele_col):
    try:
        predictions = get_table("modelisation_predictions")
    except DataLoadError:
        return go.Figure()

    label = MODEL_COLUMNS.get(modele_col, modele_col)

    fig = px.scatter(
        predictions, x="IIFT", y=modele_col, color="ensemble",
        color_discrete_map={"train": COLORS["petrole_700"], "test": COLORS["terracotta_500"]},
        hover_name="nom_commune",
        labels={"IIFT": "IIFT réel", modele_col: f"IIFT prédit ({label})", "ensemble": "Échantillon"},
    )
    min_v = min(predictions["IIFT"].min(), predictions[modele_col].min())
    max_v = max(predictions["IIFT"].max(), predictions[modele_col].max())
    fig.add_shape(
        type="line", x0=min_v, y0=min_v, x1=max_v, y1=max_v,
        line=dict(color=COLORS["text_secondary"], dash="dash"),
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=420,
        font_family="Inter, sans-serif", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
    )
    return fig
