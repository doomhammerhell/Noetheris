from __future__ import annotations

from noetheris.qubo import (
    CompiledProblem,
    QuadraticTerm,
    QuboModel,
    external_solver_replay_artifact,
    replay_external_solution,
)


def test_qubo_construction_and_solution() -> None:
    model = QuboModel(
        variables=["x", "y"],
        linear={"x": -2.0, "y": 1.0},
        quadratic=[QuadraticTerm("x", "y", 4.0)],
    )
    solution = model.exhaustive_solve()
    assert solution.assignment == {"x": True, "y": False}
    assert solution.energy == -2.0


def test_exactly_one_qubo_selects_minimum_cost() -> None:
    model = QuboModel.exactly_one_choice(
        {"path_0": 4.0, "path_1": 1.0, "path_2": 7.0}, penalty=20.0
    )
    solution = model.exhaustive_solve()
    assert solution.assignment["path_1"] is True
    assert sum(solution.assignment.values()) == 1


def test_qubo_to_ising_preserves_energy() -> None:
    model = QuboModel(
        variables=["x", "y"],
        linear={"x": -2.0, "y": 1.0},
        quadratic=[QuadraticTerm("x", "y", 5.0)],
        constant=0.5,
    )
    ising = model.to_ising()
    for x in (False, True):
        for y in (False, True):
            assignment = {"x": x, "y": y}
            spins = model.assignment_to_spins(assignment)
            assert abs(model.evaluate(assignment) - ising.evaluate(spins)) < 1e-9
    assert any(term.operator == "Z[x] Z[y]" for term in ising.hamiltonian_terms())


def test_qubo_rejects_incomplete_assignment() -> None:
    model = QuboModel(variables=["x", "y"], linear={"x": 1.0})
    try:
        model.evaluate({"x": True})
    except ValueError as exc:
        assert "missing variables" in str(exc)
    else:
        raise AssertionError("incomplete assignment was accepted")


def test_canonical_qubo_preserves_energy_with_duplicate_reverse_and_self_terms() -> None:
    model = QuboModel(
        variables=["x", "y"],
        linear={"x": 1.0},
        quadratic=[
            QuadraticTerm("x", "y", 2.0),
            QuadraticTerm("y", "x", 3.0),
            QuadraticTerm("x", "x", 4.0),
        ],
        constant=0.25,
    )
    canonical = model.canonicalized()
    assert canonical.linear["x"] == 5.0
    assert canonical.quadratic == [QuadraticTerm("x", "y", 5.0)]
    for x in (False, True):
        for y in (False, True):
            assignment = {"x": x, "y": y}
            assert model.evaluate(assignment) == canonical.evaluate(assignment)


def test_exact_solver_bound_does_not_block_structural_validation() -> None:
    variables = [f"x{i}" for i in range(25)]
    model = QuboModel(variables=variables, linear={variables[0]: -1.0})
    model.validate()
    try:
        model.exhaustive_solve()
    except ValueError as exc:
        assert "bounded to 24 variables" in str(exc)
    else:
        raise AssertionError("oversized exact solve was accepted")


def test_external_solution_replay_fails_closed() -> None:
    model = QuboModel(variables=["x"], linear={"x": -1.0})
    compiled = CompiledProblem(
        problem_type="unit",
        problem_hash="sha256:problem",
        compiled_model_hash="sha256:compiled",
        model=model,
        variable_metadata={"x": "unit"},
    )
    verified = replay_external_solution(
        compiled,
        {"x": True},
        reported_energy=-1.0,
        problem_hash="sha256:problem",
        compiled_model_hash="sha256:compiled",
    )
    assert verified["status"] == "verified"
    assert verified["energy_recomputed"] is True

    assert replay_external_solution(compiled, {"x": True}, reported_energy=0.0)["status"] == "rejected"
    assert replay_external_solution(compiled, {"x": True}, problem_hash="bad")["status"] == "rejected"
    assert replay_external_solution(compiled, {}, reported_energy=0.0)["status"] == "rejected"
    assert replay_external_solution(compiled, {"x": True, "y": True}, reported_energy=-1.0)["status"] == "rejected"


def test_external_replay_artifact_records_explicit_rejection_codes() -> None:
    model = QuboModel(variables=["x", "y"], linear={"x": -1.0, "y": 2.0})
    compiled = CompiledProblem(
        problem_type="unit",
        problem_hash="sha256:problem",
        compiled_model_hash="sha256:compiled",
        model=model,
        variable_metadata={"x": "unit", "y": "unit"},
    )
    accepted = external_solver_replay_artifact(
        compiled,
        {"x": 1, "y": 0},
        reported_energy=-1.0,
        problem_hash="sha256:problem",
        compiled_model_hash="sha256:compiled",
        solver_metadata={"solver": "local_reference"},
    )
    assert accepted["schema"] == "noetheris.external_solver_replay.v1"
    assert accepted["status"] == "verified"
    assert accepted["artifact_hash"].startswith("sha256:")
    assert accepted["assignment_domain"]["missing_variables"] == []
    assert accepted["assignment_domain"]["unknown_variables"] == []
    assert accepted["recomputed_energy"] == -1.0

    rejected_cases = {
        "problem_hash_mismatch": external_solver_replay_artifact(
            compiled,
            {"x": True, "y": False},
            reported_energy=-1.0,
            problem_hash="sha256:wrong",
            compiled_model_hash="sha256:compiled",
        ),
        "compiled_model_hash_mismatch": external_solver_replay_artifact(
            compiled,
            {"x": True, "y": False},
            reported_energy=-1.0,
            problem_hash="sha256:problem",
            compiled_model_hash="sha256:wrong",
        ),
        "assignment_missing_variables": external_solver_replay_artifact(
            compiled,
            {"x": True},
            reported_energy=-1.0,
        ),
        "assignment_unknown_variables": external_solver_replay_artifact(
            compiled,
            {"x": True, "y": False, "z": True},
            reported_energy=-1.0,
        ),
        "reported_energy_mismatch": external_solver_replay_artifact(
            compiled,
            {"x": True, "y": False},
            reported_energy=3.0,
        ),
        "solver_metadata_malformed": external_solver_replay_artifact(
            compiled,
            {"x": True, "y": False},
            reported_energy=-1.0,
            solver_metadata="not-a-mapping",  # type: ignore[arg-type]
        ),
        "embedding_metadata_malformed": external_solver_replay_artifact(
            compiled,
            {"x": True, "y": False},
            reported_energy=-1.0,
            embedding_metadata="not-a-mapping",  # type: ignore[arg-type]
        ),
    }
    for expected_code, artifact in rejected_cases.items():
        assert artifact["status"] == "rejected"
        assert expected_code in {
            reason["code"] for reason in artifact["rejection_reasons"]
        }
