from __future__ import annotations

import numpy as np

from noetheris.cv.displacement import position_displacement
from noetheris.cv.linalg import normalize_state
from noetheris.cv.operators import position


def gkp_stabilizer_spacing() -> float:
    """Return the square-lattice GKP stabilizer spacing for [q, p] = i.

    With q = (a + a^dagger) / sqrt(2) and p = (a - a^dagger)/(i sqrt(2)),
    the ideal square-lattice code has logical shifts separated by sqrt(pi)
    and stabilizer translations separated by 2*sqrt(pi).
    """
    return 2.0 * np.sqrt(np.pi)


def approximate_gkp_zero_state(k: int, delta: float, grid_cutoff: int) -> np.ndarray:
    return _approximate_gkp_state(k, delta, grid_cutoff, bit=0)


def approximate_gkp_one_state(k: int, delta: float, grid_cutoff: int) -> np.ndarray:
    return _approximate_gkp_state(k, delta, grid_cutoff, bit=1)


def gkp_stabilizers(k: int) -> tuple[np.ndarray, np.ndarray]:
    scale = gkp_stabilizer_spacing()
    sx = position_displacement(k, scale)
    sp = _momentum_shift(k, scale)
    return sx, sp


def gkp_diagnostics(state: np.ndarray) -> dict[str, float]:
    vector = normalize_state(state)
    k = vector.shape[0]
    sx, sp = gkp_stabilizers(k)
    sx_value = np.vdot(vector, sx @ vector)
    sp_value = np.vdot(vector, sp @ vector)
    return {
        "cutoff": float(k),
        "stabilizer_x_real": float(np.real(sx_value)),
        "stabilizer_x_abs": float(abs(sx_value)),
        "stabilizer_p_real": float(np.real(sp_value)),
        "stabilizer_p_abs": float(abs(sp_value)),
    }


def _approximate_gkp_state(k: int, delta: float, grid_cutoff: int, *, bit: int) -> np.ndarray:
    if delta <= 0.0:
        raise ValueError("delta must be positive")
    vacuum = np.zeros(k, dtype=complex)
    vacuum[0] = 1.0
    state = np.zeros(k, dtype=complex)
    spacing = np.sqrt(np.pi)
    for index in range(-grid_cutoff, grid_cutoff + 1):
        center = (2 * index + bit) * spacing
        envelope = np.exp(-0.5 * (delta * center) ** 2)
        state += envelope * (position_displacement(k, center) @ vacuum)
    return normalize_state(state)


def _momentum_shift(k: int, beta: float) -> np.ndarray:
    from noetheris.cv.linalg import matrix_exponential

    return matrix_exponential(1j * beta * position(k))
