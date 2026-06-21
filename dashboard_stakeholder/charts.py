"""
Chart factory — pure functions: data in, go.Figure out.
No Dash imports; no side effects.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .data import (
    CERTIFIED_KPIS,
    MODEL_LABELS,
    PRIMARY_ABSOLUTE_MODEL,
    SURVEY_YEARS,
    TARGET_LABELS,
    load_geojson,
    load_model_metrics,
)

# ── palette ───────────────────────────────────────────────────────────────────
TEAL   = "#2E75B6"
DARK   = "#1F3864"
AMBER  = "#C6A000"
LIGHT  = "#DCE6F1"
RED    = "#C00000"
GREY   = "#D0D0D0"
GREEN  = "#217346"
PURPLE = "#7B2D8B"
ORANGE = "#E07B00"

PALETTE = [
    TEAL, RED, AMBER, GREEN, PURPLE, ORANGE,
    "#4472C4", "#70AD47", "#ED7D31", "#A5A5A5",
    "#FFC000", "#5B9BD5", "#C55A11", "#8064A2",
    "#9E480E", "#2F5597",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, Arial, sans-serif", size=11),
    hoverlabel=dict(bgcolor="white", font_size=12),
    margin=dict(l=20, r=20, t=45, b=40),
)


# ── shared helpers ────────────────────────────────────────────────────────────
def _add_sensor_boundary(fig: go.Figure, y_frac: float = 0.95) -> go.Figure:
    """Add satellite-data transition marker at 2011.5."""
    fig.add_vline(
        x=2011.5, line_dash="dot", line_color="#888888", line_width=1.2,
    )
    fig.add_annotation(
        x=2011.5,
        y=y_frac,
        xref="x",
        yref="paper",
        text="satellite data change",
        showarrow=False,
        textangle=-90,
        xanchor="left",
        yanchor="middle",
        font=dict(size=9, color="#666666"),
        bgcolor="rgba(255,255,255,0.80)",
        bordercolor="rgba(136,136,136,0.35)",
        borderwidth=1,
        borderpad=2,
    )
    return fig


def _base_layout(**kwargs) -> dict:
    base = PLOTLY_LAYOUT.copy()
    base.update(kwargs)
    return base


# ── Overview tab charts ───────────────────────────────────────────────────────
def make_choropleth(year_df: pd.DataFrame, target: str) -> go.Figure:
    """State choropleth coloured by poverty value."""
    geojson = load_geojson()
    df = year_df.dropna(subset=["geo_state_name", target]).copy()

    fig = go.Figure(go.Choroplethmap(
        geojson=geojson,
        locations=df["geo_state_name"],
        z=df[target],
        featureidkey="properties.shapeName",
        colorscale=[
            [0.0, "#EFF6FF"],
            [0.3, "#93C5FD"],
            [0.6, "#3B82F6"],
            [0.85, AMBER],
            [1.0, RED],
        ],
        zmin=float(df[target].min()),
        zmax=float(df[target].max()),
        colorbar=dict(
            title=dict(text=TARGET_LABELS.get(target, target), side="right"),
            thickness=12, len=0.7, tickfont=dict(size=10),
        ),
        text=df["state"],
        hovertemplate="<b>%{text}</b><br>"
                      + TARGET_LABELS.get(target, target)
                      + ": %{z:.2f}%<extra></extra>",
        marker_opacity=0.85,
        marker_line_width=0.5,
        marker_line_color="white",
    ))
    fig.update_layout(
        map=dict(
            style="carto-positron",
            center=dict(lat=4.0, lon=109.5),
            zoom=4.8,
        ),
        height=340,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=11),
    )
    return fig


def make_ranking_bar(year_df: pd.DataFrame, target: str, selected_state: str) -> go.Figure:
    """Horizontal bar of all 16 states sorted by poverty, selected highlighted."""
    df = year_df.dropna(subset=[target]).sort_values(target, ascending=True)
    colors = [TEAL if s == selected_state else "#A8C8E8" for s in df["state"]]

    fig = go.Figure(go.Bar(
        x=df[target],
        y=df["state"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}" for v in df[target]],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f} pp<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(
            height=340,
            title=dict(text="Higher-poverty states appear at the top", font_size=13),
            xaxis_title=TARGET_LABELS.get(target, target),
            yaxis_title="",
            xaxis=dict(range=[0, df[target].max() * 1.18]),
            showlegend=False,
        )
    )
    return fig


def make_loso_trend(target: str, trend_df: pd.DataFrame) -> go.Figure:
    """Average actual vs predicted LOSO trend with COVID annotation."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_df["year"], y=trend_df["actual"],
        mode="lines+markers",
        name="Official survey average",
        line=dict(color=DARK, width=2.5),
        marker=dict(symbol="square", size=6),
    ))
    fig.add_trace(go.Scatter(
        x=trend_df["year"], y=trend_df["predicted"],
        mode="lines+markers",
        name="Model estimate in state-held-out test",
        line=dict(color=TEAL, width=2.5, dash="dash"),
        marker=dict(symbol="circle", size=6),
    ))
    _add_sensor_boundary(fig)

    # COVID annotation
    covid_row = trend_df[trend_df["year"] == 2020]
    if not covid_row.empty:
        y_covid = float(covid_row["actual"].iloc[0])
        fig.add_annotation(
            x=2020, y=y_covid,
            text="COVID-19<br>spike",
            showarrow=True, arrowhead=2, arrowcolor=RED,
            font=dict(size=9, color=RED),
            ax=-55, ay=-30,
        )

    k = CERTIFIED_KPIS
    if target == "poverty_absolute":
        ann_text = (f"Average error {k['MAE']:.2f} pp  |  Pattern explained {k['R2']:.2f}  |  "
                    f"Ranking agreement {k['Spearman']:.2f}")
    else:
        ann_text = "Headline accuracy values are for absolute poverty only"
    fig.add_annotation(
        text=ann_text,
        xref="paper", yref="paper", x=0.01, y=0.04,
        showarrow=False, font=dict(size=9, color=DARK),
        bgcolor=LIGHT, bordercolor=TEAL, borderwidth=1,
        borderpad=4,
    )
    fig.update_layout(
        **_base_layout(
            height=295,
            title=dict(text="The model follows broad official survey movements", font_size=13),
            xaxis=dict(title="Survey Year", tickvals=SURVEY_YEARS, tickangle=-45),
            yaxis=dict(title=TARGET_LABELS.get(target, "Poverty (%)"), rangemode="tozero"),
            legend=dict(orientation="h", y=1.12, x=0),
        )
    )
    return fig


