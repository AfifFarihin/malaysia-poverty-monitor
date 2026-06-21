"""
Data loading layer for the Dash dashboard.
All paths resolved relative to project root (one level up from this file).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# ── path resolution ───────────────────────────────────────────────────────────
DASH_DIR     = Path(__file__).resolve().parent
PROJECT_ROOT = DASH_DIR.parent              # project root
DATA_DIR     = PROJECT_ROOT / "data"
OUTPUTS_DIR  = PROJECT_ROOT / "outputs"

# ── shared dashboard constants ───────────────────────────────────────────────
SURVEY_YEARS = [2002, 2004, 2007, 2009, 2012, 2014, 2016, 2019, 2020, 2022]

TARGET_LABELS = {
    "poverty_absolute": "Official absolute poverty rate (%)",
    "poverty_relative": "Relative poverty rate (%)",
}

STATE_JOIN_MAP = {
    "Johor":            "Johor",
    "Kedah":            "Kedah",
    "Kelantan":         "Kelantan",
    "Melaka":           "Malacca",
    "Negeri Sembilan":  "Negeri Sembilan",
    "Pahang":           "Pahang",
    "Perak":            "Perak",
    "Perlis":           "Perlis",
    "Pulau Pinang":     "Penang",
    "Sabah":            "Sabah",
    "Sarawak":          "Sarawak",
    "Selangor":         "Selangor",
    "Terengganu":       "Terengganu",
    "W.P. Kuala Lumpur":"Kuala Lumpur",
    "W.P. Labuan":      "Labuan",
    "W.P. Putrajaya":   "Putrajaya",
}

MODEL_LABELS = {
    "rf_current_full":                "Retrospective Random Forest comparator",
    "rf_sensor_safe":                 "Selected sensor-safe Random Forest",
    "current_xgb":                    "Retrospective XGBoost comparator",
    "sensor_safe_xgb":                "XGBoost without sensor-sensitive features",
    "year_only_xgb":                  "Year-only baseline",
    "sensor_safe_elasticnet":         "ElasticNet baseline",
    "sensor_safe_year_dummies_ridge": "Year-dummy baseline",
    "sensor_safe_ridge":              "Ridge baseline",
}

PRIMARY_MODEL_BY_TARGET = {
    "poverty_absolute": "rf_sensor_safe",
    "poverty_relative": "year_only_xgb",
}
PRIMARY_ABSOLUTE_MODEL = PRIMARY_MODEL_BY_TARGET["poverty_absolute"]

# ── KPI constants (from certified metrics) ────────────────────────────────────
# ── data loaders ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_panel() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "state_year_panel_modelready_2002_2022.csv")
    df = df[df["year"].isin(SURVEY_YEARS)].copy()
    df["geo_state_name"] = df["state"].map(STATE_JOIN_MAP)
    return df


@lru_cache(maxsize=1)
def load_geojson() -> dict:
    boundary_path = DATA_DIR / "boundaries" / "malaysia_adm1_geoboundaries.geojson"
    with boundary_path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_loso_preds() -> pd.DataFrame:
    return pd.read_csv(
        OUTPUTS_DIR / "metrics/malaysia_state_loso_fold_predictions.csv"
    )


@lru_cache(maxsize=1)
def load_model_metrics() -> pd.DataFrame:
    df = pd.read_csv(OUTPUTS_DIR / "metrics/malaysia_state_model_comparison.csv")
    df["model_label"] = df["model"].map(MODEL_LABELS).fillna(df["model"])
    return df


def load_certified_kpis() -> dict[str, float]:
    """Load selected absolute-poverty KPIs from the certified comparison table."""
    metrics = load_model_metrics()
    rows = metrics[
        (metrics["target"] == "poverty_absolute")
        & (metrics["model"] == PRIMARY_ABSOLUTE_MODEL)
    ]
    if len(rows) != 1:
        raise RuntimeError(
            "Certified model evidence is missing or ambiguous for "
            f"{PRIMARY_ABSOLUTE_MODEL!r}; regenerate notebook 03 before starting the dashboard."
        )
    row = rows.iloc[0]
    required = ["loso_mae_pp", "loso_rmse", "loso_r2", "loso_spearman"]
    if row[required].isna().any():
        raise RuntimeError("Certified model evidence contains missing KPI values.")
    return {
        "MAE": float(row["loso_mae_pp"]),
        "RMSE": float(row["loso_rmse"]),
        "R2": float(row["loso_r2"]),
        "Spearman": float(row["loso_spearman"]),
    }


CERTIFIED_KPIS = load_certified_kpis()


@lru_cache(maxsize=1)
def load_uncertainty() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / "metrics/malaysia_state_uncertainty_intervals.csv")


@lru_cache(maxsize=1)
def load_rf_factor_importance() -> pd.DataFrame:
    df = pd.read_csv(OUTPUTS_DIR / "metrics/malaysia_state_rf_shap_poverty_absolute.csv")
    plain_names = {
        "year": "Survey year and long-term timing",
        "wmean_ndvi_peak": "Peak vegetation signal",
        "wmean_ntl_highshare": "Share of very bright night-time lights",
        "wmean_ntl_mean_z_by_year": "Night-time light level compared with the same year",
        "wmean_evi_mean": "Average vegetation signal",
        "wmean_ntl_mean": "Average night-time light brightness",
        "wmean_ntl_highshare_z_by_year": "Very bright night lights compared with the same year",
        "wmean_ntl_highshare_rank_by_year": "Night-light rank within the same year",
        "dist_urban_cell_share_thr02": "Urban area share",
        "wmean_frac_urban": "Urban fraction",
    }
    group_names = {
        "year/time": "Timing",
        "vegetation": "Vegetation",
        "nighttime lights": "Night-time lights",
        "urbanisation": "Urbanisation",
        "topography": "Terrain",
        "population": "Population",
    }
    df["plain_feature"] = df["feature"].map(plain_names).fillna(
        df["feature"].str.replace("_", " ").str.title()
    )
    df["plain_group"] = df["feature_group"].map(group_names).fillna(df["feature_group"])
    return df.sort_values("mean_abs_rank")


# ── derived helpers ───────────────────────────────────────────────────────────
def primary_model_for_target(target: str) -> str:
    if target not in PRIMARY_MODEL_BY_TARGET:
        raise ValueError(f"No certified dashboard model is available for target: {target}")
    return PRIMARY_MODEL_BY_TARGET[target]


def panel_for_year(year: int, target: str) -> pd.DataFrame:
    """Return panel filtered to one year, with rank column added."""
    panel = load_panel()
    df = panel[panel["year"] == year].copy()
    df = df.sort_values(target, ascending=False, na_position="last")
    df["rank"] = range(1, len(df) + 1)
    return df


def loso_for_state(state: str, target: str) -> pd.DataFrame:
    """Return LOSO predictions for one state + target using the reviewed state model."""
    loso = load_loso_preds()
    model = primary_model_for_target(target)
    return loso[
        (loso["state"] == state)
        & (loso["target"] == target)
        & (loso["model"] == model)
    ].sort_values("year")


def loso_trend_avg(target: str) -> pd.DataFrame:
    """Return year-averaged actual/predicted across all states using the reviewed state model."""
    loso = load_loso_preds()
    model = primary_model_for_target(target)
    return (
        loso[(loso["model"] == model) & (loso["target"] == target)]
        .groupby("year")[["actual", "predicted"]]
        .mean()
        .reset_index()
        .sort_values("year")
    )


def proxy_row(state: str, year: int) -> pd.Series | None:
    """Return the panel row for a given state+year (or None if missing)."""
    panel = load_panel()
    rows = panel[(panel["state"] == state) & (panel["year"] == year)]
    return rows.iloc[0] if not rows.empty else None


def state_kpis(state: str, year: int, target: str) -> dict:
    """Compute KPI values for the State Review tab cards."""
    panel = load_panel()
    row_now = panel[(panel["state"] == state) & (panel["year"] == year)]
    first_year = panel[panel["state"] == state]["year"].min()
    row_first = panel[(panel["state"] == state) & (panel["year"] == first_year)]

    raw_now = row_now[target].iloc[0] if not row_now.empty else None
    raw_first = row_first[target].iloc[0] if not row_first.empty else None
    poverty_now = float(raw_now) if pd.notna(raw_now) else None
    poverty_first = float(raw_first) if pd.notna(raw_first) else None
    delta = round(poverty_now - poverty_first, 2) if (poverty_now is not None and poverty_first is not None) else None

    # Rank within selected year
    if poverty_now is None:
        rank = None
    else:
        year_df = panel[(panel["year"] == year) & panel[target].notna()].sort_values(target, ascending=False)
        rank_series = year_df.reset_index(drop=True)
        rank_match = rank_series[rank_series["state"] == state]
        rank = int(rank_match.index[0]) + 1 if not rank_match.empty else None

    return {
        "state":   state,
        "poverty": round(poverty_now, 2) if poverty_now is not None else "N/A",
        "rank":    rank,
        "delta":   delta,
        "first_year": int(first_year),
    }


def detail_table_df(year: int, target: str, selected_state: str) -> pd.DataFrame:
    """Build the all-states comparison table for the State Review tab."""
    panel = load_panel()
    loso = load_loso_preds()

    model = primary_model_for_target(target)
    loso_model = loso[
        (loso["model"] == model) & (loso["target"] == target) & (loso["year"] == year)
    ][["state", "actual", "predicted", "abs_error"]].copy()

    df = panel[panel["year"] == year][
        ["state", target, "wmean_ntl_mean_rank_by_year", "wmean_frac_urban_rank_by_year"]
    ].copy()
    df = df.merge(loso_model, on="state", how="left")

    baseline_year = 2019 if year >= 2019 else int(panel["year"].min())
    baseline_col = f"base_{baseline_year}"
    base = panel[panel["year"] == baseline_year][["state", target]].rename(
        columns={target: baseline_col}
    )
    df = df.merge(base, on="state", how="left")
    df["trend"] = df[target] - df[baseline_col]

    df = df.sort_values(target, ascending=False, na_position="last").reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    df["highlight"] = df["state"] == selected_state

    # Convert 0-1 float percentile ranks → 1-16 integer ranks
    for col in ["wmean_ntl_mean_rank_by_year", "wmean_frac_urban_rank_by_year"]:
        if col in df.columns:
            df[col] = (df[col] * 16).round().astype("Int64")

    return df[[
        "rank", "state", target, "actual", "predicted", "abs_error",
        "trend", "wmean_ntl_mean_rank_by_year", "wmean_frac_urban_rank_by_year", "highlight"
    ]].rename(columns={
        target:                         "Poverty (%)",
        "rank":                         "Poverty rank",
        "actual":                       "Official survey",
        "predicted":                    "Model estimate",
        "abs_error":                    "Prediction Gap",
        "trend":                        f"Change since {baseline_year}",
        "wmean_ntl_mean_rank_by_year":  "Night-light Rank",
        "wmean_frac_urban_rank_by_year":"Urbanisation Rank",
    })


# ── precomputed static figures ────────────────────────────────────────────────
def _build_error_heatmap() -> go.Figure:
    """Build the error heat map figure once at startup."""
    loso = load_loso_preds()
    exec_df = loso[
        (loso["model"] == PRIMARY_ABSOLUTE_MODEL) & (loso["target"] == "poverty_absolute")
    ]
    # Order states by 2022 actual poverty (highest at top)
    order = (
        exec_df[exec_df["year"] == 2022]
        .sort_values("actual", ascending=False)["state"]
        .tolist()
    )
    em = (
        exec_df.pivot_table(index="state", columns="year", values="abs_error")
        .reindex(order)
        .reindex(columns=SURVEY_YEARS)
    )
    fig = go.Figure(go.Heatmap(
        z=em.values,
        x=[str(y) for y in SURVEY_YEARS],
        y=em.index.tolist(),
        colorscale="YlOrRd",
        colorbar=dict(title="Prediction gap (pp)", thickness=14),
        hovertemplate="<b>%{y}</b> · %{x}<br>Prediction gap: %{z:.2f} pp<extra></extra>",
        hoverongaps=False,
        xgap=1,
        ygap=1,
    ))
    fig.update_layout(
        xaxis_title="Survey Year",
        yaxis_title="",
        margin=dict(l=140, r=20, t=10, b=40),
        height=420,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=11),
    )
    return fig


def _build_proxy_corr() -> go.Figure:
    """Spearman correlation heatmap: 4 satellite proxies × 3 poverty targets."""
    panel = load_panel()
    proxy_cols = {
        "Night-time lights": "wmean_ntl_mean",
        "Vegetation signal": "wmean_evi_mean",
        "Urban share":       "wmean_frac_urban",
        "Population": "pop_sum_grid",
    }
    target_cols = {
        "Absolute":  "poverty_absolute",
        "Relative":  "poverty_relative",
    }
    avail_p = {k: v for k, v in proxy_cols.items() if v in panel.columns}
    avail_t = {k: v for k, v in target_cols.items() if v in panel.columns}

    rows_lbl = list(avail_p.keys())
    cols_lbl = list(avail_t.keys())
    z, text = [], []
    for p_col in avail_p.values():
        row_z, row_t = [], []
        for t_col in avail_t.values():
            sub = panel[[p_col, t_col]].dropna()
            r = sub[p_col].corr(sub[t_col], method="spearman") if len(sub) > 2 else float("nan")
            row_z.append(r)
            row_t.append(f"{r:.2f}" if pd.notna(r) else "")
        z.append(row_z)
        text.append(row_t)

    fig = go.Figure(go.Heatmap(
        z=z, x=cols_lbl, y=rows_lbl,
        text=text, texttemplate="%{text}",
        textfont=dict(size=13),
        colorscale="RdBu_r", zmin=-1, zmax=1,
        colorbar=dict(title="Ranking link", thickness=14),
        hovertemplate="<b>%{y} vs %{x}</b><br>Ranking link: %{z:.3f}<extra></extra>",
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        title="How strongly each supporting indicator follows poverty rankings",
        height=280,
        margin=dict(l=110, r=60, t=50, b=40),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=12),
    )
    return fig


# Precomputed at import time
FIGURE_ERROR_HEATMAP: go.Figure = _build_error_heatmap()
FIGURE_PROXY_CORR:    go.Figure = _build_proxy_corr()
