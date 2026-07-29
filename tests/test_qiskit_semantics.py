from __future__ import annotations

from itertools import product
import sys
from types import SimpleNamespace
from typing import Callable

import pytest

from noetheris.backends import (
    export_bool_expr_to_qiskit,
    qiskit_oracle_semantics_report,
)
from noetheris.circuits import AND, EQ, IMPLIES, OR, XOR, BoolExpr


Predicate = Callable[[dict[str, bool]], bool]


def _expected_table(variables: tuple[str, ...], predicate: Predicate) -> dict[str, int]:
    table: dict[str, int] = {}
    for bits in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        table["".join("1" if bit else "0" for bit in bits)] = int(
            predicate(assignment)
        )
    return table


def _cases() -> list[tuple[str, BoolExpr, tuple[str, ...], Predicate]]:
    a = BoolExpr.var("a")
    b = BoolExpr.var("b")
    c = BoolExpr.var("c")
    return [
        ("and", AND(a, b), ("a", "b"), lambda bits: bits["a"] and bits["b"]),
        ("or", OR(a, b), ("a", "b"), lambda bits: bits["a"] or bits["b"]),
        ("xor", XOR(a, b), ("a", "b"), lambda bits: bits["a"] ^ bits["b"]),
        (
            "implies",
            IMPLIES(a, b),
            ("a", "b"),
            lambda bits: (not bits["a"]) or bits["b"],
        ),
        ("eq", EQ(a, b), ("a", "b"), lambda bits: bits["a"] == bits["b"]),
        (
            "threshold_two_of_three",
            OR(AND(a, b), AND(a, c), AND(b, c)),
            ("a", "b", "c"),
            lambda bits: sum(1 for value in bits.values() if value) >= 2,
        ),
    ]


@pytest.mark.parametrize("name,expression,variables,predicate", _cases())
def test_qiskit_oracle_semantics_match_bool_expr_and_symbolic_oracle(
    name: str,
    expression: BoolExpr,
    variables: tuple[str, ...],
    predicate: Predicate,
) -> None:
    expected = _expected_table(variables, predicate)
    report = qiskit_oracle_semantics_report(expression, name=name)
    payload = export_bool_expr_to_qiskit(expression, name=name)
    assert report["variables"] == list(variables)
    assert report["truth_table"] == expected
    assert report["bool_expr_truth_table"] == expected
    assert report["symbolic_oracle_truth_table"] == expected
    assert report["semantic_checks"] == {
        "bool_expr_matches_symbolic_oracle": True,
        "reversibility_check": True,
        "complete_truth_table": True,
    }
    assert report["truth_table_entries"] == 2 ** len(variables)
    assert report["oracle_metrics"]["logical_variables"] == len(variables)
    assert report["oracle_metrics"]["cleanup_gate_count"] >= 1
    assert report["oracle_metrics"]["depth_estimate"] == report["oracle_metrics"]["gate_count"]
    assert report["qiskit_semantics"]["backend_execution"] is False
    assert "exponential" in report["synthesis_limit"]
    assert payload["credential_required"] is False
    assert payload["truth_table"] == expected
    assert payload["semantic_report"]["truth_table_hash"] == report["truth_table_hash"]


def test_qiskit_semantics_report_summarizes_local_quantum_circuit(monkeypatch) -> None:
    class LocalQuantumCircuit:
        def __init__(self, num_qubits: int, *, name: str):
            self.num_qubits = num_qubits
            self.name = name
            self.operations: list[tuple[str, tuple[object, ...]]] = []

        def x(self, qubit: int) -> None:
            self.operations.append(("x", (qubit,)))

        def cx(self, control: int, target: int) -> None:
            self.operations.append(("cx", (control, target)))

        def mcx(self, controls: list[int], target: int) -> None:
            self.operations.append(("mcx", (tuple(controls), target)))

        def depth(self) -> int:
            return len(self.operations)

        def size(self) -> int:
            return len(self.operations)

    local_qiskit = SimpleNamespace(
        __version__="local-test",
        QuantumCircuit=LocalQuantumCircuit,
    )
    monkeypatch.setitem(sys.modules, "qiskit", local_qiskit)
    expression = AND(BoolExpr.var("a"), BoolExpr.var("b"))
    payload = export_bool_expr_to_qiskit(expression, name="and_policy")
    summary = payload["qiskit_circuit_summary"]
    assert payload["status"] == {"available": True, "qiskit": "local-test"}
    assert summary["class"] == "qiskit.QuantumCircuit"
    assert summary["name"] == "O_and_policy"
    assert summary["num_qubits"] == 3
    assert summary["truth_table_entries"] == 4
    assert summary["true_rows"] == ["11"]
    assert summary["synthesis"] == "exact_truth_table_multi_controlled_x"
    assert payload["semantic_report"]["qiskit_semantics"]["status"] == (
        "synthesized_from_verified_truth_table"
    )
    assert payload["semantic_report"]["qiskit_semantics"]["backend_execution"] is False
