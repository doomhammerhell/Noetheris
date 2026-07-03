from __future__ import annotations

from typing import Any

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
    oracle = build_oracle(expression, name=name)
    table = oracle.truth_table()
    status = qiskit_status()
    circuit_summary: dict[str, Any] | None = None
    if status["available"]:
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
            circuit_summary = {
                "class": "qiskit.QuantumCircuit",
                "num_qubits": circuit.num_qubits,
                "depth": circuit.depth(),
                "size": circuit.size(),
                "name": circuit.name,
            }
        except Exception as exc:
            circuit_summary = {
                "class": "qiskit.QuantumCircuit",
                "export_error": exc.__class__.__name__,
            }
    return {
        "status": status,
        "oracle_metrics": oracle.cost_metrics(),
        "truth_table": table,
        "qasm_like": oracle.qasm_like(),
        "qiskit_circuit_summary": circuit_summary,
        "credential_required": False,
        "export_policy": "truth-table synthesis is exact for small predicates and exponential in input width",
    }
