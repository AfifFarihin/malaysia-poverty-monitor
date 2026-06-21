"""
Stakeholder app layout - HTML/dbc structure only, no callbacks.
"""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from . import charts as C
from . import data as D

# ── palette ───────────────────────────────────────────────────────────────────
TEAL  = "#2E75B6"
DARK  = "#1F3864"
AMBER = "#C6A000"
LIGHT = "#DCE6F1"
RED   = "#C00000"
GREEN = "#217346"

# ── precomputed insight facts (verified against data) ─────────────────────────
def _key_takeaways_band() -> html.Div:
    panel = D.load_panel()
    # Top poverty state 2022
    top = panel[panel["year"] == 2022].sort_values("poverty_absolute", ascending=False).iloc[0]
    nat22 = panel[panel["year"] == 2022]["poverty_absolute"].mean()
    # Best COVID recovery (2020→2022)
    p20 = panel[panel["year"] == 2020].set_index("state")["poverty_absolute"]
    p22 = panel[panel["year"] == 2022].set_index("state")["poverty_absolute"]
    recovery = (p22 - p20).dropna().sort_values()
    best_rec_state = recovery.index[0]
    best_rec_val   = recovery.iloc[0]

    card_style = {
        "background": "white",
        "border": f"1px solid {LIGHT}",
        "borderRadius": "10px",
        "padding": "10px 12px",
        "boxShadow": "0 .125rem .25rem rgba(0,0,0,.055)",
        "minHeight": "82px",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
    }

    def card(label: str, headline: str, detail: str, accent: str = TEAL) -> dbc.Col:
        return dbc.Col(html.Div([
            html.Div(label.upper(), style={
                "fontSize": "0.64rem", "fontWeight": "800",
                "letterSpacing": "0.04rem", "color": accent,
                "marginBottom": "4px",
            }),
            html.Div(headline, style={
                "fontSize": "0.86rem", "fontWeight": "700",
                "color": DARK, "lineHeight": "1.18",
            }),
            html.Div(detail, style={
                "fontSize": "0.73rem", "color": "#556",
                "lineHeight": "1.25", "marginTop": "4px",
            }),
        ], style=card_style), width=3)

    return html.Div([
        html.Div("Key takeaways for stakeholders", style={
            "fontSize": "0.78rem", "fontWeight": "800",
            "color": DARK, "marginBottom": "8px",
        }),
        dbc.Row([
            card(
                "Observed poverty group",
                f"{top['state']} is the highest-poverty state in 2022",
                f"{top['poverty_absolute']:.1f} pp, about {top['poverty_absolute']/nat22:.1f}x the state average.",
                RED,
            ),
            card(
                "Trend signal",
                f"{best_rec_state} showed the largest poverty reduction since 2020",
                f"Change from 2020 to 2022: {best_rec_val:+.1f} percentage points.",
                GREEN,
            ),
            card(
                "Model reliability",
                "Useful monitoring signal",
                f"Average error is {D.CERTIFIED_KPIS['MAE']:.2f} pp; official DOSM statistics remain the source of record.",
                TEAL,
            ),
            card(
                "How to use it",
                "Investigate patterns carefully",
                "Use the dashboard to support questions, comparison, and transparency.",
                AMBER,
            ),
        ], className="g-2"),
    ], style={
        "background": "#EDF3F8",
        "padding": "10px 24px 12px",
        "borderBottom": f"1px solid {LIGHT}",
    })
# ── small helpers ─────────────────────────────────────────────────────────────
def _kpi_chip(label: str, value: str, help_text: str = "") -> html.Div:
    return html.Div([
        html.Div(value, style={
            "fontSize": "1.5rem", "fontWeight": "700",
            "color": TEAL, "lineHeight": "1",
        }),
        html.Div(label, style={
            "fontSize": "0.72rem", "color": "#aab", "marginTop": "2px",
        }),
        html.Div(help_text, style={
            "fontSize": "0.62rem", "color": "#7f8fa6", "marginTop": "2px",
        }) if help_text else None,
    ], style={
        "background": "#fff", "borderRadius": "8px",
        "padding": "10px 18px", "minWidth": "128px",
        "textAlign": "center", "border": f"1px solid {LIGHT}",
        "minHeight": "64px", "display": "flex", "flexDirection": "column",
        "justifyContent": "center",
    })


