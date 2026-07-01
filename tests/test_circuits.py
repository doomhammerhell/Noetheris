from __future__ import annotations

from noetheris.circuits import AND, IMPLIES, BooleanOracle, BoolExpr, build_oracle
from noetheris.circuits import expectation_from_probabilities, simulate_qaoa
from noetheris.qubo import QuboModel


def test_symbolic_circuit_oracle_behavior() -> None:
    oracle = BooleanOracle(
        ("a", "b", "c"),
        lambda bits: 1 if sum(bits) >= 2 else 0,
        name="threshold",
    )
    assert oracle.apply((1, 1, 0), 0) == ((1, 1, 0), 1)
    assert oracle.apply((1, 0, 0), 1) == ((1, 0, 0), 1)
    assert "xor threshold" in oracle.symbolic_circuit().to_text()


def test_qaoa_simulator_preserves_probability_mass() -> None:
    model = QuboModel(variables=["x"], linear={"x": -1.0})
    result = simulate_qaoa(model, gammas=(0.7,), betas=(0.2,))
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-9
    assert abs(
        expectation_from_probabilities(model, result.probabilities) - result.expectation
    ) < 1e-9
    assert result.most_probable_energy in (0.0, -1.0)


def test_oracle_compiler_truth_table_and_metrics() -> None:
    a = BoolExpr.var("a")
    b = BoolExpr.var("b")
    expression = IMPLIES(AND(a, b), a)
    oracle = build_oracle(expression, name="implication")
    table = oracle.truth_table()
    assert set(table.values()) == {1}
    metrics = oracle.cost_metrics()
    assert metrics["logical_variables"] == 2
    assert metrics["gate_count"] >= 2
    assert oracle.reversibility_check() is True
    assert "OPENQASM-LIKE" in oracle.qasm_like()
