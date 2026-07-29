from __future__ import annotations

from itertools import product
from typing import Any

from noetheris.certificates import stable_problem_hash
from noetheris.circuits import BooleanOracle, BoolExpr, build_oracle


def qiskit_status() -> dict[str, Any]:
    try:
        import qiskit  # type: ignore
    except Exception as exc:
        return {"available": False, "reason": exc.__class__.__name__}
    return {"available": True, "qiskit": getattr(qiskit, "__version__", "available")}


def qasm_like_export(oracle: BooleanOracle) -> str:
    lines = ["OPENQASM-LIKE 0.1;", f"// oracle O_{oracle.name}"]
    for variable in oracle.variables:
        lines.append(f"qubit {variable};")
    lines.append("qubit target;")
    for operation in oracle.symbolic_circuit().operations:
        lines.append(f"// {operation}")
    return "\n".join(lines)


def export_oracle_to_qiskit(oracle: BooleanOracle) -> dict[str, Any]:
    circuit, status = oracle.qiskit_export()
    return {
        "status": qiskit_status(),
        "export_status": status,
        "qasm_like": qasm_like_export(oracle),
        "qiskit_object_available": circuit is not None,
        "credential_required": False,
    }


def export_bool_expr_to_qiskit(expression: BoolExpr, *, name: str = "phi") -> dict[str, Any]:
    semantics = qiskit_oracle_semantics_report(expression, name=name)
    return {
        "status": semantics["qiskit_status"],
        "oracle_metrics": semantics["oracle_metrics"],
        "truth_table": semantics["truth_table"],
        "qasm_like": semantics["qasm_like"],
        "qiskit_circuit_summary": semantics["qiskit_circuit_summary"],
        "credential_required": False,
        "export_policy": "truth-table synthesis is exact for small predicates and exponential in input width",
        "semantic_report": semantics,
    }


def qiskit_oracle_semantics_report(
    expression: BoolExpr, *, name: str = "phi"
) -> dict[str, Any]:
    oracle = build_oracle(expression, name=name)
    expression_table = _expression_truth_table(expression)
    oracle_table = oracle.truth_table()
    truth_table_hash = stable_problem_hash(
        {
            "variables": list(oracle.variables),
            "truth_table": expression_table,
        }
    )
    status = qiskit_status()
    circuit_summary = _qiskit_circuit_summary(
        oracle,
        expression_table,
        name=name,
        available=status["available"],
    )
    if status["available"]:
        qiskit_semantics = {
            "status": (
                "export_error"
                if circuit_summary and "export_error" in circuit_summary
                else "synthesized_from_verified_truth_table"
            ),
            "truth_table_hash": truth_table_hash,
            "backend_execution": False,
            "equivalence_basis": (
                "local BoolExpr truth table equals symbolic oracle truth table; "
                "Qiskit circuit is synthesized from that verified table"
            ),
        }
    else:
        qiskit_semantics = {
            "status": "qiskit_unavailable",
            "truth_table_hash": truth_table_hash,
            "backend_execution": False,
            "equivalence_basis": "Qiskit package unavailable; local truth table remains authoritative",
        }
    return {
        "variables": list(oracle.variables),
        "truth_table": expression_table,
        "truth_table_hash": truth_table_hash,
        "truth_table_entries": len(expression_table),
        "true_rows": [
            bitstring for bitstring, value in sorted(expression_table.items()) if value
        ],
        "bool_expr_truth_table": expression_table,
        "symbolic_oracle_truth_table": oracle_table,
        "semantic_checks": {
            "bool_expr_matches_symbolic_oracle": expression_table == oracle_table,
            "reversibility_check": oracle.reversibility_check(),
            "complete_truth_table": len(expression_table) == 2 ** len(oracle.variables),
        },
        "oracle_metrics": oracle.cost_metrics(),
        "qasm_like": oracle.qasm_like(),
        "qiskit_status": status,
        "qiskit_circuit_summary": circuit_summary,
        "qiskit_semantics": qiskit_semantics,
        "credential_required": False,
        "synthesis_limit": "truth-table synthesis is exponential in logical variable count",
    }


def _expression_truth_table(expression: BoolExpr) -> dict[str, int]:
    variables = expression.variables()
    table: dict[str, int] = {}
    for bits in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        table["".join("1" if bit else "0" for bit in bits)] = int(
            expression.evaluate(assignment)
        )
    return table


def _qiskit_circuit_summary(
    oracle: Any,
    table: dict[str, int],
    *,
    name: str,
    available: bool,
) -> dict[str, Any] | None:
    if not available:
        return None
    try:
        from qiskit import QuantumCircuit  # type: ignore

        width = len(oracle.variables)
        target = width
        circuit = QuantumCircuit(width + 1, name=f"O_{name}")
        for bitstring, value in sorted(table.items()):
            if not value:
                continue
            false_controls = [
                index for index, bit in enumerate(bitstring) if bit == "0"
            ]
            for index in false_controls:
                circuit.x(index)
            if width == 0:
                circuit.x(target)
            elif width == 1:
                circuit.cx(0, target)
            else:
                circuit.mcx(list(range(width)), target)
            for index in reversed(false_controls):
                circuit.x(index)
        return {
            "class": "qiskit.QuantumCircuit",
            "num_qubits": circuit.num_qubits,
            "depth": circuit.depth(),
            "size": circuit.size(),
            "name": circuit.name,
            "synthesis": "exact_truth_table_multi_controlled_x",
            "truth_table_entries": len(table),
            "true_rows": [
                bitstring for bitstring, value in sorted(table.items()) if value
            ],
        }
    except Exception as exc:
        return {
            "class": "qiskit.QuantumCircuit",
            "export_error": exc.__class__.__name__,
        }
