from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.certificates import stable_problem_hash
from noetheris.circuits import AND, BoolExpr, build_oracle
from noetheris.cv import cv_diagnostic_certificate
from noetheris.ir import StructuralSystem
from noetheris.qubo import (
    compile_system,
    replay_external_solution,
    solve_exact,
    solve_simulated_annealing,
)


def run_benchmarks(*, small: bool = True) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for name, file_name, problem in (
        ("consensus_ir", "consensus_safety_ir.json", "invariant"),
        ("saga_ir", "saga_failure_ir.json", "invariant"),
        ("threshold_ir", "threshold_policy_ir.json", "threshold"),
        ("pqc_migration_ir", "pqc_migration_ir.json", "migration"),
    ):
        system = StructuralSystem.from_json_file(ROOT / "examples" / "structural_ir" / file_name)
        compiled = compile_system(system, problem)
        for solver_name in ("exact", "anneal"):
            solution = (
                solve_exact(compiled)
                if solver_name == "exact"
                else solve_simulated_annealing(compiled, seed=1337, sweeps=64 if small else 256)
            )
            replay = replay_external_solution(
                compiled,
                solution.assignment,
                reported_energy=solution.energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                solver_metadata={"solver": solver_name, "seed": 1337},
            )
            records.append(
                {
                    "problem_name": name,
                    "problem_hash": compiled.problem_hash,
                    "compiled_model_hash": compiled.compiled_model_hash,
                    "assignment_hash": stable_problem_hash(solution.assignment),
                    "problem_size": len(system.nodes) + len(system.edges),
                    "variable_count": len(compiled.model.variables),
                    "constraint_count": len(compiled.constraints),
                    "solver": solver_name,
                    "seed": 1337,
                    "runtime_seconds": None,
                    "runtime_policy": "canonical_baseline_omits_wall_clock",
                    "energy": solution.energy,
                    "energy_recomputed": replay["energy_recomputed"],
                    "validation_status": replay["status"],
                    "solver_boundary": "local deterministic baseline",
                    "embedding_status": "not_requested",
                    "embedding": None,
                    "residual_risk": None,
                    "oracle_depth_estimate": None,
                    "boundary_leakage": None,
                }
            )
    expr = AND(BoolExpr.var("a"), BoolExpr.var("b"))
    oracle = build_oracle(expr, name="and_policy")
    metrics = oracle.cost_metrics()
    records.append(
        {
            "problem_name": "oracle_and_policy",
            "problem_hash": stable_problem_hash({"truth_table": oracle.truth_table()}),
            "compiled_model_hash": stable_problem_hash(oracle.cost_metrics()),
            "assignment_hash": None,
            "problem_size": metrics["logical_variables"],
            "variable_count": metrics["logical_variables"],
            "constraint_count": 1,
            "solver": "truth_table",
            "seed": 1337,
            "runtime_seconds": None,
            "runtime_policy": "canonical_baseline_omits_wall_clock",
            "energy": 0.0,
            "energy_recomputed": True,
            "validation_status": "truth_table_verified",
            "solver_boundary": "local symbolic oracle",
            "embedding_status": "not_applicable",
            "embedding": None,
            "residual_risk": None,
            "oracle_depth_estimate": metrics["depth_estimate"],
            "boundary_leakage": None,
        }
    )
    cv = cv_diagnostic_certificate(cutoff=8, delta=0.4, grid_cutoff=1, seed=1337)
    records.append(
        {
            "problem_name": "cv_gkp_cutoff_8",
            "problem_hash": stable_problem_hash({"cutoff": 8, "delta": 0.4, "grid_cutoff": 1}),
            "compiled_model_hash": cv["certificate"]["problem_hash"],
            "assignment_hash": None,
            "problem_size": 8,
            "variable_count": 0,
            "constraint_count": 2,
            "solver": "cv_diagnostic",
            "seed": 1337,
            "runtime_seconds": None,
            "runtime_policy": "canonical_baseline_omits_wall_clock",
            "energy": cv["certificate"]["total_energy"],
            "energy_recomputed": True,
            "validation_status": f"certificate_{cv['certificate_status']}",
            "solver_boundary": "local finite-fock diagnostic",
            "embedding_status": "not_applicable",
            "embedding": None,
            "residual_risk": None,
            "oracle_depth_estimate": None,
            "boundary_leakage": cv["diagnostics"]["boundary_population"],
        }
    )
    return {
        "release": "Noetheris v0.1.0 — Structural Quantum Security Kernel",
        "benchmark_scope": "local deterministic baseline",
        "records": records,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    results = ROOT / "benchmarks" / "results"
    results.mkdir(parents=True, exist_ok=True)
    json_path = results / "noetheris_v0_1_baseline.json"
    csv_path = results / "noetheris_v0_1_baseline.csv"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(payload["records"][0].keys()))
        writer.writeheader()
        writer.writerows(payload["records"])


def main() -> None:
    payload = run_benchmarks(small=True)
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
