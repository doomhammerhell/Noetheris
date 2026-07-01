from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import cmath
import math
from typing import Iterable, Mapping

from noetheris.qubo import QuboModel


@dataclass(frozen=True)
class QaoaAngles:
    gammas: tuple[float, ...]
    betas: tuple[float, ...]


@dataclass(frozen=True)
class QaoaResult:
    angles: QaoaAngles
    expectation: float
    most_probable_assignment: dict[str, bool]
    most_probable_energy: float
    probabilities: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "angles": {
                "gammas": list(self.angles.gammas),
                "betas": list(self.angles.betas),
            },
            "expectation": self.expectation,
            "most_probable_assignment": dict(self.most_probable_assignment),
            "most_probable_energy": self.most_probable_energy,
            "probabilities": dict(sorted(self.probabilities.items())),
        }


def simulate_qaoa(
    model: QuboModel,
    *,
    gammas: Iterable[float],
    betas: Iterable[float],
) -> QaoaResult:
    model.validate()
    gamma_tuple = tuple(float(gamma) for gamma in gammas)
    beta_tuple = tuple(float(beta) for beta in betas)
    if len(gamma_tuple) != len(beta_tuple):
        raise ValueError("QAOA gamma and beta schedules must have equal length")
    if len(model.variables) > 12:
        raise ValueError("exact QAOA simulator is bounded to 12 variables")
    if not gamma_tuple:
        raise ValueError("QAOA schedule must contain at least one layer")
    dimension = 1 << len(model.variables)
    amplitude = 1.0 / math.sqrt(dimension)
    state = [complex(amplitude, 0.0) for _ in range(dimension)]
    energies = [_energy_for_mask(model, mask) for mask in range(dimension)]
    for gamma, beta in zip(gamma_tuple, beta_tuple):
        for mask, energy in enumerate(energies):
            state[mask] *= cmath.exp(complex(0.0, -gamma * energy))
        _apply_mixer(state, len(model.variables), beta)
    probabilities = {
        _bitstring(mask, len(model.variables)): abs(amplitude) ** 2
        for mask, amplitude in enumerate(state)
    }
    expectation = sum(
        probabilities[_bitstring(mask, len(model.variables))] * energy
        for mask, energy in enumerate(energies)
    )
    most_probable_mask = max(
        range(dimension),
        key=lambda mask: probabilities[_bitstring(mask, len(model.variables))],
    )
    assignment = _assignment_for_mask(model.variables, most_probable_mask)
    return QaoaResult(
        angles=QaoaAngles(gamma_tuple, beta_tuple),
        expectation=expectation,
        most_probable_assignment=assignment,
        most_probable_energy=model.evaluate(assignment),
        probabilities=probabilities,
    )


def grid_search_qaoa_p1(
    model: QuboModel,
    *,
    gamma_values: Iterable[float],
    beta_values: Iterable[float],
) -> QaoaResult:
    best: QaoaResult | None = None
    for gamma, beta in product(tuple(gamma_values), tuple(beta_values)):
        result = simulate_qaoa(model, gammas=(gamma,), betas=(beta,))
        if best is None or result.expectation < best.expectation:
            best = result
    if best is None:
        raise ValueError("QAOA grid search requires non-empty angle grids")
    return best


def expectation_from_probabilities(
    model: QuboModel, probabilities: Mapping[str, float]
) -> float:
    total_probability = sum(probabilities.values())
    if abs(total_probability - 1.0) > 1e-8:
        raise ValueError("probabilities must sum to one")
    expectation = 0.0
    for bitstring, probability in probabilities.items():
        if len(bitstring) != len(model.variables):
            raise ValueError("probability bitstring width does not match QUBO variables")
        assignment = {
            variable: bitstring[idx] == "1"
            for idx, variable in enumerate(model.variables)
        }
        expectation += probability * model.evaluate(assignment)
    return expectation


def _apply_mixer(state: list[complex], width: int, beta: float) -> None:
    cosine = math.cos(beta)
    sine = math.sin(beta)
    for qubit in range(width):
        stride = 1 << qubit
        period = stride << 1
        for base in range(0, len(state), period):
            for offset in range(stride):
                zero_index = base + offset
                one_index = zero_index + stride
                zero = state[zero_index]
                one = state[one_index]
                state[zero_index] = cosine * zero - 1j * sine * one
                state[one_index] = -1j * sine * zero + cosine * one


def _energy_for_mask(model: QuboModel, mask: int) -> float:
    return model.evaluate(_assignment_for_mask(model.variables, mask))


def _assignment_for_mask(variables: list[str], mask: int) -> dict[str, bool]:
    return {
        variable: bool((mask >> idx) & 1)
        for idx, variable in enumerate(variables)
    }


def _bitstring(mask: int, width: int) -> str:
    return "".join("1" if (mask >> idx) & 1 else "0" for idx in range(width))
