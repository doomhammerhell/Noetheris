from __future__ import annotations

import numpy as np

from noetheris.cv import (
    annihilation,
    boundary_population,
    commutator_boundary_profile,
    creation,
    cv_diagnostic_certificate,
    displacement,
    gkp_stabilizer_spacing,
    logarithmic_negativity,
    momentum,
    negativity,
    number,
    partial_transpose,
    photon_loss_channel,
    position,
    restricted_commutator_error,
    solve_lindblad,
    squeezing,
)


def test_fock_operator_dimensions_and_hermiticity() -> None:
    cutoff = 6
    assert annihilation(cutoff).shape == (cutoff, cutoff)
    assert creation(cutoff).shape == (cutoff, cutoff)
    assert number(cutoff).shape == (cutoff, cutoff)
    assert np.allclose(position(cutoff), position(cutoff).conj().T)
    assert np.allclose(momentum(cutoff), momentum(cutoff).conj().T)


def test_truncated_commutator_boundary_profile() -> None:
    profile = commutator_boundary_profile(5)
    assert profile["boundary_diagonal"] < 0.0
    assert restricted_commutator_error(8, 4) < 1e-12


def test_displacement_and_squeezing_are_unitary_numerically() -> None:
    cutoff = 5
    eye = np.eye(cutoff)
    assert np.allclose(displacement(cutoff, 0.1 + 0.2j).conj().T @ displacement(cutoff, 0.1 + 0.2j), eye, atol=1e-9)
    assert np.allclose(squeezing(cutoff, 0.1).conj().T @ squeezing(cutoff, 0.1), eye, atol=1e-9)


def test_gkp_diagnostic_certificate_valid() -> None:
    result = cv_diagnostic_certificate(cutoff=8, delta=0.4, grid_cutoff=1)
    assert result["certificate_status"] == "verified"
    assert 0.0 <= result["diagnostics"]["boundary_population"] <= 1.0
    assert abs(gkp_stabilizer_spacing() - 2.0 * np.sqrt(np.pi)) < 1e-12


def test_partial_transpose_detects_bell_entanglement() -> None:
    bell = np.zeros(4, dtype=complex)
    bell[0] = 1 / np.sqrt(2)
    bell[3] = 1 / np.sqrt(2)
    rho = np.outer(bell, bell.conj())
    assert negativity(rho, (2, 2), 1) > 0.49
    assert logarithmic_negativity(rho, (2, 2), 1) > 0.99
    assert np.any(np.linalg.eigvals(partial_transpose(rho, (2, 2), 1)) < -0.49)


def test_lindblad_trace_preservation_small_system() -> None:
    cutoff = 4
    rho0 = np.zeros((cutoff, cutoff), dtype=complex)
    rho0[2, 2] = 1.0
    evolved = solve_lindblad(
        number(cutoff),
        rho0,
        (photon_loss_channel(cutoff, 0.1),),
        dt=0.01,
        steps=10,
    )
    assert abs(np.trace(evolved) - 1.0) < 1e-9
    assert 0.0 <= boundary_population(evolved, cutoff) <= 1.0
