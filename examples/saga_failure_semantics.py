from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.ir import StructuralSystem
from noetheris.qubo import compile_invariant_search_to_qubo, explain_solution, solve_exact


def main() -> None:
    system = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "saga_failure_ir.json"
    )
    compiled = compile_invariant_search_to_qubo(system)
    solution = solve_exact(compiled)
    print(json.dumps(explain_solution(compiled, solution), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
