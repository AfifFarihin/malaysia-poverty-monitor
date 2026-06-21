import json
from pathlib import Path

import pandas as pd
import pytest

from dashboard_stakeholder.data import (
    STATE_JOIN_MAP,
    detail_table_df,
    load_certified_kpis,
    load_geojson,
)

ROOT = Path(__file__).resolve().parents[1]
SURVEY_YEARS = [2002, 2004, 2007, 2009, 2012, 2014, 2016, 2019, 2020, 2022]


def test_model_ready_panel_contract() -> None:
    panel = pd.read_csv(ROOT / "data/state_year_panel_modelready_2002_2022.csv")

    assert len(panel) == 158
    assert panel["state_key"].nunique() == 16
    assert sorted(panel["year"].unique().tolist()) == SURVEY_YEARS
    assert panel["poverty_absolute"].notna().sum() == 157


def test_selected_model_metrics_are_certified() -> None:
    metrics = pd.read_csv(ROOT / "outputs/metrics/malaysia_state_model_comparison.csv")
    promotion = json.loads(
        (ROOT / "outputs/qa/malaysia_state_model_promotion.json").read_text(encoding="utf-8")
    )
    eligible = metrics[
        (metrics["target"] == "poverty_absolute")
        & (metrics["feature_policy"] == "sensor_safe")
    ].sort_values(
        ["loso_mae_pp", "loso_spearman", "model"],
        ascending=[True, False, True],
    )

    assert promotion["selected_model"] == eligible.iloc[0]["model"]
    assert promotion["manual_promotion_review_status"] == "not_applicable_deterministic_rule"
    assert promotion["selected_absolute"]["feature_policy"] == "sensor_safe"


def test_boundary_names_cover_all_dashboard_states() -> None:
    geojson = load_geojson()
    boundary_names = {feature["properties"]["shapeName"] for feature in geojson["features"]}

    assert len(geojson["features"]) == 16
    assert set(STATE_JOIN_MAP.values()) == boundary_names


def test_example_environment_contains_no_credentials() -> None:
    text = (ROOT / "setup/local_reproducibility_config.example.env").read_text(
        encoding="utf-8"
    )

    assert "EE_PROJECT_ID=your-google-cloud-project-id" in text
    assert "GOOGLE_APPLICATION_CREDENTIALS=" in text
    assert "EE_SERVICE_ACCOUNT_EMAIL=" in text


def test_qa_contract_is_valid_json() -> None:
    contract = json.loads(
        (ROOT / "outputs/qa/dashboard_artifact_contract.json").read_text(encoding="utf-8")
    )
    assert contract["all_present"] is True
    paths = {artifact["path"] for artifact in contract["artifacts"]}
    assert "data/boundaries/malaysia_adm1_geoboundaries.geojson" in paths


def test_temporal_backtest_uses_only_prior_years() -> None:
    temporal = pd.read_csv(ROOT / "outputs/metrics/malaysia_state_temporal_backtest.csv")

    assert not temporal.empty
    assert (temporal["train_end_year"] < temporal["year"]).all()
    assert temporal["model"].nunique() == 1


def test_detail_table_uses_truthful_baseline_label() -> None:
    early = detail_table_df(2012, "poverty_absolute", "Johor")
    recent = detail_table_df(2022, "poverty_absolute", "Johor")

    assert "Change since 2002" in early.columns
    assert "Change since 2019" in recent.columns


def test_certified_kpis_do_not_fall_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dashboard_stakeholder.data.load_model_metrics",
        lambda: pd.DataFrame(columns=["target", "model"]),
    )

    with pytest.raises(RuntimeError, match="Certified model evidence"):
        load_certified_kpis()
