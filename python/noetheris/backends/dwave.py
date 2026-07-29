from __future__ import annotations

from typing import Any, Mapping

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
    status = dwave_status()
    payload = qubo_exchange_payload(model)
    bqm_report = ocean_bqm_parity_report(model, assignments=())
    return {
        "status": status,
        "exchange": payload,
        "bqm_summary": bqm_report["bqm_summary"],
        "ocean_bqm_report": bqm_report,
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


def ocean_bqm_parity_report(
    model: QuboModel,
    *,
    assignments: tuple[Mapping[str, bool | int], ...],
) -> dict[str, Any]:
    model.validate()
    try:
        import dimod  # type: ignore
    except Exception as exc:
        return {
            "available": False,
            "reason": exc.__class__.__name__,
            "credential_required": False,
            "bqm_summary": None,
            "assignment_reports": [],
            "energy_agreement": None,
            "policy": "Ocean is optional; missing dimod does not affect local Noetheris replay",
        }

    canonical = model.canonicalized()
    try:
        linear_biases = {
            variable: canonical.linear.get(variable, 0.0)
            for variable in canonical.variables
        }
        bqm = dimod.BinaryQuadraticModel(
            linear_biases,
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
            "offset": float(getattr(bqm, "offset", canonical.constant)),
            "to_qubo_terms": len(qubo),
            "to_qubo_offset": float(offset),
        }
        assignment_reports = [
            _ocean_assignment_report(model, bqm, assignment)
            for assignment in assignments
        ]
    except Exception as exc:
        return {
            "available": True,
            "credential_required": False,
            "bqm_summary": {
                "class": "dimod.BinaryQuadraticModel",
                "export_error": exc.__class__.__name__,
            },
            "assignment_reports": [],
            "energy_agreement": False,
            "policy": "local BQM construction failed before any external solver boundary",
        }
    return {
        "available": True,
        "credential_required": False,
        "bqm_summary": bqm_summary,
        "assignment_reports": assignment_reports,
        "energy_agreement": (
            all(item["agreement"] for item in assignment_reports)
            if assignment_reports
            else None
        ),
        "policy": "local dimod BQM construction only; no D-Wave credentials or sampler calls",
    }


def _ocean_assignment_report(
    model: QuboModel, bqm: Any, assignment: Mapping[str, bool | int]
) -> dict[str, Any]:
    normalized = {variable: bool(value) for variable, value in assignment.items()}
    noetheris_energy = model.evaluate(normalized)
    ocean_assignment = {
        variable: int(normalized[variable]) for variable in model.variables
    }
    ocean_energy = float(bqm.energy(ocean_assignment))
    difference = ocean_energy - noetheris_energy
    return {
        "assignment": {variable: normalized[variable] for variable in model.variables},
        "noetheris_energy": noetheris_energy,
        "ocean_energy": ocean_energy,
        "difference": difference,
        "agreement": abs(difference) <= 1e-9,
    }


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
