from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.annealing import search_invariant_violation
from noetheris.graph import StateGraph


def main() -> None:
    graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    result = search_invariant_violation(
        graph,
        max_depth=3,
        adversarial_budget=2,
        seed=2026,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
