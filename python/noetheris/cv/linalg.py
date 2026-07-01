from __future__ import annotations

import numpy as np


def dagger(matrix: np.ndarray) -> np.ndarray:
    return np.asarray(matrix, dtype=complex).conj().T


def normalize_state(state: np.ndarray) -> np.ndarray:
    vector = np.asarray(state, dtype=complex).reshape(-1)
    norm = np.linalg.norm(vector)
    if norm == 0.0:
        raise ValueError("state norm must be nonzero")
    return vector / norm


def density_matrix(state_or_rho: np.ndarray) -> np.ndarray:
    value = np.asarray(state_or_rho, dtype=complex)
    if value.ndim == 1:
        vector = normalize_state(value)
        return np.outer(vector, vector.conj())
    if value.ndim == 2 and value.shape[0] == value.shape[1]:
        return value
    raise ValueError("input must be a state vector or square density matrix")


def matrix_exponential(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eig(np.asarray(matrix, dtype=complex))
    return vectors @ np.diag(np.exp(values)) @ np.linalg.inv(vectors)


def hermitian_matrix_exponential(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(np.asarray(matrix, dtype=complex))
    return vectors @ np.diag(np.exp(values)) @ dagger(vectors)
