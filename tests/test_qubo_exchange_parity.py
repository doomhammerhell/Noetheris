from __future__ import annotations

from itertools import product
from typing import Any, Mapping

import pytest

from noetheris.backends import qubo_exchange_payload
from noetheris.qubo import QuadraticTerm, QuboModel


def _assignments(variables: list[str]) -> list[dict[str, bool]]:
    return [
        dict(zip(variables, bits))
        for bits in product((False, True), repeat=len(variables))
    ]


def _exchange_energy(payload: Mapping[str, Any], assignment: Mapping[str, bool]) -> float:
    expected = set(payload["variables"])
    provided = set(assignment)
    if expected != provided:
        raise ValueError("assignment domain does not match exchange variables")
    energy = float(payload["offset"])
    for item in payload["linear_terms"]:
        if assignment[str(item["variable"])]:
            energy += float(item["coefficient"])
    for item in payload["quadratic_terms"]:
        if assignment[str(item["left"])] and assignment[str(item["right"])]:
            energy += float(item["coefficient"])
    return energy


def _optional_ocean_energy(
    payload: Mapping[str, Any], assignment: Mapping[str, bool]
) -> float | None:
    try:
        import dimod  # type: ignore
    except Exception:
        return None
    bqm = dimod.BinaryQuadraticModel(
        {
            str(item["variable"]): float(item["coefficient"])
            for item in payload["linear_terms"]
        },
        {
            (str(item["left"]), str(item["right"])): float(item["coefficient"])
            for item in payload["quadratic_terms"]
        },
        float(payload["offset"]),
        dimod.BINARY,
    )
    return float(
        bqm.energy({variable: int(value) for variable, value in assignment.items()})
    )


@pytest.mark.parametrize(
    "model",
    [
        QuboModel(
            variables=["x"],
            linear={"x": -1.25},
            constant=0.5,
        ),
        QuboModel(
            variables=["a", "b", "c"],
            linear={"a": -2.0, "b": 0.75, "c": 1.5},
            quadratic=[
                QuadraticTerm("a", "b", 4.0),
                QuadraticTerm("b", "c", -0.5),
            ],
            constant=-3.0,
        ),
        QuboModel(
            variables=["alpha", "beta", "gamma"],
            linear={"gamma": 0.25},
            quadratic=[
                QuadraticTerm("beta", "alpha", 2.0),
                QuadraticTerm("alpha", "beta", -0.25),
                QuadraticTerm("gamma", "alpha", 1.5),
                QuadraticTerm("alpha", "gamma", 0.5),
            ],
            constant=2.0,
        ),
        QuboModel(
            variables=["x", "y"],
            linear={"x": 1.0},
            quadratic=[
                QuadraticTerm("x", "x", 4.0),
                QuadraticTerm("y", "y", -2.0),
                QuadraticTerm("y", "x", 3.0),
            ],
            constant=0.125,
        ),
        QuboModel(
            variables=["node,0", "node,1"],
            linear={"node,0": -0.5},
            quadratic=[
                QuadraticTerm("node,1", "node,0", 1.25),
                QuadraticTerm("node,0", "node,0", -0.75),
            ],
            constant=9.0,
        ),
        QuboModel(
            variables=["left", "right"],
            linear={"left": 1.0, "right": -1.0},
            quadratic=[
                QuadraticTerm("left", "right", 2.0),
                QuadraticTerm("right", "left", -2.0),
            ],
            constant=4.0,
        ),
    ],
)
def test_qubo_exchange_preserves_energy_for_all_small_assignments(
    model: QuboModel,
) -> None:
    payload = qubo_exchange_payload(model)
    canonical = model.canonicalized()
    assert payload == qubo_exchange_payload(canonical)
    assert payload["variables"] == model.variables
    assert payload["normalization"] == {
        "duplicate_pairs": "aggregated",
        "reversed_pairs": "ordered_by_variable_list",
        "self_quadratic": "folded_into_linear",
    }
    for assignment in _assignments(model.variables):
        original_energy = model.evaluate(assignment)
        canonical_energy = canonical.evaluate(assignment)
        exchange_energy = _exchange_energy(payload, assignment)
        ocean_energy = _optional_ocean_energy(payload, assignment)
        assert original_energy == pytest.approx(canonical_energy)
        assert original_energy == pytest.approx(exchange_energy)
        if ocean_energy is not None:
            assert original_energy == pytest.approx(ocean_energy)


def test_qubo_exchange_large_models_are_valid_without_exact_solving() -> None:
    variables = [f"asset,{idx}" for idx in range(25)]
    model = QuboModel(
        variables=variables,
        linear={variables[0]: -1.0, variables[-1]: 2.0},
        quadratic=[
            QuadraticTerm(variables[1], variables[0], 3.0),
            QuadraticTerm(variables[0], variables[1], -0.5),
            QuadraticTerm(variables[-1], variables[-1], 4.0),
        ],
        constant=7.0,
    )
    model.validate()
    payload = qubo_exchange_payload(model)
    assert payload["variables"] == variables
    assert payload["linear_terms"] == [
        {"variable": variables[0], "coefficient": -1.0},
        {"variable": variables[-1], "coefficient": 6.0},
    ]
    assert payload["quadratic_terms"] == [
        {"left": variables[0], "right": variables[1], "coefficient": 2.5}
    ]
    try:
        model.exhaustive_solve()
    except ValueError as exc:
        assert "bounded to 24 variables" in str(exc)
    else:
        raise AssertionError("large export model was solved exhaustively")


def test_qubo_exchange_rejects_assignment_domain_mismatch() -> None:
    payload = qubo_exchange_payload(QuboModel(variables=["x"], linear={"x": -1.0}))
    with pytest.raises(ValueError, match="assignment domain"):
        _exchange_energy(payload, {})
    with pytest.raises(ValueError, match="assignment domain"):
        _exchange_energy(payload, {"x": True, "extra": True})