# ── State Review tab charts ───────────────────────────────────────────────────
def make_state_detail_trend(
    state_loso: pd.DataFrame,
    panel: pd.DataFrame,
    state: str,
    target: str,
) -> go.Figure:
    """State-specific trend: actual survey data + LOSO predicted line."""
    actual = panel[(panel["state"] == state)][["year", target]].dropna().sort_values("year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual["year"], y=actual[target],
        mode="lines+markers",
        name="Official survey values",
        line=dict(color=DARK, width=2.5),
        marker=dict(symbol="square", size=7),
    ))
    if not state_loso.empty:
        fig.add_trace(go.Scatter(
            x=state_loso["year"], y=state_loso["predicted"],
            mode="lines+markers",
            name="Model estimate",
            line=dict(color=TEAL, width=2.2, dash="dash"),
            marker=dict(symbol="circle", size=6),
        ))
    _add_sensor_boundary(fig)
    fig.update_layout(
        **_base_layout(
            height=285,
            title=dict(text=f"{state}: official trend and model estimate", font_size=13),
            xaxis=dict(title="Survey Year", tickvals=SURVEY_YEARS, tickangle=-45),
            yaxis=dict(title=TARGET_LABELS.get(target, "Poverty (%)"), rangemode="tozero"),
            legend=dict(orientation="h", y=1.12, x=0),
        )
    )
    return fig


