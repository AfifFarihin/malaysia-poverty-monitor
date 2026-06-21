"""Execute the ordered notebook workflow for local verification and CI."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    "00_dosm_raw_to_labels.ipynb",
    "01_malaysia_data_preparation.ipynb",
    "02_malaysia_spatial_features.ipynb",
    "03_model_training_evaluation.ipynb",
    "04_dashboard_artifacts.ipynb",
]
SMOKE_NOTEBOOKS = [
    "01_malaysia_data_preparation.ipynb",
    "02_malaysia_spatial_features.ipynb",
    "04_dashboard_artifacts.ipynb",
]


def execute_notebook(name: str, *, write: bool) -> None:
    path = ROOT / "notebooks" / name
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=1200,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    if write:
        nbformat.write(notebook, path)
    print(f"PASS {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Skip network and model notebooks.")
    parser.add_argument("--write", action="store_true", help="Save executed outputs in place.")
    args = parser.parse_args()
    selected = SMOKE_NOTEBOOKS if args.smoke else NOTEBOOKS
    for name in selected:
        execute_notebook(name, write=args.write)


if __name__ == "__main__":
    main()
