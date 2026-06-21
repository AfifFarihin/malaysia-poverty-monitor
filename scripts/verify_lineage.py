"""Verify retained source and derived-panel checksums against provenance metadata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PATH = ROOT / "data" / "provenance" / "malaysia_dosm_poverty_provenance.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    checks = {
        provenance["raw_file"]: provenance["raw_sha256"],
        provenance["clean_file"]: provenance["clean_sha256"],
        provenance["model_ready_panel"]: provenance["panel_sha256"],
    }
    failures = []
    for relative_path, expected in checks.items():
        path = ROOT / relative_path
        actual = sha256(path)
        if actual != expected:
            failures.append(f"{relative_path}: expected {expected}, got {actual}")
        else:
            print(f"PASS {relative_path}")
    if failures:
        raise SystemExit("Lineage verification failed:\n" + "\n".join(failures))


if __name__ == "__main__":
    main()
