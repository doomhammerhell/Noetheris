from __future__ import annotations

import numpy as np

from noetheris.cv.linalg import density_matrix


def partial_trace(rho: np.ndarray, dims: tuple[int, ...], keep: tuple[int, ...]) -> np.ndarray:
    value = density_matrix(rho)
    keep_set = set(keep)
    if value.shape != (int(np.prod(dims)), int(np.prod(dims))):
        raise ValueError("density matrix dimension does not match subsystem dimensions")
    tensor = value.reshape(*dims, *dims)
    trace_over = [idx for idx in range(len(dims)) if idx not in keep_set]
    for idx in reversed(trace_over):
        tensor = np.trace(tensor, axis1=idx, axis2=idx + len(dims))
    kept_dims = [dims[idx] for idx in keep]
    size = int(np.prod(kept_dims))
    return tensor.reshape(size, size)


def partial_transpose(rho: np.ndarray, dims: tuple[int, ...], subsystem: int) -> np.ndarray:
    value = density_matrix(rho)
    n = len(dims)
    tensor = value.reshape(*dims, *dims)
    axes = list(range(2 * n))
    axes[subsystem], axes[subsystem + n] = axes[subsystem + n], axes[subsystem]
    return np.transpose(tensor, axes).reshape(value.shape)


def negativity(rho: np.ndarray, dims: tuple[int, ...], subsystem: int) -> float:
    pt = partial_transpose(rho, dims, subsystem)
    eigenvalues = np.linalg.eigvals(pt)
    return float((np.sum(np.abs(eigenvalues)) - 1.0) / 2.0)


def logarithmic_negativity(rho: np.ndarray, dims: tuple[int, ...], subsystem: int) -> float:
    return float(np.log2(2.0 * negativity(rho, dims, subsystem) + 1.0))


def von_neumann_entropy(rho: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(density_matrix(rho))
    positive = eigenvalues[eigenvalues > 1e-12]
    return float(-np.sum(positive * np.log2(positive)))