def make_proxy_bar(row: pd.Series) -> go.Figure:
    """Supporting indicator within-year rank chart for a single state-year."""
    features = [
        ("wmean_ntl_mean_rank_by_year",    "Night-time lights", TEAL),
        ("wmean_evi_mean_rank_by_year",    "Vegetation signal", "#5B9BD5"),
        ("wmean_frac_urban_rank_by_year",  "Urban share",       AMBER),
        ("pop_sum_grid_rank_by_year",      "Population size", "#70AD47"),
    ]
    labels, values, colors = [], [], []
    for col, lbl, color in features:
        if col in row.index and pd.notna(row[col]):
            labels.append(lbl)
            values.append(float(row[col]))
            colors.append(color)

    if not values:
        fig = go.Figure()
        fig.add_annotation(
            text="No supporting-indicator data for this year",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12, color="#999"),
        )
        fig.update_layout(**_base_layout(height=285))
        return fig

    int_ranks = [round(v * 16) for v in values]
    fig = go.Figure(go.Bar(
        x=int_ranks, y=labels, orientation="h",
        marker_color=colors,
        text=[f"#{r} of 16" for r in int_ranks],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: #%{x} of 16<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(
            height=285,
            title=dict(text="How this state compares on supporting indicators", font_size=12),
            xaxis=dict(title="Rank among 16 states (1 = lowest)", range=[0, 20]),
            yaxis_title="",
            showlegend=False,
        )
    )
    return fig


# ── Reliability Check tab charts ──────────────────────────────────────────────
def make_model_comparison() -> go.Figure:
    """Dual horizontal bar: MAE (left) and Spearman (right) for 6 state models."""
    mc = load_model_metrics()
    mc_abs = mc[mc["target"] == "poverty_absolute"].sort_values("loso_mae_pp")
    labels = mc_abs["model_label"].tolist()
    mae    = mc_abs["loso_mae_pp"].tolist()
    spear  = mc_abs["loso_spearman"].tolist()
    best   = MODEL_LABELS.get(PRIMARY_ABSOLUTE_MODEL, PRIMARY_ABSOLUTE_MODEL)

    def _bar_colors(vals_ignored):
        return [TEAL if lbl == best else "#A8C8E8" for lbl in labels]

    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.22,
        subplot_titles=["Prediction error", "Ranking fit"],
    )
    fig.add_trace(go.Bar(
        x=mae, y=labels, orientation="h",
        marker_color=_bar_colors(mae),
        text=[f"{v:.2f}" for v in mae], textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f} pp<extra></extra>",
        name="Average prediction error",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=spear, y=labels, orientation="h",
        marker_color=_bar_colors(spear),
        text=[f"{v:.2f}" for v in spear], textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f}<extra></extra>",
        name="Ranking agreement",
    ), row=1, col=2)

    fig.update_xaxes(range=[0, max(mae) * 1.3], row=1, col=1)
    fig.update_xaxes(range=[0, 1.05], row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(autorange="reversed", showticklabels=False, row=1, col=2)

    fig.update_layout(
        **_base_layout(
            height=320,
            title=dict(text="Selected RF compared with LOSO benchmarks", font_size=13),
            showlegend=False,
            margin=dict(l=160, r=60, t=60, b=40),
        )
    )
    return fig


# ── New charts ────────────────────────────────────────────────────────────────

def make_ntl_scatter(panel: pd.DataFrame, target: str) -> go.Figure:
    """Scatter of NTL brightness vs poverty rate for all state-years, with OLS trendline."""
    df = panel[["state", "year", "wmean_ntl_mean", target]].dropna().copy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["wmean_ntl_mean"],
        y=df[target],
        mode="markers",
        marker=dict(
            color=df["year"],
            colorscale="Viridis",
            size=8,
            colorbar=dict(title="Year", thickness=10, len=0.7),
            line=dict(width=0.5, color="white"),
        ),
        text=df["state"] + " (" + df["year"].astype(str) + ")",
        hovertemplate="<b>%{text}</b><br>Night-time lights: %{x:.2f}<br>"
                      + TARGET_LABELS.get(target, "Poverty") + ": %{y:.2f}%<extra></extra>",
        showlegend=False,
    ))

    x_arr = df["wmean_ntl_mean"].values
    y_arr = df[target].values
    mask = np.isfinite(x_arr) & np.isfinite(y_arr)
    if mask.sum() > 1:
        coef = np.polyfit(x_arr[mask], y_arr[mask], 1)
        xline = np.linspace(x_arr[mask].min(), x_arr[mask].max(), 120)
        fig.add_trace(go.Scatter(
            x=xline, y=np.polyval(coef, xline),
            mode="lines",
            line=dict(color="#888", width=1.5, dash="dot"),
            showlegend=False,
            hoverinfo="skip",
        ))

    fig.update_layout(**_base_layout(
        height=295,
        title=dict(text="Night-time lights are a supporting signal, not a direct poverty measure", font_size=13),
        xaxis=dict(title="Night-time light brightness", zeroline=False),
        yaxis=dict(title=TARGET_LABELS.get(target, "Poverty (%)"), rangemode="tozero"),
    ))
    return fig


