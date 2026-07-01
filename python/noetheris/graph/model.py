from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    cost: float
    adversarial: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Transition":
        return cls(
            source=str(value["from"]),
            target=str(value["to"]),
            cost=float(value.get("cost", 1.0)),
            adversarial=bool(value.get("adversarial", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.source,
            "to": self.target,
            "cost": self.cost,
            "adversarial": self.adversarial,
        }


@dataclass(frozen=True)
class StateGraph:
    states: tuple[str, ...]
    transitions: tuple[Transition, ...]
    forbidden_states: tuple[str, ...] = ()
    forbidden_transitions: tuple[tuple[str, str], ...] = ()
    initial_state: str | None = None
    invariant_name: str = "forbidden_state_unreachable"

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "StateGraph":
        forbidden_transitions = tuple(
            (str(pair[0]), str(pair[1]))
            for pair in value.get("forbidden_transitions", ())
        )
        return cls(
            states=tuple(str(state) for state in value["states"]),
            transitions=tuple(
                Transition.from_dict(transition)
                for transition in value.get("transitions", ())
            ),
            forbidden_states=tuple(
                str(state) for state in value.get("forbidden_states", ())
            ),
            forbidden_transitions=forbidden_transitions,
            initial_state=(
                str(value["initial_state"]) if value.get("initial_state") else None
            ),
            invariant_name=str(
                value.get("invariant_name", "forbidden_state_unreachable")
            ),
        )

    @classmethod
    def from_json_file(cls, path: str | Path) -> "StateGraph":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def validate(self) -> None:
        if not self.states:
            raise ValueError("state graph must contain at least one state")
        if len(set(self.states)) != len(self.states):
            raise ValueError("state graph contains duplicate states")
        known = set(self.states)
        for state in self.states:
            if not state.strip():
                raise ValueError("state names must not be empty")
        if self.initial_state is not None and self.initial_state not in known:
            raise ValueError(f"initial state {self.initial_state} is not declared")
        for transition in self.transitions:
            if transition.source not in known or transition.target not in known:
                raise ValueError(
                    f"transition {transition.source}->{transition.target} references an unknown state"
                )
            if transition.cost < 0.0 or not _finite(transition.cost):
                raise ValueError(
                    f"transition {transition.source}->{transition.target} has invalid cost"
                )
        for state in self.forbidden_states:
            if state not in known:
                raise ValueError(f"forbidden state {state} is not declared")
        for source, target in self.forbidden_transitions:
            if source not in known or target not in known:
                raise ValueError(
                    f"forbidden transition {source}->{target} references an unknown state"
                )

    def outgoing(self, state: str) -> tuple[Transition, ...]:
        return tuple(transition for transition in self.transitions if transition.source == state)

    def violates_invariant(self, path: tuple[str, ...]) -> bool:
        if any(state in self.forbidden_states for state in path):
            return True
        return any(
            (left, right) in self.forbidden_transitions
            for left, right in zip(path, path[1:])
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "states": list(self.states),
            "transitions": [transition.to_dict() for transition in self.transitions],
            "forbidden_states": list(self.forbidden_states),
            "forbidden_transitions": [
                [source, target] for source, target in self.forbidden_transitions
            ],
            "initial_state": self.initial_state,
            "invariant_name": self.invariant_name,
        }


def _finite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))

