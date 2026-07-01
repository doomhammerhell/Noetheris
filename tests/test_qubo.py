from __future__ import annotations

from noetheris.qubo import QuadraticTerm, QuboModel


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
