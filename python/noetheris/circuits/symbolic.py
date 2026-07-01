from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable


Predicate = Callable[[tuple[int, ...]], int]


@dataclass(frozen=True)
class TruthTableOracle:
    variables: tuple[str, ...]
    truth_table: dict[tuple[int, ...], int]

    def evaluate(self, bits: tuple[int, ...]) -> int:
        if len(bits) != len(self.variables):
            raise ValueError("input width does not match oracle variables")
        normalized = tuple(1 if bit else 0 for bit in bits)
        return 1 if self.truth_table.get(normalized, 0) else 0


@dataclass(frozen=True)
class SymbolicCircuit:
    variables: tuple[str, ...]
    operations: tuple[str, ...]

    def to_text(self) -> str:
        return "\n".join(self.operations)


@dataclass(frozen=True)
class BooleanOracle:
    variables: tuple[str, ...]
    predicate: Predicate
    name: str = "phi"

    def apply(self, x: tuple[int, ...], y: int) -> tuple[tuple[int, ...], int]:
        if len(x) != len(self.variables):
            raise ValueError("input width does not match oracle variables")
        normalized_x = tuple(1 if bit else 0 for bit in x)
        normalized_y = 1 if y else 0
        return normalized_x, normalized_y ^ (1 if self.predicate(normalized_x) else 0)

    def simulate_all(self) -> dict[tuple[tuple[int, ...], int], tuple[tuple[int, ...], int]]:
        table: dict[tuple[tuple[int, ...], int], tuple[tuple[int, ...], int]] = {}
        for bits in product((0, 1), repeat=len(self.variables)):
            for y in (0, 1):
                table[(bits, y)] = self.apply(bits, y)
        return table

    def symbolic_circuit(self) -> SymbolicCircuit:
        operations = (
            f"allocate input register x[{len(self.variables)}]",
            "allocate target bit y",
            f"compute predicate {self.name}(x)",
            f"apply y <- y xor {self.name}(x)",
            f"uncompute predicate {self.name}(x)",
        )
        return SymbolicCircuit(variables=self.variables, operations=operations)

    def qiskit_export(self) -> tuple[object | None, str]:
        try:
            from qiskit import QuantumCircuit  # type: ignore
        except Exception as exc:
            return None, f"qiskit unavailable: {exc.__class__.__name__}"
        circuit = QuantumCircuit(len(self.variables) + 1, name=f"O_{self.name}")
        circuit.barrier()
        return circuit, "qiskit circuit shell exported without semantic synthesis"