def _section_card(*children, title: str = "", class_name: str = "") -> dbc.Card:
    body = []
    if title:
        body.append(html.H6(title, className="mb-3",
                            style={"color": DARK, "fontWeight": "600"}))
    body.extend(children)
    return dbc.Card(dbc.CardBody(body),
                    className=f"shadow-sm mb-3 {class_name}".strip(),
                    style={"border": f"1px solid {LIGHT}", "borderRadius": "10px"})


def _guidance_card(title: str, body: str, tone: str = "info") -> dbc.Card:
    color = TEAL if tone == "info" else AMBER
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, style={
                "fontSize": "0.82rem", "fontWeight": "700",
                "color": DARK, "marginBottom": "4px",
            }),
            html.Div(body, style={
                "fontSize": "0.80rem", "color": "#445",
                "lineHeight": "1.35",
            }),
        ]),
        className="shadow-sm mb-3",
        style={
            "borderLeft": f"5px solid {color}",
            "borderTop": f"1px solid {LIGHT}",
            "borderRight": f"1px solid {LIGHT}",
            "borderBottom": f"1px solid {LIGHT}",
            "borderRadius": "10px",
            "background": "#FFFFFF",
        },
    )


# ── sidebar ───────────────────────────────────────────────────────────────────
def _sidebar() -> html.Div:
    return html.Div([
        # Filters
        html.H6("Choose review settings", style={"color": DARK, "fontWeight": "700", "marginBottom": "12px"}),

        html.Label("Choose survey year", style={"fontSize": "0.8rem", "color": "#555"}),
        dcc.Dropdown(
            id="year-dd",
            options=[{"label": str(y), "value": y} for y in D.SURVEY_YEARS],
            value=2022,
            clearable=False,
            style={"marginBottom": "12px", "fontSize": "0.9rem"},
        ),

        html.Label("Choose poverty type", style={"fontSize": "0.8rem", "color": "#555"}),
        dcc.RadioItems(
            id="target-radio",
            options=[
                {"label": " Absolute poverty", "value": "poverty_absolute"},
                {"label": " Relative poverty", "value": "poverty_relative"},
            ],
            value="poverty_absolute",
            inputStyle={"marginRight": "6px"},
            style={"fontSize": "0.88rem", "marginBottom": "14px"},
            labelStyle={"display": "block", "marginBottom": "4px"},
        ),

        html.Label("Choose state to review", style={"fontSize": "0.8rem", "color": "#555"}),
        dcc.Dropdown(
            id="state-dd",
            options=[{"label": s, "value": s} for s in sorted(D.STATE_JOIN_MAP.keys())],
            value="Sabah",
            clearable=False,
            style={"marginBottom": "12px", "fontSize": "0.9rem"},
        ),

        html.Div([
            html.Label("Compare in trend", style={
                "fontSize": "0.8rem", "color": "#555", "margin": 0,
            }),
            dbc.Button(
                "All / Clear",
                id="compare-toggle-btn",
                n_clicks=0,
                size="sm",
                outline=True,
                color="primary",
                style={
                    "fontSize": "0.64rem", "padding": "2px 6px",
                    "lineHeight": "1.2",
                    "whiteSpace": "nowrap",
                },
            ),
        ], style={
            "display": "flex", "alignItems": "center",
            "justifyContent": "space-between", "gap": "6px",
            "marginBottom": "4px",
        }),
        dcc.Dropdown(
            id="compare-states-dd",
            options=[{"label": s, "value": s} for s in sorted(D.STATE_JOIN_MAP.keys())],
            value=["Sabah", "Kelantan"],
            multi=True,
            clearable=False,
            style={"marginBottom": "20px", "fontSize": "0.88rem"},
        ),

        html.Hr(style={"borderColor": LIGHT}),

        html.H6("How to use this", style={"color": DARK, "fontWeight": "700",
                                               "marginBottom": "8px", "fontSize": "0.8rem"}),
        html.Div([
            html.Div("Selected model", style={"fontSize": "0.68rem", "color": "#778"}),
            html.Div("Random Forest", style={"fontSize": "0.85rem", "fontWeight": "700", "color": TEAL}),
            html.Div(f"Average error: {D.CERTIFIED_KPIS['MAE']:.2f} percentage points", style={"fontSize": "0.72rem", "color": "#445", "marginTop": "6px"}),
            html.Div("Use it to compare patterns, then confirm conclusions with official DOSM evidence.", style={"fontSize": "0.72rem", "color": "#445", "marginTop": "6px"}),
        ], style={
            "background": "#F7F9FC",
            "border": f"1px solid {LIGHT}",
            "borderRadius": "8px",
            "padding": "10px",
        }),

    ], style={
        "padding": "20px 14px",
        "background": "white",
        "borderRight": f"1px solid {LIGHT}",
        "height": "100vh",
        "overflowY": "auto",
        "position": "sticky",
        "top": 0,
    })