def make_delta_bar(panel: pd.DataFrame, target: str, end_year: int) -> go.Figure:
    """Horizontal bar of Δ poverty (end_year − 2002) per state, green=improved, red=worsened."""
    if end_year <= 2002:
        fig = go.Figure()
        fig.add_annotation(
            text="Select a year after 2002 to see poverty change",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12, color="#999"),
        )
        fig.update_layout(**_base_layout(height=295, title=dict(text="Poverty Change since 2002", font_size=13)))
        return fig

    base = panel[panel["year"] == 2002][["state", target]].rename(columns={target: "base"})
    end  = panel[panel["year"] == end_year][["state", target]].rename(columns={target: "end"})
    df = base.merge(end, on="state", how="inner")
    df["delta"] = df["end"] - df["base"]
    df = df.sort_values("delta", ascending=True)

    colors = [GREEN if d < 0 else RED for d in df["delta"]]

    fig = go.Figure(go.Bar(
        x=df["delta"],
        y=df["state"],
        orientation="h",
        marker_color=colors,
        text=[f"{d:+.1f}" for d in df["delta"]],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:+.2f} pp since 2002<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="#888", line_width=1)
    max_abs = df["delta"].abs().max() * 1.25 or 1
    fig.update_layout(**_base_layout(
        height=295,
        title=dict(text="Improvement appears left; worsening appears right", font_size=13),
        xaxis=dict(
            title="Poverty change (pp): left = improved, right = worsened",
            range=[-max_abs, max_abs],
            zeroline=False,
        ),
        yaxis_title="",
        showlegend=False,
    ))
    return fig


def make_multistate_trend(panel: pd.DataFrame, states: list, target: str) -> go.Figure:
    """Overlay actual survey poverty for multiple states + national average reference line."""
    states = states or []

    fig = go.Figure()
    y_values = []

    # National average reference line (always first so it sits behind state lines)
    nat_avg = (
        panel.groupby("year")[target].mean()
        .reset_index()
        .sort_values("year")
        .dropna()
    )
    y_values.extend(nat_avg[target].dropna().tolist())
    fig.add_trace(go.Scatter(
        x=nat_avg["year"], y=nat_avg[target],
        mode="lines",
        name="Malaysia avg",
        line=dict(color=GREY, width=1.5, dash="dot"),
        hovertemplate="<b>Malaysia avg</b><br>%{x}: %{y:.2f}%<extra></extra>",
    ))

    for i, state in enumerate(states):
        actual = panel[panel["state"] == state][["year", target]].dropna().sort_values("year")
        y_values.extend(actual[target].dropna().tolist())
        fig.add_trace(go.Scatter(
            x=actual["year"], y=actual[target],
            mode="lines+markers",
            name=state,
            line=dict(color=PALETTE[i % len(PALETTE)], width=2.2),
            marker=dict(size=6),
            hovertemplate=f"<b>{state}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>",
        ))

    if not states:
        fig.add_annotation(
            text="Use All / Clear or choose states to compare against the Malaysia average.",
            xref="paper", yref="paper", x=0.5, y=0.55,
            showarrow=False, font=dict(size=12, color="#777"),
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor=LIGHT, borderwidth=1, borderpad=6,
        )

    ymax = max(y_values) if y_values else 1
    ymin = min(y_values) if y_values else 0
    yrange = [max(0, ymin - max(0.4, (ymax - ymin) * 0.08)), ymax + max(0.8, ymax * 0.08)]

    _add_sensor_boundary(fig, y_frac=0.52)
    fig.update_layout(**_base_layout(
        height=440,
        title=dict(text="Compare state poverty paths against the Malaysia average", font_size=13),
        xaxis=dict(title="Survey Year", tickvals=SURVEY_YEARS, tickangle=-45),
        yaxis=dict(title=TARGET_LABELS.get(target, "Poverty (%)"), range=yrange, zeroline=False),
        legend=dict(
            orientation="h",
            y=-0.32,
            x=0,
            font=dict(size=9),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="rgba(220,230,241,0.9)",
            borderwidth=1,
            itemwidth=38,
        ),
        margin=dict(l=58, r=22, t=50, b=118),
    ))
    return fig
