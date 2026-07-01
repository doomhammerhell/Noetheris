from __future__ import annotations

import numpy as np

from noetheris.cv.linalg import matrix_exponential
from noetheris.cv.operators import annihilation


def squeezing(k: int, zeta: complex) -> np.ndarray:
    a = annihilation(k)
    generator = 0.5 * (np.conjugate(zeta) * (a @ a) - zeta * (a.conj().T @ a.conj().T))
    return matrix_exponential(generator)