# ── header ────────────────────────────────────────────────────────────────────
def _header() -> html.Div:
    k = D.CERTIFIED_KPIS
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Malaysia Poverty Monitor", style={
                    "fontSize": "1.25rem", "fontWeight": "800",
                    "color": "white", "letterSpacing": "0.3px",
                    "lineHeight": "1.1",
                }),
                html.Div("Stakeholder view for state monitoring", style={
                    "fontSize": "0.76rem", "color": "#B8C7DD",
                    "marginTop": "4px",
                }),
            ]), width=4),
            dbc.Col(html.Div([
                html.Div([
                    _kpi_chip("Average prediction error", f"{k['MAE']:.2f} pp", "lower is better"),
                    _kpi_chip("Large-error penalty",      f"{k['RMSE']:.2f} pp", "checks big misses"),
                    _kpi_chip("Pattern explained",        f"{k['R2']:.2f}", "higher is better"),
                    _kpi_chip("Ranking agreement",        f"{k['Spearman']:.2f}", "higher is better"),
                ], style={
                    "display": "flex", "gap": "12px", "flexWrap": "wrap",
                    "alignItems": "center", "justifyContent": "center",
                }),
                html.Div("Selected model - absolute poverty - tested by leaving each state out once",
                         style={"fontSize": "0.68rem", "color": "#8899aa",
                                "textAlign": "center", "marginTop": "5px"}),
            ]),
            width=8),
        ], align="center", style={"width": "100%"}),
    ], style={
        "background": DARK,
        "padding": "12px 24px",
        "borderBottom": f"3px solid {TEAL}",
        "display": "flex",
        "alignItems": "center",
        "minHeight": "92px",
    })


# ── Tab 1 — Overview ──────────────────────────────────────────────────────────
def _tab_overview() -> html.Div:
    return html.Div([
        _guidance_card(
            "What stakeholders should notice",
            "Use this page as a briefing view: compare observed poverty levels, check whether the model follows official survey trends, and see which supporting indicators describe the pattern. It supports investigation, but it does not replace DOSM statistics or determine policy priorities.",
        ),
        dbc.Row([
            dbc.Col(_section_card(
                dcc.Loading(
                    dcc.Graph(id="map-graph", config={"displayModeBar": False}),
                    type="circle", color=TEAL,
                ),
                title="Where poverty was higher in the selected year",
            ), width=7),
            dbc.Col(_section_card(
                dcc.Graph(id="ranking-bar", config={"displayModeBar": False}),
                title="Highest-poverty states for planning discussion",
            ), width=5),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(_section_card(
                dcc.Graph(id="overview-trend", config={"displayModeBar": False}),
                title="The model trend compared with official surveys",
            ), width=7),
            dbc.Col(_section_card(
                html.Div([
                    html.P(id="shap-title",
                           children="Main factors behind the selected model",
                           style={"fontWeight": "600", "color": DARK,
                                  "fontSize": "0.85rem", "marginBottom": "4px"}),
                    html.Small(id="shap-note", style={
                        "color": AMBER, "fontSize": "0.75rem",
                        "display": "block", "marginBottom": "6px",
                    }),
                    html.Div(id="factor-list"),
                ])
            ), width=5),
        ], className="g-3 mt-0"),
        dbc.Row([
            dbc.Col(_section_card(
                dcc.Graph(id="ntl-scatter", config={"displayModeBar": False}),
            title="Night-time lights as a supporting indicator",
            ), width=6),
            dbc.Col(_section_card(
                dcc.Graph(id="delta-bar", config={"displayModeBar": False}),
                title="Which states improved or worsened over time",
            ), width=6),
        ], className="g-3 mt-0"),
    ], style={"padding": "16px"})


