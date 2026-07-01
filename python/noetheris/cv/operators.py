from __future__ import annotations

import numpy as np


def annihilation(k: int) -> np.ndarray:
    _validate_cutoff(k)
    op = np.zeros((k, k), dtype=complex)
    for n in range(1, k):
        op[n - 1, n] = np.sqrt(n)
    return op


def creation(k: int) -> np.ndarray:
    return annihilation(k).conj().T


def number(k: int) -> np.ndarray:
    _validate_cutoff(k)
    return np.diag(np.arange(k, dtype=float)).astype(complex)


def position(k: int) -> np.ndarray:
    a = annihilation(k)
    return (a + a.conj().T) / np.sqrt(2.0)


def momentum(k: int) -> np.ndarray:
    a = annihilation(k)
    return (a - a.conj().T) / (1j * np.sqrt(2.0))


def parity(k: int) -> np.ndarray:
    _validate_cutoff(k)
    return np.diag([1 if n % 2 == 0 else -1 for n in range(k)]).astype(complex)


def _validate_cutoff(k: int) -> None:
    if k < 2:
        raise ValueError("Fock cutoff must be at least 2")
