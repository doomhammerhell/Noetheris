from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.cv import cv_diagnostic_certificate


def main() -> None:
    print(
        json.dumps(
            cv_diagnostic_certificate(cutoff=10, delta=0.35, grid_cutoff=2, seed=2026),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
