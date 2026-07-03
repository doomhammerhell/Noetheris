from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Mapping


@dataclass(frozen=True)
class QuadraticTerm:
    left: str
    right: str
    coefficient: float


@dataclass(frozen=True)
class QuboSolution:
    assignment: dict[str, bool]
    energy: float


@dataclass(frozen=True)
class IsingCoupling:
    left: str
    right: str
    coefficient: float


@dataclass(frozen=True)
class HamiltonianTerm:
    operator: str
    coefficient: float


@dataclass(frozen=True)
class IsingModel:
    variables: tuple[str, ...]
    fields: dict[str, float]
    couplings: tuple[IsingCoupling, ...]
    offset: float

    def evaluate(self, spins: Mapping[str, int]) -> float:
        energy = self.offset
        for variable, field in self.fields.items():
            spin = _spin(spins.get(variable, 1), variable)
            energy += field * spin
        for coupling in self.couplings:
            left = _spin(spins.get(coupling.left, 1), coupling.left)
            right = _spin(spins.get(coupling.right, 1), coupling.right)
            energy += coupling.coefficient * left * right
        return energy

    def hamiltonian_terms(self) -> tuple[HamiltonianTerm, ...]:
        terms = [HamiltonianTerm("I", self.offset)]
        for variable in self.variables:
            coefficient = self.fields.get(variable, 0.0)
            if coefficient != 0.0:
                terms.append(HamiltonianTerm(f"Z[{variable}]", coefficient))
        for coupling in self.couplings:
            if coupling.coefficient != 0.0:
                terms.append(
                    HamiltonianTerm(
                        f"Z[{coupling.left}] Z[{coupling.right}]",
                        coupling.coefficient,
                    )
                )
        return tuple(terms)

    def to_dict(self) -> dict[str, object]:
        return {
            "variables": list(self.variables),
            "fields": dict(sorted(self.fields.items())),
            "couplings": [
                {
                    "left": coupling.left,
                    "right": coupling.right,
                    "coefficient": coupling.coefficient,
                }
                for coupling in self.couplings
            ],
            "offset": self.offset,
            "hamiltonian_terms": [
                {"operator": term.operator, "coefficient": term.coefficient}
                for term in self.hamiltonian_terms()
            ],
        }


