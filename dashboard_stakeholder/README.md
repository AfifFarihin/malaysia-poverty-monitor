# Stakeholder Dashboard

The Dash application presents the project's certified state-level artifacts without retraining models at runtime.

## Run

From the repository root:

```powershell
uv sync --extra dashboard
uv run python -m dashboard_stakeholder.app
```

Open `http://127.0.0.1:8051`.

## Views

| View | Purpose |
|---|---|
| Overview | National trends, state rankings, supporting factors, and cautious stakeholder uses. |
| State Review | State-specific trends, model estimates, indicator ranks, and comparisons. |
| Reliability Check | Model benchmarks, uncertainty, large prediction gaps, and indicator relationships. |

The dashboard supports monitoring and research. It does not replace official DOSM releases, local evidence, or formal resource-allocation processes.
