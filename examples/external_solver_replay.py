from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.ir import StructuralSystem
from noetheris.qubo import external_solver_replay_artifact, compile_system, solve_exact


def main() -> None:
    system = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "consensus_safety_ir.json"
    )
    compiled = compile_system(system, system.problem_type)
    solution = solve_exact(compiled)
    assignment = dict(solution.assignment)
    first_variable = compiled.model.variables[0]

    accepted = external_solver_replay_artifact(
        compiled,
        assignment,
        reported_energy=solution.energy,
        problem_hash=compiled.problem_hash,
        compiled_model_hash=compiled.compiled_model_hash,
        solver_metadata={
            "solver": "local_exact_reference",
            "credential_required": False,
            "sample_source": "deterministic_example",
        },
        embedding_metadata={
            "embedding_status": "not_requested",
            "embedding": None,
        },
        candidate_id="accepted-local-reference",
    )
    rejected = [
        _case(
            "problem_hash_mismatch",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=solution.energy,
                problem_hash="sha256:wrong-problem",
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-problem-hash",
            ),
        ),
        _case(
            "compiled_model_hash_mismatch",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=solution.energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash="sha256:wrong-compiled-model",
                candidate_id="rejected-compiled-model-hash",
            ),
        ),
        _case(
            "missing_variables",
            external_solver_replay_artifact(
                compiled,
                {
                    variable: value
                    for variable, value in assignment.items()
                    if variable != first_variable
                },
                reported_energy=solution.energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-missing-variable",
            ),
        ),
        _case(
            "unknown_variables",
            external_solver_replay_artifact(
                compiled,
                {**assignment, "outside_compiled_domain": True},
                reported_energy=solution.energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-unknown-variable",
            ),
        ),
        _case(
            "energy_mismatch",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=solution.energy + 1.0,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-energy-mismatch",
            ),
        ),
        _case(
            "malformed_metadata",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=solution.energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                solver_metadata="not-a-mapping",  # type: ignore[arg-type]
                embedding_metadata="not-a-mapping",  # type: ignore[arg-type]
                candidate_id="rejected-malformed-metadata",
            ),
        ),
    ]
    print(
        json.dumps(
            {
                "example": "external_solver_replay",
                "problem_hash": compiled.problem_hash,
                "compiled_model_hash": compiled.compiled_model_hash,
                "credential_required": False,
                "verification_authority": "noetheris.local_replay",
                "accepted_candidate": accepted,
                "rejected_candidates": rejected,
            },
            indent=2,
            sort_keys=True,
        )
    )


def _case(name: str, artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "case": name,
        "status": artifact["status"],
        "reason_codes": [
            reason["code"] for reason in artifact["rejection_reasons"]
        ],
        "artifact": artifact,
    }


if __name__ == "__main__":
    main()
