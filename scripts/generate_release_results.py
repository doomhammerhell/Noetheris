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
    external_solver_replay_artifact,
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
    exchange = qubo_exchange_payload(compiled.model)
    sample_replay = replay_external_solution(
        compiled,
        solution.assignment,
        reported_energy=solution.energy,
        problem_hash=compiled.problem_hash,
        compiled_model_hash=compiled.compiled_model_hash,
        solver_metadata={"source": "local_exact_solver"},
    )
    replay_examples = _external_replay_examples(
        compiled, solution.assignment, solution.energy
    )
    _write(
        "compiled_qubo_solution.json",
        {
            "compiled": compiled.to_dict(),
            "solution": {
                "assignment": solution.assignment,
                "energy": solution.energy,
            },
            "explanation": explain_solution(compiled, solution),
            "dwave_exchange": exchange,
            "external_sample_replay": sample_replay,
        },
        artifacts,
    )
    _write(
        "external_solver_replay_examples.json",
        replay_examples,
        artifacts,
    )
    _write(
        "solver_boundary_evidence.json",
        _solver_boundary_evidence(compiled, exchange, sample_replay, replay_examples),
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
            "schema": "noetheris.release_evidence_index.v1",
            "release": "Noetheris v0.1.0 — Structural Quantum Security Kernel",
            "scope": "deterministic release evidence",
            "roadmap_scope": "v0.2 solver-boundary evidence included",
            "regenerate": "python3 scripts/generate_release_results.py",
            "artifacts": artifacts,
        },
        [],
    )


def _write(name: str, payload: dict[str, Any], artifacts: list[dict[str, Any]]) -> None:
    path = RESULTS / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifacts.append(
        _artifact_index_entry(
            payload,
            file=f"docs/results/{name}",
            byte_count=path.stat().st_size,
        )
    )


def _artifact_index_entry(
    payload: dict[str, Any],
    *,
    file: str,
    byte_count: int,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "file": file,
        "bytes": byte_count,
    }
    if "schema" in payload:
        entry["schema"] = payload["schema"]
    if "scope" in payload:
        entry["scope"] = payload["scope"]
    return entry


def _solver_boundary_evidence(
    compiled: Any,
    exchange: dict[str, Any],
    replay: dict[str, Any],
    replay_examples: dict[str, Any],
) -> dict[str, Any]:
    reason_codes = sorted(
        {
            reason_code
            for candidate in replay_examples["rejected_candidates"]
            for reason_code in candidate["reason_codes"]
        }
    )
    return {
        "schema": "noetheris.solver_boundary_evidence.v1",
        "scope": "v0.2 deterministic solver-boundary evidence",
        "host_independent": True,
        "runtime_seconds": None,
        "runtime_policy": (
            "committed evidence excludes wall-clock timing and installed optional "
            "package state"
        ),
        "problem": {
            "problem_type": compiled.problem_type,
            "problem_hash": compiled.problem_hash,
            "compiled_model_hash": compiled.compiled_model_hash,
        },
        "qubo_exchange": {
            "schema": exchange["format"],
            "model_hash": exchange["model_hash"],
            "vartype": exchange["vartype"],
            "variable_count": len(exchange["variables"]),
            "linear_term_count": len(exchange["linear_terms"]),
            "quadratic_term_count": len(exchange["quadratic_terms"]),
            "normalization": exchange["normalization"],
        },
        "candidate_replay": {
            "schema": replay["schema"],
            "status": replay["status"],
            "artifact_hash": replay["artifact_hash"],
            "reported_energy": replay["reported_energy"],
            "recomputed_energy": replay["recomputed_energy"],
            "energy_recomputed": replay["energy_recomputed"],
            "verification_authority": replay["verification_authority"],
        },
        "rejection_coverage": {
            "case_count": len(replay_examples["rejected_candidates"]),
            "reason_codes": reason_codes,
        },
        "optional_ecosystem_availability": {
            "ocean": {
                "committed_availability": "not_assumed",
                "credential_required": False,
                "runtime_probe_command": "python3 examples/dwave_ocean_exchange.py",
                "availability_field": "ocean_bqm_report.available",
                "host_independent": True,
            },
            "qiskit": {
                "committed_availability": "not_assumed",
                "credential_required": False,
                "runtime_probe_command": "python3 examples/qiskit_oracle_export.py",
                "availability_field": "qiskit_status.available",
                "host_independent": True,
            },
        },
        "metadata_boundaries": {
            "solver_metadata": {
                "authority": "external_tool",
                "local_interpretation": "recorded_evidence_only",
            },
            "embedding_metadata": {
                "authority": "external_tool",
                "local_interpretation": "recorded_evidence_only",
                "local_default": {
                    "embedding_status": "not_requested",
                    "embedding": None,
                },
            },
            "hardware_claims": {
                "hardware_benchmark": False,
                "quantum_advantage": False,
            },
        },
    }


def _external_replay_examples(
    compiled: Any,
    assignment: dict[str, bool],
    energy: float,
) -> dict[str, Any]:
    first_variable = compiled.model.variables[0]
    accepted = external_solver_replay_artifact(
        compiled,
        assignment,
        reported_energy=energy,
        problem_hash=compiled.problem_hash,
        compiled_model_hash=compiled.compiled_model_hash,
        solver_metadata={
            "solver": "local_exact_reference",
            "credential_required": False,
            "sample_source": "release_evidence",
        },
        embedding_metadata={
            "embedding_status": "not_requested",
            "embedding": None,
        },
        candidate_id="accepted-local-reference",
    )
    rejected = [
        _replay_case(
            "problem_hash_mismatch",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=energy,
                problem_hash="sha256:wrong-problem",
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-problem-hash",
            ),
        ),
        _replay_case(
            "compiled_model_hash_mismatch",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash="sha256:wrong-compiled-model",
                candidate_id="rejected-compiled-model-hash",
            ),
        ),
        _replay_case(
            "missing_variables",
            external_solver_replay_artifact(
                compiled,
                {
                    variable: value
                    for variable, value in assignment.items()
                    if variable != first_variable
                },
                reported_energy=energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-missing-variable",
            ),
        ),
        _replay_case(
            "unknown_variables",
            external_solver_replay_artifact(
                compiled,
                {**assignment, "outside_compiled_domain": True},
                reported_energy=energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-unknown-variable",
            ),
        ),
        _replay_case(
            "energy_mismatch",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=energy + 1.0,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                candidate_id="rejected-energy-mismatch",
            ),
        ),
        _replay_case(
            "malformed_metadata",
            external_solver_replay_artifact(
                compiled,
                assignment,
                reported_energy=energy,
                problem_hash=compiled.problem_hash,
                compiled_model_hash=compiled.compiled_model_hash,
                solver_metadata="not-a-mapping",  # type: ignore[arg-type]
                embedding_metadata="not-a-mapping",  # type: ignore[arg-type]
                candidate_id="rejected-malformed-metadata",
            ),
        ),
    ]
    return {
        "schema": "noetheris.external_solver_replay.examples.v1",
        "credential_required": False,
        "verification_authority": "noetheris.local_replay",
        "accepted_candidate": accepted,
        "rejected_candidates": rejected,
    }


def _replay_case(name: str, artifact: dict[str, Any]) -> dict[str, Any]:
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