# ── Tab 2 — State Review ──────────────────────────────────────────────────────
def _tab_detail() -> html.Div:
    return html.Div([
        html.Div(id="state-recommendation"),
        # KPI cards
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(id="kpi-state-val", style={
                    "fontSize": "1.1rem", "fontWeight": "700", "color": TEAL,
                    "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap",
                }),
                html.Div("Selected state", style={"fontSize": "0.72rem", "color": "#888"}),
            ])), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(id="kpi-poverty-val", style={
                    "fontSize": "1.3rem", "fontWeight": "700", "color": TEAL,
                }),
                html.Div(id="kpi-poverty-lbl", style={"fontSize": "0.72rem", "color": "#888"}),
            ])), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(id="kpi-rank-val", style={
                    "fontSize": "1.3rem", "fontWeight": "700", "color": TEAL,
                }),
                html.Div("Poverty rank (1 = highest)", style={"fontSize": "0.72rem", "color": "#888"}),
            ])), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(id="kpi-delta-val", style={
                    "fontSize": "1.3rem", "fontWeight": "700", "color": RED,
                }),
                html.Div(id="kpi-delta-lbl", style={"fontSize": "0.72rem", "color": "#888"}),
            ])), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(id="kpi-recovery-val", style={
                    "fontSize": "1.3rem", "fontWeight": "700", "color": TEAL,
                }),
                html.Div(id="kpi-recovery-lbl", style={"fontSize": "0.70rem", "color": "#888"}),
            ])), width=4),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_section_card(
                dcc.Loading(
                    dcc.Graph(id="detail-trend", config={"displayModeBar": False}),
                    type="circle", color=TEAL,
                ),
                title="How selected states changed over time",
            ), width=6),
            dbc.Col(_section_card(
                dcc.Graph(id="proxy-bar", config={"displayModeBar": False}),
                title="Supporting indicators for the selected state",
            ), width=6),
        ], className="g-3"),

        _section_card(
            dash_table.DataTable(
                id="detail-table",
                columns=[],
                data=[],
                tooltip_header={
                    "Prediction Gap":     "Difference between the official DOSM survey value and the model estimate.",
                    "Night-light Rank":   "Rank 1 = lowest night-time light among the 16 states (potentially more disadvantaged).",
                    "Urbanisation Rank":  "Rank 1 = lowest urban share among the 16 states (potentially more disadvantaged).",
                },
                tooltip_delay=0,
                tooltip_duration=None,
                style_table={"overflowX": "auto", "maxHeight": "320px", "overflowY": "auto"},
                style_header={
                    "backgroundColor": DARK, "color": "white",
                    "fontWeight": "bold", "fontSize": "12px",
                    "position": "sticky", "top": 0,
                },
                style_cell={
                    "fontSize": "12px", "padding": "6px 10px",
                    "fontFamily": "Inter, Arial, sans-serif",
                    "textAlign": "right", "border": f"1px solid {LIGHT}",
                },
                style_cell_conditional=[
                    {"if": {"column_id": "state"}, "textAlign": "left"},
                ],
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#FAFBFC"},
                ],
                page_size=16,
                sort_action="native",
            ),
            title="Compare all states in the selected year",
        ),
    ], style={"padding": "16px"})


