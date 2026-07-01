from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.cv import commutator_boundary_profile, restricted_commutator_error


def main() -> None:
    cutoff = 8
    print(
        json.dumps(
            {
                "cutoff": cutoff,
                "commutator_boundary_profile": commutator_boundary_profile(cutoff),
                "restricted_error_m4": restricted_commutator_error(cutoff, 4),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
