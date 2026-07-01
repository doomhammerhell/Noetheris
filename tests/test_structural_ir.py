from __future__ import annotations

from pathlib import Path

from noetheris.ir import StructuralSystem
from noetheris.qubo import (
    compile_invariant_search_to_qubo,
    compile_pqc_migration_to_qubo,
    compile_threshold_policy_to_qubo,
    evaluate_energy,
    explain_solution,
    solve_exact,
    solve_simulated_annealing,
)


ROOT = Path(__file__).resolve().parents[1]


def test_structural_ir_examples_load_validate_and_hash() -> None:
    for name in (
        "consensus_safety_ir.json",
        "pqc_migration_ir.json",
        "threshold_policy_ir.json",
        "cv_gkp_diagnostic_ir.json",
        "saga_failure_ir.json",
    ):
        system = StructuralSystem.from_json_file(ROOT / "examples" / "structural_ir" / name)
        system.validate()
        assert system.canonical_hash().startswith("sha256:")


def test_invariant_ir_compiles_and_reverse_maps() -> None:
    system = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "consensus_safety_ir.json"
    )
    compiled = compile_invariant_search_to_qubo(system)
    first = compiled.to_dict()
    second = compile_invariant_search_to_qubo(system).to_dict()
    assert first == second
    solution = solve_exact(compiled)
    explanation = explain_solution(compiled, solution)
    assert explanation["selected"]
    assert evaluate_energy(compiled, solution.assignment) == solution.energy


def test_migration_and_threshold_ir_compile() -> None:
    migration = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "pqc_migration_ir.json"
    )
    compiled_migration = compile_pqc_migration_to_qubo(migration)
    assert compiled_migration.model.variables
    threshold = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "threshold_policy_ir.json"
    )
    compiled_threshold = compile_threshold_policy_to_qubo(threshold)
    assert compiled_threshold.model.variables


def test_simulated_annealing_is_seed_deterministic() -> None:
    system = StructuralSystem.from_json_file(
        ROOT / "examples" / "structural_ir" / "threshold_policy_ir.json"
    )
    compiled = compile_threshold_policy_to_qubo(system)
    first = solve_simulated_annealing(compiled, seed=99, sweeps=32)
    second = solve_simulated_annealing(compiled, seed=99, sweeps=32)
    assert first == second
