from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Mapping

from noetheris.certificates import stable_problem_hash


@dataclass(frozen=True)
class RiskAnnotation:
    category: str
    weight: float
    harvest_now_decrypt_later: bool = False

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RiskAnnotation":
        return cls(
            category=str(value["category"]),
            weight=float(value["weight"]),
            harvest_now_decrypt_later=bool(value.get("harvest_now_decrypt_later", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "weight": self.weight,
            "harvest_now_decrypt_later": self.harvest_now_decrypt_later,
        }


@dataclass(frozen=True)
class CryptoAsset:
    algorithm: str
    key_lifetime_days: int = 0
    compliance_required: bool = False

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CryptoAsset":
        return cls(
            algorithm=str(value["algorithm"]),
            key_lifetime_days=int(value.get("key_lifetime_days", 0)),
            compliance_required=bool(value.get("compliance_required", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "key_lifetime_days": self.key_lifetime_days,
            "compliance_required": self.compliance_required,
        }


@dataclass(frozen=True)
class MigrationCandidate:
    candidate_id: str
    target_algorithm: str
    migration_cost: float
    downtime: float
    risk_reduction: float
    hybrid: bool = False
    compliance_satisfies: bool = False
    incompatible_with: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "MigrationCandidate":
        return cls(
            candidate_id=str(value["candidate_id"]),
            target_algorithm=str(value["target_algorithm"]),
            migration_cost=float(value["migration_cost"]),
            downtime=float(value.get("downtime", 0.0)),
            risk_reduction=float(value["risk_reduction"]),
            hybrid=bool(value.get("hybrid", False)),
            compliance_satisfies=bool(value.get("compliance_satisfies", False)),
            incompatible_with=tuple(str(item) for item in value.get("incompatible_with", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "target_algorithm": self.target_algorithm,
            "migration_cost": self.migration_cost,
            "downtime": self.downtime,
            "risk_reduction": self.risk_reduction,
            "hybrid": self.hybrid,
            "compliance_satisfies": self.compliance_satisfies,
            "incompatible_with": list(self.incompatible_with),
        }


@dataclass(frozen=True)
class StructuralNode:
    node_id: str
    kind: str
    label: str
    risk: RiskAnnotation | None = None
    crypto: CryptoAsset | None = None
    migration_candidates: tuple[MigrationCandidate, ...] = ()
    annotations: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "StructuralNode":
        return cls(
            node_id=str(value["id"]),
            kind=str(value["kind"]),
            label=str(value.get("label", value["id"])),
            risk=RiskAnnotation.from_dict(value["risk"]) if value.get("risk") else None,
            crypto=CryptoAsset.from_dict(value["crypto"]) if value.get("crypto") else None,
            migration_candidates=tuple(
                MigrationCandidate.from_dict(item)
                for item in value.get("migration_candidates", ())
            ),
            annotations={str(k): str(v) for k, v in value.get("annotations", {}).items()},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.node_id,
            "kind": self.kind,
            "label": self.label,
            "risk": self.risk.to_dict() if self.risk else None,
            "crypto": self.crypto.to_dict() if self.crypto else None,
            "migration_candidates": [
                candidate.to_dict() for candidate in self.migration_candidates
            ],
            "annotations": dict(sorted(self.annotations.items())),
        }


@dataclass(frozen=True)
class StructuralEdge:
    edge_id: str
    source: str
    target: str
    kind: str
    cost: float = 0.0
    adversarial: bool = False
    annotations: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "StructuralEdge":
        return cls(
            edge_id=str(value["id"]),
            source=str(value["source"]),
            target=str(value["target"]),
            kind=str(value["kind"]),
            cost=float(value.get("cost", 0.0)),
            adversarial=bool(value.get("adversarial", False)),
            annotations={str(k): str(v) for k, v in value.get("annotations", {}).items()},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "cost": self.cost,
            "adversarial": self.adversarial,
            "annotations": dict(sorted(self.annotations.items())),
        }


@dataclass(frozen=True)
class Constraint:
    constraint_id: str
    kind: str
    expression: str
    weight: float
    nodes: tuple[str, ...] = ()
    edges: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Constraint":
        return cls(
            constraint_id=str(value["id"]),
            kind=str(value["kind"]),
            expression=str(value["expression"]),
            weight=float(value.get("weight", 1.0)),
            nodes=tuple(str(item) for item in value.get("nodes", ())),
            edges=tuple(str(item) for item in value.get("edges", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.constraint_id,
            "kind": self.kind,
            "expression": self.expression,
            "weight": self.weight,
            "nodes": list(self.nodes),
            "edges": list(self.edges),
        }


@dataclass(frozen=True)
class Objective:
    objective_id: str
    expression: str
    weight: float

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Objective":
        return cls(
            objective_id=str(value["id"]),
            expression=str(value["expression"]),
            weight=float(value.get("weight", 1.0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.objective_id,
            "expression": self.expression,
            "weight": self.weight,
        }


@dataclass(frozen=True)
class AdversaryAction:
    action_id: str
    label: str
    budget_cost: float
    edge_ids: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "AdversaryAction":
        return cls(
            action_id=str(value["id"]),
            label=str(value["label"]),
            budget_cost=float(value.get("budget_cost", 1.0)),
            edge_ids=tuple(str(item) for item in value.get("edge_ids", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.action_id,
            "label": self.label,
            "budget_cost": self.budget_cost,
            "edge_ids": list(self.edge_ids),
        }


@dataclass(frozen=True)
class WitnessAssignment:
    variables: Mapping[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {"variables": dict(sorted(self.variables.items()))}


@dataclass(frozen=True)
class StructuralSystem:
    system_id: str
    version: str
    problem_type: str
    nodes: tuple[StructuralNode, ...]
    edges: tuple[StructuralEdge, ...]
    constraints: tuple[Constraint, ...] = ()
    invariants: tuple[Constraint, ...] = ()
    objectives: tuple[Objective, ...] = ()
    adversary_actions: tuple[AdversaryAction, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "StructuralSystem":
        return cls(
            system_id=str(value["system_id"]),
            version=str(value.get("version", "0.1.0")),
            problem_type=str(value["problem_type"]),
            nodes=tuple(StructuralNode.from_dict(item) for item in value.get("nodes", ())),
            edges=tuple(StructuralEdge.from_dict(item) for item in value.get("edges", ())),
            constraints=tuple(
                Constraint.from_dict(item) for item in value.get("constraints", ())
            ),
            invariants=tuple(
                Constraint.from_dict(item) for item in value.get("invariants", ())
            ),
            objectives=tuple(
                Objective.from_dict(item) for item in value.get("objectives", ())
            ),
            adversary_actions=tuple(
                AdversaryAction.from_dict(item)
                for item in value.get("adversary_actions", ())
            ),
            metadata={str(k): str(v) for k, v in value.get("metadata", {}).items()},
        )

    @classmethod
    def from_json_file(cls, path: str | Path) -> "StructuralSystem":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def validate(self) -> None:
        if not self.system_id.strip():
            raise ValueError("structural system id must not be empty")
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("structural node ids must be unique")
        edge_ids = {edge.edge_id for edge in self.edges}
        if len(edge_ids) != len(self.edges):
            raise ValueError("structural edge ids must be unique")
        for edge in self.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise ValueError(f"edge {edge.edge_id} references an unknown endpoint")
            if edge.cost < 0.0 or not _finite(edge.cost):
                raise ValueError(f"edge {edge.edge_id} has invalid cost")
        for node in self.nodes:
            if node.risk and (node.risk.weight < 0.0 or not _finite(node.risk.weight)):
                raise ValueError(f"node {node.node_id} has invalid risk weight")
            for candidate in node.migration_candidates:
                if not 0.0 <= candidate.risk_reduction <= 1.0:
                    raise ValueError(
                        f"candidate {candidate.candidate_id} has invalid risk reduction"
                    )
        for collection in (self.constraints, self.invariants):
            for constraint in collection:
                if constraint.weight < 0.0 or not _finite(constraint.weight):
                    raise ValueError(f"constraint {constraint.constraint_id} has invalid weight")
                for node in constraint.nodes:
                    if node not in node_ids:
                        raise ValueError(
                            f"constraint {constraint.constraint_id} references unknown node"
                        )
                for edge in constraint.edges:
                    if edge not in edge_ids:
                        raise ValueError(
                            f"constraint {constraint.constraint_id} references unknown edge"
                        )
        for objective in self.objectives:
            if not _finite(objective.weight):
                raise ValueError(f"objective {objective.objective_id} has invalid weight")
        for action in self.adversary_actions:
            if action.budget_cost < 0.0 or not _finite(action.budget_cost):
                raise ValueError(f"adversary action {action.action_id} has invalid budget")
            for edge in action.edge_ids:
                if edge not in edge_ids:
                    raise ValueError(
                        f"adversary action {action.action_id} references unknown edge"
                    )

    def canonical_hash(self) -> str:
        self.validate()
        return stable_problem_hash(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_id": self.system_id,
            "version": self.version,
            "problem_type": self.problem_type,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "constraints": [constraint.to_dict() for constraint in self.constraints],
            "invariants": [constraint.to_dict() for constraint in self.invariants],
            "objectives": [objective.to_dict() for objective in self.objectives],
            "adversary_actions": [
                action.to_dict() for action in self.adversary_actions
            ],
            "metadata": dict(sorted(self.metadata.items())),
        }


def _finite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))
