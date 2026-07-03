from __future__ import annotations

from typing import Any

from noetheris.certificates import stable_problem_hash
from noetheris.qubo import QuboModel


def dwave_status() -> dict[str, Any]:
    try:
        import dimod  # type: ignore
    except Exception as exc:
        return {"available": False, "reason": exc.__class__.__name__}
    return {"available": True, "dimod": getattr(dimod, "__version__", "available")}


def export_qubo_to_dwave(model: QuboModel) -> dict[str, Any]:
    model.validate()
    canonical = model.canonicalized()
    status = dwave_status()
    payload = qubo_exchange_payload(model)
    bqm_summary: dict[str, Any] | None = None
    if status["available"]:
        try:
            import dimod  # type: ignore

            bqm = dimod.BinaryQuadraticModel(
                dict(canonical.linear),
                {(term.left, term.right): term.coefficient for term in canonical.quadratic},
                canonical.constant,
                dimod.BINARY,
            )
            qubo, offset = bqm.to_qubo()
            bqm_summary = {
                "class": "dimod.BinaryQuadraticModel",
                "vartype": str(bqm.vartype),
                "num_variables": len(bqm.variables),
                "num_interactions": len(bqm.quadratic),
                "to_qubo_terms": len(qubo),
                "to_qubo_offset": float(offset),
            }
        except Exception as exc:
            bqm_summary = {
                "class": "dimod.BinaryQuadraticModel",
                "export_error": exc.__class__.__name__,
            }
    return {
        "status": status,
        "exchange": payload,
        "bqm_summary": bqm_summary,
        "credential_required": False,
        "external_solver_policy": "solver samples are untrusted until local energy replay succeeds",
    }


def qubo_exchange_payload(model: QuboModel) -> dict[str, Any]:
    canonical = model.canonicalized()
    payload = {
        "format": "noetheris.qubo.exchange.v1",
        "vartype": "BINARY",
        "variables": list(canonical.variables),
        "offset": canonical.constant,
        "linear_terms": [
            {"variable": variable, "coefficient": coefficient}
            for variable, coefficient in sorted(canonical.linear.items())
        ],
        "quadratic_terms": [
            {
                "left": term.left,
                "right": term.right,
                "coefficient": term.coefficient,
            }
            for term in canonical.quadratic
        ],
        "normalization": {
            "duplicate_pairs": "aggregated",
            "reversed_pairs": "ordered_by_variable_list",
            "self_quadratic": "folded_into_linear",
        },
    }
    return {**payload, "model_hash": stable_problem_hash(payload)}


def replay_external_sample(
    model: QuboModel,
    sample: dict[str, bool | int],
    *,
    solver_metadata: dict[str, Any] | None = None,
    embedding_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assignment = {name: bool(value) for name, value in sample.items()}
    energy = model.evaluate(assignment)
    return {
        "status": "replayed",
        "assignment": {name: assignment[name] for name in model.variables},
        "energy": energy,
        "model_hash": stable_problem_hash(model.to_dict()),
        "solver_metadata": solver_metadata or {},
        "embedding_metadata": embedding_metadata or {
            "provided": False,
            "policy": "embedding is solver-specific metadata and is not inferred locally",
        },
    }
