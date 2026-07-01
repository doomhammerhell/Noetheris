from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.migration import MigrationGraph, optimize_migration_plan


def main() -> None:
    graph = MigrationGraph.from_json_file(ROOT / "examples" / "pqc_migration_graph.json")
    plan = optimize_migration_plan(graph, seed=2026)
    print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
