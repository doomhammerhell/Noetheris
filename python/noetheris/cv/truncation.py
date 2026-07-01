from __future__ import annotations

import numpy as np

from noetheris.cv.linalg import density_matrix
from noetheris.cv.operators import annihilation, creation


def commutator_boundary_profile(k: int) -> dict[str, float]:
    a = annihilation(k)
    commutator = a @ creation(k) - creation(k) @ a
    deviation = commutator - np.eye(k, dtype=complex)
    return {
        "cutoff": float(k),
        "operator_norm": float(np.linalg.norm(deviation, ord=2)),
        "frobenius_norm": float(np.linalg.norm(deviation)),
        "boundary_diagonal": float(np.real(commutator[-1, -1])),
    }


def restricted_commutator_error(k: int, m: int) -> float:
    if m < 1 or m > k:
        raise ValueError("restricted subspace dimension must satisfy 1 <= m <= k")
    a = annihilation(k)
    commutator = a @ creation(k) - creation(k) @ a
    restricted = commutator[:m, :m] - np.eye(m, dtype=complex)
    return float(np.linalg.norm(restricted))


def boundary_population(state_or_rho: np.ndarray, k: int) -> float:
    rho = density_matrix(state_or_rho)
    if rho.shape != (k, k):
        raise ValueError("state dimension does not match cutoff")
    return float(np.real(rho[-1, -1]))
