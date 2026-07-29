from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.backends import export_qubo_to_dwave, ocean_bqm_parity_report
from noetheris.ir import StructuralSystem
from noetheris.qubo import compile_system, replay_external_solution, solve_exact


def main() -> None:
    system = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "consensus_safety_ir.json"
    )
    compiled = compile_system(system, system.problem_type)
    solution = solve_exact(compiled)
    exported = export_qubo_to_dwave(compiled.model)
    replay = replay_external_solution(
        compiled,
        solution.assignment,
        reported_energy=solution.energy,
        problem_hash=compiled.problem_hash,
        compiled_model_hash=compiled.compiled_model_hash,
        solver_metadata={
            "adapter": "noetheris.backends.export_qubo_to_dwave",
            "candidate_source": "local_exact_reference",
            "credential_required": False,
        },
        embedding_metadata={
            "embedding_status": "not_requested",
            "embedding": None,
        },
    )
    ocean_bqm_report = ocean_bqm_parity_report(
        compiled.model,
        assignments=(solution.assignment,),
    )
    print(
        json.dumps(
            {
                "example": "dwave_ocean_exchange",
                "problem_type": compiled.problem_type,
                "problem_hash": compiled.problem_hash,
                "compiled_model_hash": compiled.compiled_model_hash,
                "exchange": exported["exchange"],
                "dwave_status": exported["status"],
                "bqm_summary": exported["bqm_summary"],
                "ocean_bqm_report": ocean_bqm_report,
                "local_solution": {
                    "assignment": solution.assignment,
                    "energy": solution.energy,
                },
                "replay": replay,
                "credential_required": False,
                "trust_boundary": (
                    "Ocean/D-Wave artifacts are export artifacts; Noetheris accepts "
                    "a solver candidate only after deterministic local replay."
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
