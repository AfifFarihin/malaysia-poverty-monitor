# Run Guide

## Supported Environment

- Windows, macOS, or Linux
- Python 3.11
- `uv` 0.8 or newer

From the repository root:

```powershell
uv sync --extra dashboard --extra notebooks --group dev
```

The dependency definitions in `pyproject.toml` are authoritative.

## Dashboard

```powershell
uv run python -m dashboard_stakeholder.app
```

Open `http://127.0.0.1:8051` and review the Overview, State Review, and Reliability Check tabs.

## Notebook Workflow

```powershell
uv run jupyter lab
```

Run the notebooks in numeric order. Notebook 00 can retrieve fresh DOSM labels and falls back to the retained raw CSV when the network is unavailable. Later notebooks validate the retained feature panel, regenerate model evidence, and verify the dashboard contract.

For a non-interactive end-to-end run:

```powershell
uv run python scripts/run_notebooks.py --write
```

## Optional Earth Engine Configuration

The included notebooks and dashboard do not require Earth Engine credentials. The final feature panel is retained because a clean raster extraction depends on an authorized Earth Engine account and upstream collection availability.

The original raster extraction implementation is not included in this repository. For separate extraction work, use the current Earth Engine SDK and provider documentation, copy `setup/local_reproducibility_config.example.env` to `.env`, and fill in your own project and credential values. Never commit `.env`, service-account JSON, tokens, or private key files.

## Checks

```powershell
uv run ruff check dashboard_stakeholder scripts tests
uv run python scripts/verify_lineage.py
uv run pip-audit
uv run pytest -q
```

Headline geographic metrics are recorded in `outputs/metrics/malaysia_state_model_comparison.csv`; the separate rolling-origin future-year check is recorded in `outputs/metrics/malaysia_state_temporal_backtest.csv`. Small XGBoost differences can occur across operating systems and binary builds; the deterministic selection rule resolves ties consistently.
