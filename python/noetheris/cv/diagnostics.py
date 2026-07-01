from __future__ import annotations

from typing import Any

import numpy as np

from noetheris.certificates import (
    CertificateConstraint,
    EnergyTerm,
    make_certificate,
    validate_certificate,
)
from noetheris.cv.displacement import local_weyl_residual
from noetheris.cv.gkp import approximate_gkp_zero_state, gkp_diagnostics
from noetheris.cv.truncation import boundary_population, commutator_boundary_profile


def run_gkp_diagnostic(*, cutoff: int, delta: float, grid_cutoff: int) -> dict[str, Any]:
    state = approximate_gkp_zero_state(cutoff, delta, grid_cutoff)
    diagnostics = gkp_diagnostics(state)
    diagnostics["boundary_population"] = boundary_population(state, cutoff)
    diagnostics["weyl_residual"] = local_weyl_residual(
        cutoff, 0.05, 0.05, state
    )
    diagnostics["commutator_boundary_norm"] = commutator_boundary_profile(cutoff)[
        "operator_norm"
    ]
    return diagnostics


def cv_diagnostic_certificate(
    *, cutoff: int, delta: float, grid_cutoff: int, seed: int = 0
):
    diagnostics = run_gkp_diagnostic(
        cutoff=cutoff, delta=delta, grid_cutoff=grid_cutoff
    )
    terms = (
        EnergyTerm("boundary_population", 1.0, diagnostics["boundary_population"]),
        EnergyTerm("weyl_residual", 1.0, diagnostics["weyl_residual"]),
        EnergyTerm(
            "stabilizer_defect",
            1.0,
            1.0 - min(1.0, diagnostics["stabilizer_x_abs"]),
        ),
    )
    constraints = [
        CertificateConstraint(
            "finite_diagnostics",
            all(np.isfinite(value) for value in diagnostics.values()),
            "all diagnostic scalar values are finite",
        )
    ]
    certificate = make_certificate(
        problem={
            "cutoff": cutoff,
            "delta": delta,
            "grid_cutoff": grid_cutoff,
            "diagnostics": diagnostics,
        },
        problem_type="cv_gkp_diagnostic",
        algorithm_name="cv_gkp_diagnostic",
        energy_terms=terms,
        selected_variables={},
        witness_assignment=diagnostics,
        satisfied_constraints=tuple(item for item in constraints if item.satisfied),
        violated_constraints=tuple(item for item in constraints if not item.satisfied),
        reproducibility_seed=seed,
        proof_obligations=("finite_diagnostics", "bounded_fock_cutoff_declared"),
    )
    validation = validate_certificate(certificate)
    return {
        "diagnostics": diagnostics,
        "certificate": certificate.to_dict(),
        "certificate_status": validation.status,
    }
