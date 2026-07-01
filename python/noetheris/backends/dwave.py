from __future__ import annotations

from typing import Any

from noetheris.qubo import QuboModel


def dwave_status() -> dict[str, Any]:
    try:
        import dimod  # type: ignore
    except Exception as exc:
        return {"available": False, "reason": exc.__class__.__name__}
    return {"available": True, "dimod": getattr(dimod, "__version__", "available")}


def export_qubo_to_dwave(model: QuboModel) -> dict[str, Any]:
    model.validate()
    status = dwave_status()
    qubo: dict[tuple[str, str], float] = {}
    for variable, coefficient in model.linear.items():
        qubo[(variable, variable)] = coefficient
    for term in model.quadratic:
        qubo[(term.left, term.right)] = term.coefficient
    return {
        "status": status,
        "offset": model.constant,
        "qubo": {f"{left},{right}": coefficient for (left, right), coefficient in sorted(qubo.items())},
        "credential_required": False,
    }
