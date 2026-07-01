from __future__ import annotations

from typing import Any

from noetheris.circuits import BooleanOracle


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
