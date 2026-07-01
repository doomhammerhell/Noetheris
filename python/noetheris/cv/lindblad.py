from __future__ import annotations

import numpy as np

from noetheris.cv.linalg import dagger, density_matrix
from noetheris.cv.operators import annihilation, number
from noetheris.cv.truncation import boundary_population


def liouvillian(H: np.ndarray, collapse_ops: tuple[np.ndarray, ...]) -> np.ndarray:
    dim = H.shape[0]
    eye = np.eye(dim, dtype=complex)
    generator = -1j * (np.kron(eye, H) - np.kron(H.T, eye))
    for op in collapse_ops:
        op_dag_op = dagger(op) @ op
        generator += np.kron(op.conj(), op)
        generator -= 0.5 * np.kron(eye, op_dag_op)
        generator -= 0.5 * np.kron(op_dag_op.T, eye)
    return generator


def solve_lindblad(
    H: np.ndarray,
    rho0: np.ndarray,
    collapse_ops: tuple[np.ndarray, ...],
    *,
    dt: float,
    steps: int,
) -> np.ndarray:
    rho = density_matrix(rho0).astype(complex)
    for _ in range(steps):
        drho = -1j * (H @ rho - rho @ H)
        for op in collapse_ops:
            drho += op @ rho @ dagger(op)
            drho -= 0.5 * (dagger(op) @ op @ rho + rho @ dagger(op) @ op)
        rho = rho + dt * drho
        rho = 0.5 * (rho + dagger(rho))
        trace = np.trace(rho)
        if abs(trace) > 1e-12:
            rho = rho / trace
    return rho


def photon_loss_channel(k: int, rate: float) -> np.ndarray:
    return np.sqrt(rate) * annihilation(k)


def dephasing_channel(k: int, rate: float) -> np.ndarray:
    return np.sqrt(rate) * number(k)


def leakage_report(rho: np.ndarray, k: int) -> dict[str, float]:
    return {
        "trace": float(np.real(np.trace(density_matrix(rho)))),
        "boundary_population": boundary_population(rho, k),
    }