# ── Tab 3 — Reliability Check (static) ───────────────────────────────────────
def _tab_model() -> html.Div:
    unc = D.load_uncertainty()
    unc_xgb = unc[
        (unc["model"] == D.PRIMARY_ABSOLUTE_MODEL) & (unc["target"] == "poverty_absolute")
    ].sort_values("metric")

    unc_table_cols = [
        {"name": "Measure", "id": "metric"},
        {"name": "Value", "id": "observed"},
        {"name": "Likely range", "id": "range"},
    ]
    metric_labels = {
        "mae": "Average prediction error",
        "rmse": "Large-error penalty",
        "r2": "Pattern explained",
        "spearman": "Ranking agreement",
        "pearson": "Linear trend agreement",
    }
    unc_table_data = [
        {
            "metric":   metric_labels.get(str(r["metric"]).lower(), r["metric"]),
            "observed": f"{r['observed']:.3f}",
            "range":    f"{r['ci_lower']:.3f} to {r['ci_upper']:.3f}",
        }
        for _, r in unc_xgb.iterrows()
    ]

    return html.Div([
        _guidance_card(
            "Can stakeholders trust this signal?",
            f"The selected model follows broad state patterns with an average held-out error of about {D.CERTIFIED_KPIS['MAE']:.2f} percentage points. Use this page to judge uncertainty before interpreting estimates. It supports review, but does not set priorities or replace official DOSM survey releases.",
        ),
        dbc.Row([
            dbc.Col(_section_card(
                dcc.Graph(
                    figure=C.make_model_comparison(),
                    config={"displayModeBar": False},
                ),
                title="Which approach gave the most useful monitoring estimates?",
                class_name="h-100",
            ), width=8),
            dbc.Col(_section_card(
                html.P("Repeated-sampling uncertainty for the selected absolute-poverty model.",
                       style={"fontSize": "0.78rem", "color": "#888", "marginBottom": "10px"}),
                dash_table.DataTable(
                    columns=unc_table_cols,
                    data=unc_table_data,
                    style_header={
                        "backgroundColor": DARK, "color": "white",
                        "fontWeight": "bold", "fontSize": "12px",
                    },
                    style_cell={
                        "fontSize": "12px", "padding": "6px 10px",
                        "fontFamily": "Inter, Arial, sans-serif",
                        "textAlign": "right",
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "metric"}, "textAlign": "left"},
                    ],
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#FAFBFC"},
                    ],
                ),
                html.P(
                    "A negative lower bound on Pattern explained (R²) is expected "
                    "in small-sample held-out validation and does not indicate a model error.",
                    style={"fontSize": "0.72rem", "color": "#888", "marginTop": "8px", "marginBottom": "0"},
                ),
                title="How wide is the uncertainty range?",
                class_name="h-100",
            ), width=4),
        ], className="g-3 align-items-stretch"),

        _section_card(
            dcc.Graph(
                figure=D.FIGURE_ERROR_HEATMAP,
                config={"displayModeBar": False},
                style={"height": "420px"},
            ),
            title="Where the model had larger prediction gaps",
        ),
        _section_card(
            dcc.Graph(
                figure=D.FIGURE_PROXY_CORR,
                config={"displayModeBar": False},
                style={"height": "280px"},
            ),
            title="Supporting indicators that move with poverty rankings",
        ),
    ], style={"padding": "16px"})


# ── root layout ───────────────────────────────────────────────────────────────
def create_layout() -> html.Div:
    return html.Div([
        _header(),
        _key_takeaways_band(),
        dbc.Row([
            # Sidebar
            dbc.Col(_sidebar(), width=2,
                    style={"paddingLeft": 0, "paddingRight": 0}),
            # Main content
            dbc.Col([
                dbc.Tabs(
                    id="main-tabs",
                    active_tab="tab-overview",
                    children=[
                        dbc.Tab(_tab_overview(),     label="Overview",          tab_id="tab-overview"),
                        dbc.Tab(_tab_detail(),       label="State Review",      tab_id="tab-detail"),
                        dbc.Tab(_tab_model(),        label="Reliability Check", tab_id="tab-model"),
                    ],
                    style={"borderBottom": f"2px solid {LIGHT}"},
                ),
            ], width=10, style={"paddingLeft": 0, "paddingRight": 0}),
        ], className="g-0"),
    ], style={"fontFamily": "Inter, Arial, sans-serif", "background": "#F7F9FC",
              "minHeight": "100vh"})
