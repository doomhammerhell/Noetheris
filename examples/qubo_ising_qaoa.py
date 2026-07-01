from __future__ import annotations

import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.annealing import search_invariant_violation
from noetheris.circuits import grid_search_qaoa_p1
from noetheris.graph import StateGraph


def main() -> None:
    graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    invariant_result = search_invariant_violation(graph, max_depth=3, seed=2026)
    qubo = invariant_result.qubo
    ising = qubo.to_ising()
    qaoa = grid_search_qaoa_p1(
        qubo,
        gamma_values=(0.0, math.pi / 8.0, math.pi / 4.0, 3.0 * math.pi / 8.0),
        beta_values=(0.0, math.pi / 8.0, math.pi / 4.0),
    )
    print(
        json.dumps(
            {
                "source_algorithm": "invariant_annealing_search",
                "qubo_solution_energy": invariant_result.energy,
                "ising": ising.to_dict(),
                "qaoa_p1": qaoa.to_dict(),
                "interpretation": (
                    "exact local statevector simulation for a tiny QUBO; "
                    "not a hardware performance claim"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
