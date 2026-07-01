from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.cv import logarithmic_negativity, negativity, partial_trace


def main() -> None:
    bell = np.zeros(4, dtype=complex)
    bell[0] = 1 / np.sqrt(2)
    bell[3] = 1 / np.sqrt(2)
    rho = np.outer(bell, bell.conj())
    print(
        json.dumps(
            {
                "negativity": negativity(rho, (2, 2), 1),
                "logarithmic_negativity": logarithmic_negativity(rho, (2, 2), 1),
                "reduced_trace": float(np.real(np.trace(partial_trace(rho, (2, 2), (0,))))),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
