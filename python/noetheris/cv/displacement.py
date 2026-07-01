from __future__ import annotations

import numpy as np

from noetheris.cv.linalg import matrix_exponential
from noetheris.cv.operators import annihilation, momentum, position


def displacement(k: int, alpha: complex) -> np.ndarray:
    a = annihilation(k)
    generator = alpha * a.conj().T - np.conjugate(alpha) * a
    return matrix_exponential(generator)


def position_displacement(k: int, alpha: float) -> np.ndarray:
    return matrix_exponential(-1j * float(alpha) * momentum(k))


def momentum_displacement(k: int, beta: float) -> np.ndarray:
    return matrix_exponential(1j * float(beta) * position(k))


def local_weyl_residual(k: int, alpha: float, beta: float, state: np.ndarray) -> float:
    q_shift = position_displacement(k, alpha)
    p_shift = momentum_displacement(k, beta)
    phase = np.exp(1j * alpha * beta)
    lhs = q_shift @ p_shift @ state
    rhs = phase * (p_shift @ q_shift @ state)
    return float(np.linalg.norm(lhs - rhs))
