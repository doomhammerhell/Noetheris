from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from noetheris.certificates import validate_certificate
from noetheris.certificates.replay import main as replay_certificate_main
from noetheris.cv import cv_diagnostic_certificate
from noetheris.ir import StructuralSystem
from noetheris.qubo import (
    CompiledProblem,
    compile_system,
    explain_solution,
    solve_exact,
    solve_simulated_annealing,
)


ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="noetheris")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_ir = subparsers.add_parser("validate-ir")
    validate_ir.add_argument("file")

    compile_qubo = subparsers.add_parser("compile-qubo")
    compile_qubo.add_argument("file")
    compile_qubo.add_argument("--problem", choices=("invariant", "migration", "threshold"), required=True)
    compile_qubo.add_argument("--output")

    solve = subparsers.add_parser("solve")
    solve.add_argument("compiled_qubo")
    solve.add_argument("--solver", choices=("exact", "anneal"), default="exact")
    solve.add_argument("--seed", type=int, default=1337)
    solve.add_argument("--output")

    validate_cert = subparsers.add_parser("validate-certificate")
    validate_cert.add_argument("certificate")

    replay_cert = subparsers.add_parser("replay-certificate")
    replay_cert.add_argument("certificate")

    scenario = subparsers.add_parser("run-scenario")
    scenario.add_argument("name")

    benchmark = subparsers.add_parser("benchmark")
    benchmark.add_argument("--small", action="store_true")

    cv = subparsers.add_parser("cv-diagnostics")
    cv.add_argument("scenario")

    args = parser.parse_args(argv)
    if args.command == "validate-ir":
        system = StructuralSystem.from_json_file(args.file)
        system.validate()
        return _emit({"status": "valid", "canonical_hash": system.canonical_hash()})
    if args.command == "compile-qubo":
        system = StructuralSystem.from_json_file(args.file)
        compiled = compile_system(system, args.problem)
        return _emit(compiled.to_dict(), args.output)
    if args.command == "solve":
        with Path(args.compiled_qubo).open("r", encoding="utf-8") as handle:
            compiled = CompiledProblem.from_dict(json.load(handle))
        solution = (
            solve_exact(compiled)
            if args.solver == "exact"
            else solve_simulated_annealing(compiled, seed=args.seed)
        )
        payload = {
            "solver": args.solver,
            "seed": args.seed,
            "assignment": solution.assignment,
            "energy": solution.energy,
            "explanation": explain_solution(compiled, solution),
        }
        return _emit(payload, args.output)
    if args.command == "validate-certificate":
        with Path(args.certificate).open("r", encoding="utf-8") as handle:
            result = validate_certificate(json.load(handle))
        _emit({"status": result.status, "reasons": list(result.reasons)})
        return 0 if result.status == "verified" else 1
    if args.command == "replay-certificate":
        return replay_certificate_main([args.certificate])
    if args.command == "run-scenario":
        return _run_scenario(args.name)
    if args.command == "benchmark":
        from benchmarks.run_benchmarks import run_benchmarks

        return _emit(run_benchmarks(small=bool(args.small)))
    if args.command == "cv-diagnostics":
        with Path(args.scenario).open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        metadata = value.get("metadata", value)
        return _emit(
            cv_diagnostic_certificate(
                cutoff=int(metadata.get("fock_cutoff", metadata.get("cutoff", 10))),
                delta=float(metadata.get("delta", 0.35)),
                grid_cutoff=int(metadata.get("grid_cutoff", 2)),
                seed=2026,
            )
        )
    raise ValueError(f"unknown command {args.command}")


def _run_scenario(name: str) -> int:
    scenarios = {
        "consensus": (ROOT / "examples" / "structural_ir" / "consensus_safety_ir.json", "invariant"),
        "saga": (ROOT / "examples" / "structural_ir" / "saga_failure_ir.json", "invariant"),
        "threshold": (ROOT / "examples" / "structural_ir" / "threshold_policy_ir.json", "threshold"),
        "migration": (ROOT / "examples" / "structural_ir" / "pqc_migration_ir.json", "migration"),
        "cv-gkp": (ROOT / "examples" / "structural_ir" / "cv_gkp_diagnostic_ir.json", "cv"),
    }
    if name not in scenarios:
        raise ValueError(f"unknown scenario {name}")
    path, problem = scenarios[name]
    if problem == "cv":
        return main(["cv-diagnostics", str(path)])
    system = StructuralSystem.from_json_file(path)
    compiled = compile_system(system, problem)
    solution = solve_exact(compiled)
    return _emit(explain_solution(compiled, solution))


def _emit(payload: dict[str, Any], output: str | None = None) -> int:
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0