@dataclass
class QuboModel:
    variables: list[str]
    linear: dict[str, float] = field(default_factory=dict)
    quadratic: list[QuadraticTerm] = field(default_factory=list)
    constant: float = 0.0

    def validate(self) -> None:
        if len(set(self.variables)) != len(self.variables):
            raise ValueError("QUBO variables must be unique")
        known = set(self.variables)
        for variable, coefficient in self.linear.items():
            if variable not in known:
                raise ValueError(f"linear term references unknown variable {variable}")
            if not _finite(coefficient):
                raise ValueError(f"linear coefficient for {variable} is not finite")
        for term in self.quadratic:
            if term.left not in known or term.right not in known:
                raise ValueError(
                    f"quadratic term {term.left} * {term.right} references unknown variable"
                )
            if not _finite(term.coefficient):
                raise ValueError(
                    f"quadratic coefficient for {term.left} * {term.right} is not finite"
                )

    def evaluate(self, assignment: Mapping[str, bool]) -> float:
        expected = set(self.variables)
        provided = set(assignment)
        missing = sorted(expected - provided)
        unknown = sorted(provided - expected)
        if missing:
            raise ValueError(f"assignment missing variables: {', '.join(missing)}")
        if unknown:
            raise ValueError(f"assignment contains unknown variables: {', '.join(unknown)}")
        energy = self.constant
        for variable, coefficient in self.linear.items():
            if assignment[variable]:
                energy += coefficient
        for term in self.quadratic:
            if assignment[term.left] and assignment[term.right]:
                energy += term.coefficient
        return energy

    def to_ising(self) -> IsingModel:
        self.validate()
        canonical = self.canonicalized()
        fields = {variable: 0.0 for variable in self.variables}
        offset = canonical.constant
        couplings: list[IsingCoupling] = []
        for variable, coefficient in canonical.linear.items():
            offset += coefficient / 2.0
            fields[variable] -= coefficient / 2.0
        for term in canonical.quadratic:
            offset += term.coefficient / 4.0
            fields[term.left] -= term.coefficient / 4.0
            fields[term.right] -= term.coefficient / 4.0
            couplings.append(
                IsingCoupling(
                    left=term.left,
                    right=term.right,
                    coefficient=term.coefficient / 4.0,
                )
            )
        return IsingModel(
            variables=tuple(self.variables),
            fields=fields,
            couplings=tuple(couplings),
            offset=offset,
        )

    def assignment_to_spins(self, assignment: Mapping[str, bool]) -> dict[str, int]:
        expected = set(self.variables)
        provided = set(assignment)
        missing = sorted(expected - provided)
        unknown = sorted(provided - expected)
        if missing:
            raise ValueError(f"assignment missing variables: {', '.join(missing)}")
        if unknown:
            raise ValueError(f"assignment contains unknown variables: {', '.join(unknown)}")
        return {
            variable: -1 if assignment[variable] else 1
            for variable in self.variables
        }

    def canonicalized(self) -> "QuboModel":
        self.validate()
        linear = {variable: 0.0 for variable in self.variables}
        for variable, coefficient in self.linear.items():
            linear[variable] += coefficient
        pair_coefficients: dict[tuple[str, str], float] = {}
        variable_order = {variable: idx for idx, variable in enumerate(self.variables)}
        for term in self.quadratic:
            if term.left == term.right:
                linear[term.left] += term.coefficient
                continue
            left, right = sorted(
                (term.left, term.right),
                key=lambda variable: variable_order[variable],
            )
            pair_coefficients[(left, right)] = (
                pair_coefficients.get((left, right), 0.0) + term.coefficient
            )
        quadratic = [
            QuadraticTerm(left, right, coefficient)
            for (left, right), coefficient in sorted(
                pair_coefficients.items(),
                key=lambda item: (variable_order[item[0][0]], variable_order[item[0][1]]),
            )
            if coefficient != 0.0
        ]
        return QuboModel(
            variables=list(self.variables),
            linear={
                variable: coefficient
                for variable, coefficient in linear.items()
                if coefficient != 0.0
            },
            quadratic=quadratic,
            constant=self.constant,
        )

    def exhaustive_solve(self) -> QuboSolution:
        self.validate()
        if len(self.variables) > 24:
            raise ValueError("local exhaustive QUBO solver is bounded to 24 variables")
        best: QuboSolution | None = None
        for mask in range(1 << len(self.variables)):
            assignment = {
                variable: bool((mask >> idx) & 1)
                for idx, variable in enumerate(self.variables)
            }
            energy = self.evaluate(assignment)
            if best is None or energy < best.energy:
                best = QuboSolution(assignment=assignment, energy=energy)
        if best is None:
            raise ValueError("QUBO model has no assignments")
        return best

    @classmethod
    def exactly_one_choice(
        cls, variable_costs: Mapping[str, float], *, penalty: float
    ) -> "QuboModel":
        variables = sorted(variable_costs)
        linear = {
            variable: float(variable_costs[variable]) - penalty for variable in variables
        }
        quadratic = [
            QuadraticTerm(left=a, right=b, coefficient=2.0 * penalty)
            for a, b in combinations(variables, 2)
        ]
        return cls(
            variables=variables,
            linear=linear,
            quadratic=quadratic,
            constant=penalty,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "variables": list(self.variables),
            "linear": dict(sorted(self.linear.items())),
            "quadratic": [
                {
                    "left": term.left,
                    "right": term.right,
                    "coefficient": term.coefficient,
                }
                for term in self.quadratic
            ],
            "constant": self.constant,
        }


def _finite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))


def _spin(value: int, variable: str) -> int:
    if value not in (-1, 1):
        raise ValueError(f"spin for {variable} must be -1 or +1")
    return value
