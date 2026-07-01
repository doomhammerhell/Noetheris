from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.circuits import BooleanOracle


def main() -> None:
    with (ROOT / "examples" / "threshold_wallet_policy.json").open(
        "r", encoding="utf-8"
    ) as handle:
        policy = json.load(handle)
    threshold = int(policy["threshold"])
    signers = tuple(policy["signers"])

    def predicate(bits: tuple[int, ...]) -> int:
        return 1 if sum(bits) >= threshold else 0

    oracle = BooleanOracle(signers, predicate, name="threshold_authorized")
    simulation = {
        "".join(str(bit) for bit in key[0]) + f"|{key[1]}": [
            "".join(str(bit) for bit in value[0]),
            value[1],
        ]
        for key, value in oracle.simulate_all().items()
    }
    qiskit_circuit, qiskit_status = oracle.qiskit_export()
    print(
        json.dumps(
            {
                "policy": policy["policy"],
                "symbolic_circuit": oracle.symbolic_circuit().to_text().splitlines(),
                "simulation": simulation,
                "qiskit_available": qiskit_circuit is not None,
                "qiskit_status": qiskit_status,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
