from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping


@dataclass(frozen=True)
class BoolExpr:
    op: str
    args: tuple["BoolExpr", ...] = ()
    name: str | None = None

    @staticmethod
    def var(name: str) -> "BoolExpr":
        return BoolExpr("var", name=name)

    @staticmethod
    def const(value: bool) -> "BoolExpr":
        return BoolExpr("const", name="1" if value else "0")

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        if self.op == "var":
            if self.name not in assignment:
                raise ValueError(f"missing Boolean variable {self.name}")
            return bool(assignment[self.name])
        if self.op == "const":
            return self.name == "1"
        if self.op == "not":
            return not self.args[0].evaluate(assignment)
        if self.op == "and":
            return all(arg.evaluate(assignment) for arg in self.args)
        if self.op == "or":
            return any(arg.evaluate(assignment) for arg in self.args)
        if self.op == "xor":
            value = False
            for arg in self.args:
                value ^= arg.evaluate(assignment)
            return value
        if self.op == "implies":
            return (not self.args[0].evaluate(assignment)) or self.args[1].evaluate(assignment)
        if self.op == "eq":
            values = [arg.evaluate(assignment) for arg in self.args]
            return all(value == values[0] for value in values)
        raise ValueError(f"unsupported Boolean operation {self.op}")

    def variables(self) -> tuple[str, ...]:
        if self.op == "var":
            return (self.name or "",)
        variables: set[str] = set()
        for arg in self.args:
            variables.update(arg.variables())
        return tuple(sorted(variables))


def AND(*args: BoolExpr) -> BoolExpr:
    return BoolExpr("and", tuple(args))


def OR(*args: BoolExpr) -> BoolExpr:
    return BoolExpr("or", tuple(args))


def XOR(*args: BoolExpr) -> BoolExpr:
    return BoolExpr("xor", tuple(args))


def NOT(arg: BoolExpr) -> BoolExpr:
    return BoolExpr("not", (arg,))


def IMPLIES(left: BoolExpr, right: BoolExpr) -> BoolExpr:
    return BoolExpr("implies", (left, right))


def EQ(*args: BoolExpr) -> BoolExpr:
    return BoolExpr("eq", tuple(args))


@dataclass(frozen=True)
class SymbolicGate:
    name: str
    controls: tuple[str, ...]
    targets: tuple[str, ...]


@dataclass(frozen=True)
class OracleCircuit:
    variables: tuple[str, ...]
    expression: BoolExpr
    gates: tuple[SymbolicGate, ...]
    ancilla_count: int

    def truth_table(self) -> dict[str, int]:
        table: dict[str, int] = {}
        for bits in product((False, True), repeat=len(self.variables)):
            assignment = dict(zip(self.variables, bits))
            table["".join("1" if bit else "0" for bit in bits)] = int(
                self.expression.evaluate(assignment)
            )
        return table

    def cost_metrics(self) -> dict[str, int]:
        return {
            "logical_variables": len(self.variables),
            "ancilla_count": self.ancilla_count,
            "gate_count": len(self.gates),
            "depth_estimate": len(self.gates),
        }

    def reversibility_check(self) -> bool:
        return all(gate.targets for gate in self.gates)

    def qasm_like(self) -> str:
        lines = ["OPENQASM-LIKE 0.1;", "qubit target;"]
        for variable in self.variables:
            lines.append(f"qubit {variable};")
        for index in range(self.ancilla_count):
            lines.append(f"qubit ancilla_{index};")
        for gate in self.gates:
            controls = ",".join(gate.controls)
            targets = ",".join(gate.targets)
            lines.append(f"{gate.name} controls[{controls}] targets[{targets}];")
        return "\n".join(lines)


def build_oracle(expression: BoolExpr, *, name: str = "phi") -> OracleCircuit:
    variables = expression.variables()
    gates: list[SymbolicGate] = []
    ancilla_counter = 0

    def lower(expr: BoolExpr) -> str:
        nonlocal ancilla_counter
        if expr.op == "var":
            return expr.name or ""
        if expr.op == "const":
            target = f"ancilla_{ancilla_counter}"
            ancilla_counter += 1
            if expr.name == "1":
                gates.append(SymbolicGate("X", (), (target,)))
            return target
        child_targets = tuple(lower(arg) for arg in expr.args)
        target = f"ancilla_{ancilla_counter}"
        ancilla_counter += 1
        gate_name = {
            "not": "NOT",
            "and": "AND",
            "or": "OR",
            "xor": "XOR",
            "implies": "IMPLIES",
            "eq": "EQ",
        }[expr.op]
        gates.append(SymbolicGate(gate_name, child_targets, (target,)))
        return target

    predicate_wire = lower(expression)
    gates.append(SymbolicGate(f"O_{name}", (predicate_wire,), ("target",)))
    return OracleCircuit(
        variables=variables,
        expression=expression,
        gates=tuple(gates),
        ancilla_count=ancilla_counter,
    )
