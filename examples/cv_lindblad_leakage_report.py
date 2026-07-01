from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.cv import leakage_report, number, photon_loss_channel, solve_lindblad


def main() -> None:
    cutoff = 5
    rho0 = np.zeros((cutoff, cutoff), dtype=complex)
    rho0[3, 3] = 1.0
    evolved = solve_lindblad(
        number(cutoff),
        rho0,
        (photon_loss_channel(cutoff, 0.1),),
        dt=0.01,
        steps=20,
    )
    print(json.dumps(leakage_report(evolved, cutoff), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
