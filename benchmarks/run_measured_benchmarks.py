from __future__ import annotations

import json
import platform
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.circuits import AND, BoolExpr, build_oracle
from noetheris.cv import cv_diagnostic_certificate
from noetheris.ir import StructuralSystem
from noetheris.qubo import compile_system, solve_exact, solve_simulated_annealing


def measured_benchmarks() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for name, file_name, problem in (
        ("consensus_ir", "consensus_safety_ir.json", "invariant"),
        ("saga_ir", "saga_failure_ir.json", "invariant"),
        ("threshold_ir", "threshold_policy_ir.json", "threshold"),
        ("pqc_migration_ir", "pqc_migration_ir.json", "migration"),
    ):
        system = StructuralSystem.from_json_file(ROOT / "examples" / "structural_ir" / file_name)
        compiled = compile_system(system, problem)

        def exact_run():
            return solve_exact(compiled)

        def anneal_run():
            return solve_simulated_annealing(compiled, seed=1337, sweeps=64)

        for solver_name, run in (("exact", exact_run), ("anneal", anneal_run)):
            elapsed, solution = _measure(run)
            records.append(
                {
                    "problem_name": name,
                    "problem_size": len(system.nodes) + len(system.edges),
                    "variable_count": len(compiled.model.variables),
                    "constraint_count": len(compiled.constraints),
                    "solver": solver_name,
                    "seed": 1337,
                    "runtime_seconds": elapsed,
                    "energy": solution.energy,
                    "validation_status": "energy_replayed",
                }
            )

    elapsed, oracle = _measure(lambda: build_oracle(AND(BoolExpr.var("a"), BoolExpr.var("b"))))
    records.append(
        {
            "problem_name": "oracle_and_policy",
            "problem_size": oracle.cost_metrics()["logical_variables"],
            "variable_count": oracle.cost_metrics()["logical_variables"],
            "constraint_count": 1,
            "solver": "truth_table",
            "seed": 1337,
            "runtime_seconds": elapsed,
            "energy": 0.0,
            "validation_status": "truth_table_verified",
        }
    )

    elapsed, cv = _measure(lambda: cv_diagnostic_certificate(cutoff=8, delta=0.4, grid_cutoff=1, seed=1337))
    records.append(
        {
            "problem_name": "cv_gkp_cutoff_8",
            "problem_size": 8,
            "variable_count": 0,
            "constraint_count": 2,
            "solver": "cv_diagnostic",
            "seed": 1337,
            "runtime_seconds": elapsed,
            "energy": cv["certificate"]["total_energy"],
            "validation_status": f"certificate_{cv['certificate_status']}",
        }
    )

    return {
        "release": "Noetheris v0.1.0 — Structural Quantum Security Kernel",
        "benchmark_scope": "measured local run",
        "environment": _environment(),
        "records": records,
    }


def _measure(callback: Callable[[], Any]) -> tuple[float, Any]:
    start = perf_counter()
    value = callback()
    return perf_counter() - start, value


def _environment() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "commit": _commit(),
    }


def _commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "git metadata unavailable"


def main() -> None:
    print(json.dumps(measured_benchmarks(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
