"""
Dash callbacks — all @callback decorators.
Uses dash.callback (Dash 2+) so no circular app import is needed.
"""
from __future__ import annotations

import pandas as pd
from dash import Input, Output, State, callback, html, no_update

from . import charts as C
from . import data as D


def register_callbacks() -> None:
    """Register all callbacks. Called once from app.py after layout is set."""

    # ── Overview Tab ─────────────────────────────────────────────────────────

    @callback(
        Output("map-graph", "figure"),
        Input("year-dd", "value"),
        Input("target-radio", "value"),
    )
    def update_map(year, target):
        year_df = D.panel_for_year(int(year), target)
        return C.make_choropleth(year_df, target)

    @callback(
        Output("ranking-bar", "figure"),
        Input("year-dd", "value"),
        Input("target-radio", "value"),
        Input("state-dd", "value"),
    )
    def update_ranking(year, target, state):
        year_df = D.panel_for_year(int(year), target)
        return C.make_ranking_bar(year_df, target, state)

    @callback(
        Output("overview-trend", "figure"),
        Input("target-radio", "value"),
    )
    def update_overview_trend(target):
        trend_df = D.loso_trend_avg(target)
        return C.make_loso_trend(target, trend_df)

    @callback(
        Output("factor-list", "children"),
        Output("shap-note",  "children"),
        Output("shap-title", "children"),
        Input("target-radio", "value"),
    )
    def update_shap(target):
        def factor_cards():
            factors = D.load_rf_factor_importance().head(6)
            items = []
            for _, row in factors.iterrows():
                share = float(row["importance_share"]) * 100
                items.append(html.Div([
                    html.Div(row["plain_feature"], style={
                        "fontWeight": "700",
                        "color": "#1F3864",
                        "fontSize": "0.78rem",
                    }),
                    html.Div(f"{row['plain_group']} - about {share:.0f}% of model explanation", style={
                        "color": "#556",
                        "fontSize": "0.72rem",
                    }),
                ], style={
                    "padding": "7px 9px",
                    "border": "1px solid #DCE6F1",
                    "borderRadius": "7px",
                    "background": "#FAFBFC",
                    "marginBottom": "6px",
                }))
            return items

        if target == "poverty_relative":
            note = (
                "Relative poverty is mostly explained by time trends in this dataset. "
                "The factor list below is shown only as reference for the selected absolute-poverty model."
            )
            return factor_cards(), note, "Reference: strongest factors for the selected absolute-poverty model"
        note = "These factors describe how the selected model uses supporting indicators. They are not causal proof."
        return factor_cards(), note, "Main factors behind the selected absolute-poverty model"

    @callback(
        Output("ntl-scatter", "figure"),
        Input("target-radio", "value"),
    )
    def update_ntl_scatter(target):
        return C.make_ntl_scatter(D.load_panel(), target)

    @callback(
        Output("delta-bar", "figure"),
        Input("target-radio", "value"),
        Input("year-dd", "value"),
    )
    def update_delta_bar(target, year):
        return C.make_delta_bar(D.load_panel(), target, int(year))

    # ── State Review tab ──────────────────────────────────────────────────────

    @callback(
        Output("kpi-state-val",      "children"),
        Output("kpi-poverty-val",    "children"),
        Output("kpi-poverty-lbl",    "children"),
        Output("kpi-rank-val",       "children"),
        Output("kpi-delta-val",      "children"),
        Output("kpi-delta-lbl",      "children"),
        Output("kpi-recovery-val",   "children"),
        Output("kpi-recovery-lbl",   "children"),
        Output("kpi-recovery-val",   "style"),
        Input("state-dd",     "value"),
        Input("year-dd",      "value"),
        Input("target-radio", "value"),
    )
    def update_kpis(state, year, target):
        year = int(year)
        kpis = D.state_kpis(state, year, target)
        poverty_lbl = D.TARGET_LABELS.get(target, "Poverty (%)")
        poverty_val = f"{kpis['poverty']:.2f} pp" if isinstance(kpis["poverty"], float) else "N/A"
        rank_val    = f"#{kpis['rank']} / 16" if kpis["rank"] else "N/A"
        if kpis["delta"] is not None:
            sign    = "+" if kpis["delta"] >= 0 else ""
            delta_v = f"{sign}{kpis['delta']:.2f} pp"
            delta_l = f"Change since {kpis['first_year']}"
        else:
            delta_v, delta_l = "N/A", f"Change since {kpis['first_year']}"

        # Recovery badge: change from 2020 COVID peak to selected year
        panel = D.load_panel()
        row_2020 = panel[(panel["state"] == state) & (panel["year"] == 2020)]
        row_now  = panel[(panel["state"] == state) & (panel["year"] == year)]
        if not row_2020.empty and not row_now.empty and year != 2020:
            p2020_raw = row_2020[target].iloc[0]
            p_now_raw = row_now[target].iloc[0]
            if pd.notna(p2020_raw) and pd.notna(p_now_raw):
                p2020 = float(p2020_raw)
                p_now = float(p_now_raw)
                state_chg = p_now - p2020
                nat_2020 = panel[panel["year"] == 2020][target].mean()
                nat_now  = panel[panel["year"] == year][target].mean()
                nat_chg  = nat_now - nat_2020
                s1 = "+" if state_chg >= 0 else ""
                s2 = "+" if nat_chg   >= 0 else ""
                recovery_val = f"{s1}{state_chg:.2f} pp"
                recovery_lbl = f"Since 2020 peak (nat. avg {s2}{nat_chg:.2f} pp)"
            else:
                recovery_val = "N/A"
                recovery_lbl = "Since 2020 COVID peak"
        else:
            recovery_val = "N/A"
            recovery_lbl = "Since 2020 COVID peak"

        # Recovery badge colour: green/teal = improved (negative), red = worsened (positive)
        base_style = {"fontSize": "1.3rem", "fontWeight": "700"}
        if recovery_val == "N/A":
            rec_style = {**base_style, "color": "#888"}
        else:
            try:
                rec_num = float(recovery_val.replace(" pp", "").replace("+", ""))
                rec_style = {**base_style, "color": "#C00000" if rec_num > 0 else "#2E75B6"}
            except ValueError:
                rec_style = {**base_style, "color": "#2E75B6"}

        return (state, poverty_val, poverty_lbl, rank_val,
                delta_v, delta_l, recovery_val, recovery_lbl, rec_style)

    @callback(
        Output("state-recommendation", "children"),
        Input("state-dd",     "value"),
        Input("year-dd",      "value"),
        Input("target-radio", "value"),
    )
    def update_state_recommendation(state, year, target):
        year = int(year)
        kpis = D.state_kpis(state, year, target)
        poverty = kpis["poverty"]
        rank = kpis["rank"]
        delta = kpis["delta"]

        if poverty == "N/A" or rank is None:
            message = f"No complete poverty record is available for {state} in {year}."
            caution = "Use another survey year or state for a complete review."
        else:
            if rank <= 3:
                position = "in the higher observed poverty group"
            elif rank <= 8:
                position = "in the middle observed poverty range"
            else:
                position = "in the lower observed poverty group"

            if delta is None:
                direction = "Long-term change is not available for this selection."
            elif delta > 1:
                direction = f"Poverty is {delta:.1f} percentage points higher than the first survey year in this panel."
            elif delta < -1:
                direction = f"Poverty is {abs(delta):.1f} percentage points lower than the first survey year in this panel."
            else:
                direction = "Long-term poverty is broadly stable compared with the first survey year in this panel."

            message = (
                f"{state} is {position} in {year}, ranked #{rank} of 16 for the selected poverty measure. "
                f"{direction} This descriptive signal can help users decide where to investigate further, "
                f"but it does not determine need, eligibility, or resource allocation."
            )
            caution = (
                "Confirm any policy or resource decision with current DOSM releases, local evidence, "
                "and an appropriate needs assessment."
            )

        return html.Div([
            html.Div("Suggested stakeholder use", style={
                "fontSize": "0.82rem",
                "fontWeight": "700",
                "color": "#1F3864",
                "marginBottom": "4px",
            }),
            html.Div(message, style={
                "fontSize": "0.82rem",
                "color": "#445",
                "lineHeight": "1.35",
            }),
            html.Div(caution, style={
                "fontSize": "0.74rem",
                "color": "#667",
                "lineHeight": "1.3",
                "marginTop": "6px",
                "paddingTop": "6px",
                "borderTop": "1px solid #E6EEF7",
            }),
        ], style={
            "background": "white",
            "borderLeft": "5px solid #2E75B6",
            "border": "1px solid #DCE6F1",
            "borderRadius": "10px",
            "padding": "12px 16px",
            "marginBottom": "14px",
            "boxShadow": "0 .125rem .25rem rgba(0,0,0,.075)",
        })

    @callback(
        Output("compare-states-dd", "value"),
        Input("compare-toggle-btn", "n_clicks"),
        State("compare-states-dd", "value"),
        prevent_initial_call=True,
    )
    def toggle_compare_states(_, current_states):
        all_states = sorted(D.STATE_JOIN_MAP.keys())
        current_states = current_states or []
        if set(current_states) == set(all_states):
            return []
        return all_states

    @callback(
        Output("detail-trend", "figure"),
        Input("compare-states-dd", "value"),
        Input("target-radio",      "value"),
    )
    def update_detail_trend(states, target):
        if states is None:
            return no_update
        return C.make_multistate_trend(D.load_panel(), states, target)

    @callback(
        Output("proxy-bar", "figure"),
        Input("state-dd", "value"),
        Input("year-dd",  "value"),
    )
    def update_proxy(state, year):
        row = D.proxy_row(state, int(year))
        if row is None:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(text=f"No data for {state} / {year}",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False, font=dict(size=12))
            return fig
        return C.make_proxy_bar(row)

    @callback(
        Output("detail-table", "columns"),
        Output("detail-table", "data"),
        Output("detail-table", "style_data_conditional"),
        Input("year-dd",      "value"),
        Input("target-radio", "value"),
        Input("state-dd",     "value"),
    )
    def update_detail_table(year, target, state):
        df = D.detail_table_df(int(year), target, state)
        highlight = df["highlight"].tolist()
        display_df = df.drop(columns=["highlight"])

        columns = [{"name": c, "id": c} for c in display_df.columns]
        data    = display_df.round(2).to_dict("records")

        LIGHT = "#DCE6F1"
        TEAL  = "#2E75B6"
        style_cond = [
            {"if": {"row_index": "odd"}, "backgroundColor": "#FAFBFC"},
        ]
        for i, is_hl in enumerate(highlight):
            if is_hl:
                style_cond.append({
                    "if": {"row_index": i},
                    "backgroundColor": LIGHT,
                    "fontWeight":      "600",
                    "color":           TEAL,
                })
        return columns, data, style_cond
