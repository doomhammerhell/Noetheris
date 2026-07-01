from __future__ import annotations

import numpy as np

from noetheris.cv.linalg import density_matrix
from noetheris.cv.operators import momentum, position


def quadrature_means_from_state(state_or_rho: np.ndarray) -> dict[str, float]:
    rho = density_matrix(state_or_rho)
    k = rho.shape[0]
    q = position(k)
    p = momentum(k)
    return {
        "q": float(np.real(np.trace(rho @ q))),
        "p": float(np.real(np.trace(rho @ p))),
    }


def quadrature_covariance_from_state(state_or_rho: np.ndarray) -> list[list[float]]:
    rho = density_matrix(state_or_rho)
    k = rho.shape[0]
    ops = [position(k), momentum(k)]
    means = [np.trace(rho @ op) for op in ops]
    covariance = np.zeros((2, 2), dtype=float)
    for i, left in enumerate(ops):
        for j, right in enumerate(ops):
            sym = 0.5 * (left @ right + right @ left)
            covariance[i, j] = float(np.real(np.trace(rho @ sym) - means[i] * means[j]))
    return covariance.tolist()


def density_fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    rho_value = density_matrix(rho)
    sigma_value = density_matrix(sigma)
    eigvals, eigvecs = np.linalg.eigh(rho_value)
    sqrt_rho = eigvecs @ np.diag(np.sqrt(np.maximum(eigvals, 0.0))) @ eigvecs.conj().T
    product = sqrt_rho @ sigma_value @ sqrt_rho
    values = np.linalg.eigvalsh(product)
    return float(np.real(np.sum(np.sqrt(np.maximum(values, 0.0))) ** 2))
