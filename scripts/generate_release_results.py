from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "python"))

from benchmarks.run_benchmarks import run_benchmarks
from noetheris.annealing import search_invariant_violation
from noetheris.backends import qubo_exchange_payload
from noetheris.circuits import AND, BoolExpr, build_oracle, grid_search_qaoa_p1
from noetheris.cv import cv_diagnostic_certificate
from noetheris.graph import StateGraph
from noetheris.ir import StructuralSystem
from noetheris.migration import MigrationGraph, optimize_migration_plan
from noetheris.qubo import (
    compile_system,
    explain_solution,
    replay_external_solution,
    solve_exact,
)


RESULTS = ROOT / "docs" / "results"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, Any]] = []

    consensus_graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    invariant = search_invariant_violation(consensus_graph, max_depth=3, seed=2026)
    _write("invariant_witness.json", invariant.to_dict(), artifacts)

    structural = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "consensus_safety_ir.json"
    )
    compiled = compile_system(structural, "invariant")
    solution = solve_exact(compiled)
    _write(
        "compiled_qubo_solution.json",
        {
            "compiled": compiled.to_dict(),
            "solution": {
                "assignment": solution.assignment,
                "energy": solution.energy,
            },
            "explanation": explain_solution(compiled, solution),
            "dwave_exchange": qubo_exchange_payload(compiled.model),
            "external_sample_replay": replay_external_solution(
                compiled,
                solution.assignment,
                reported_energy=solution.energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                solver_metadata={"source": "local_exact_solver"},
            ),
        },
        artifacts,
    )

    migration_graph = MigrationGraph.from_json_file(ROOT / "examples" / "pqc_migration_graph.json")
    migration = optimize_migration_plan(migration_graph, seed=2026)
    _write("pqc_migration_plan.json", migration.to_dict(), artifacts)

    expression = AND(BoolExpr.var("a"), BoolExpr.var("b"))
    oracle = build_oracle(expression, name="and_policy")
    _write(
        "oracle_truth_table.json",
        {
            "expression": "a AND b",
            "truth_table": oracle.truth_table(),
            "metrics": oracle.cost_metrics(),
            "reversibility_check": oracle.reversibility_check(),
            "qasm_like": oracle.qasm_like(),
        },
        artifacts,
    )

    qaoa = grid_search_qaoa_p1(
        invariant.qubo,
        gamma_values=(0.0, 0.39269908169872414, 0.7853981633974483),
        beta_values=(0.0, 0.39269908169872414, 0.7853981633974483),
    )
    _write(
        "qaoa_hamiltonian_report.json",
        {
            "source": "consensus invariant QUBO",
            "ising": invariant.qubo.to_ising().to_dict(),
            "qaoa_p1": qaoa.to_dict(),
            "interpretation": "exact statevector check for a tiny local model; no hardware-performance claim",
        },
        artifacts,
    )

    _write(
        "cv_gkp_diagnostic_certificate.json",
        cv_diagnostic_certificate(cutoff=10, delta=0.35, grid_cutoff=2, seed=2026),
        artifacts,
    )

    _write("benchmark_report.json", run_benchmarks(small=True), artifacts)
    _write(
        "release_evidence_index.json",
        {
            "release": "Noetheris v0.1.0 — Structural Quantum Security Kernel",
            "scope": "deterministic release evidence",
            "regenerate": "python3 scripts/generate_release_results.py",
            "artifacts": artifacts,
        },
        [],
    )


def _write(name: str, payload: dict[str, Any], artifacts: list[dict[str, Any]]) -> None:
    path = RESULTS / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifacts.append(
        {
            "file": f"docs/results/{name}",
            "bytes": path.stat().st_size,
        }
    )


if __name__ == "__main__":
    main()
