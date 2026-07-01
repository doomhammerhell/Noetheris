from __future__ import annotations

import pytest

from noetheris.lattice import LatticeInstance, analyze_lattice


def test_toy_lattice_analysis() -> None:
    instance = LatticeInstance(basis=((2, 1), (1, 3)), target=(3, 4))
    analysis = analyze_lattice(instance, coefficient_bound=2)
    assert analysis.distance == 0.0
    assert analysis.nearest_vector == (3, 4)


def test_toy_lattice_boundary() -> None:
    instance = LatticeInstance(
        basis=((1, 0, 0, 0, 0),),
        target=(1, 0, 0, 0, 0),
    )
    with pytest.raises(ValueError, match="toy lattice analysis"):
        analyze_lattice(instance)

