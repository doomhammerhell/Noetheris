from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from typing import Any

from noetheris.qubo import QuboModel


@dataclass(frozen=True)
class LatticeInstance:
    basis: tuple[tuple[int, ...], ...]
    target: tuple[int, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "LatticeInstance":
        return cls(
            basis=tuple(tuple(int(item) for item in row) for row in value["basis"]),
            target=tuple(int(item) for item in value["target"]),
        )

    def validate(self) -> None:
        if not self.basis:
            raise ValueError("basis must not be empty")
        dimension = len(self.target)
        if dimension > 4 or len(self.basis) > 4:
            raise ValueError("toy lattice analysis is bounded to dimension and rank at most 4")
        for row in self.basis:
            if len(row) != dimension:
                raise ValueError("basis vectors must match target dimension")


@dataclass(frozen=True)
class LatticeAnalysis:
    nearest_coefficients: tuple[int, ...]
    nearest_vector: tuple[int, ...]
    distance: float
    noise_sensitivity: float
    qubo: QuboModel

    def to_dict(self) -> dict[str, Any]:
        return {
            "nearest_coefficients": list(self.nearest_coefficients),
            "nearest_vector": list(self.nearest_vector),
            "distance": self.distance,
            "noise_sensitivity": self.noise_sensitivity,
            "qubo": self.qubo.to_dict(),
        }


def analyze_lattice(instance: LatticeInstance, *, coefficient_bound: int = 2) -> LatticeAnalysis:
    instance.validate()
    if coefficient_bound > 3:
        raise ValueError("coefficient bound is intentionally limited for toy analysis")
    coefficients, vector, distance = _nearest_vector(instance, coefficient_bound)
    sensitivity = _noise_sensitivity(instance, coefficient_bound, distance)
    qubo = _toy_qubo(instance, coefficient_bound)
    return LatticeAnalysis(
        nearest_coefficients=coefficients,
        nearest_vector=vector,
        distance=distance,
        noise_sensitivity=sensitivity,
        qubo=qubo,
    )


def _nearest_vector(
    instance: LatticeInstance, coefficient_bound: int
) -> tuple[tuple[int, ...], tuple[int, ...], float]:
    best: tuple[tuple[int, ...], tuple[int, ...], float] | None = None
    rank = len(instance.basis)
    for coefficients in product(
        range(-coefficient_bound, coefficient_bound + 1), repeat=rank
    ):
        vector = tuple(
            sum(coefficients[row] * instance.basis[row][col] for row in range(rank))
            for col in range(len(instance.target))
        )
        distance = math.sqrt(
            sum((vector[idx] - instance.target[idx]) ** 2 for idx in range(len(vector)))
        )
        candidate = (tuple(coefficients), vector, distance)
        if best is None or candidate[2] < best[2]:
            best = candidate
    if best is None:
        raise ValueError("lattice search produced no candidates")
    return best


def _noise_sensitivity(
    instance: LatticeInstance, coefficient_bound: int, base_distance: float
) -> float:
    deltas: list[float] = []
    for idx in range(len(instance.target)):
        for direction in (-1, 1):
            target = list(instance.target)
            target[idx] += direction
            perturbed = LatticeInstance(basis=instance.basis, target=tuple(target))
            _, _, distance = _nearest_vector(perturbed, coefficient_bound)
            deltas.append(abs(distance - base_distance))
    return sum(deltas) / len(deltas) if deltas else 0.0


def _toy_qubo(instance: LatticeInstance, coefficient_bound: int) -> QuboModel:
    variables: list[str] = []
    linear: dict[str, float] = {}
    for row in range(len(instance.basis)):
        for value in range(-coefficient_bound, coefficient_bound + 1):
            variable = f"c_{row}_{value}"
            variables.append(variable)
            linear[variable] = abs(value) * 0.1
    return QuboModel(variables=variables, linear=linear, constant=0.0)

