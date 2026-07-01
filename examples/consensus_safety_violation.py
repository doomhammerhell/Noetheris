from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.annealing import InvariantWeights, search_invariant_violation
from noetheris.graph import StateGraph


def main() -> None:
    graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    weights = InvariantWeights(validity=80.0, invariant=50.0, path=1.0, adversary=2.0)
    result = search_invariant_violation(
        graph,
        max_depth=3,
        weights=weights,
        adversarial_budget=2,
        seed=17,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
