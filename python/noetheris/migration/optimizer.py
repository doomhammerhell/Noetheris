from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from noetheris.certificates import (
    CertificateConstraint,
    EnergyCertificate,
    EnergyTerm,
    make_certificate,
)
from noetheris.qubo import QuboModel, QuadraticTerm


@dataclass(frozen=True)
class Asset:
    asset_id: str
    name: str
    algorithm: str
    risk_weight: float
    downtime_cost: float
    compliance_required: bool = False
    harvest_now_decrypt_later: bool = False


@dataclass(frozen=True)
class Dependency:
    asset_id: str
    depends_on: str
    kind: str


@dataclass(frozen=True)
class MigrationCandidate:
    candidate_id: str
    asset_id: str
    target_algorithm: str
    migration_cost: float
    downtime: float
    risk_reduction: float
    hybrid: bool = False
    compliance_satisfies: bool = False
    incompatible_with: tuple[str, ...] = ()


@dataclass(frozen=True)
class MigrationWeights:
    risk: float = 10.0
    cost: float = 1.0
    downtime: float = 1.5
    incompatibility: float = 100.0
    compliance: float = 80.0
    dependency: float = 60.0
    one_candidate: float = 500.0


@dataclass(frozen=True)
class MigrationGraph:
    assets: tuple[Asset, ...]
    dependencies: tuple[Dependency, ...]
    candidates: tuple[MigrationCandidate, ...]

    @classmethod
    def from_json_file(cls, path: str | Path) -> "MigrationGraph":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "MigrationGraph":
        return cls(
            assets=tuple(
                Asset(
                    asset_id=str(asset["id"]),
                    name=str(asset["name"]),
                    algorithm=str(asset["algorithm"]),
                    risk_weight=float(asset["risk_weight"]),
                    downtime_cost=float(asset.get("downtime_cost", 0.0)),
                    compliance_required=bool(asset.get("compliance_required", False)),
                    harvest_now_decrypt_later=bool(
                        asset.get("harvest_now_decrypt_later", False)
                    ),
                )
                for asset in value["assets"]
            ),
            dependencies=tuple(
                Dependency(
                    asset_id=str(edge["asset"]),
                    depends_on=str(edge["depends_on"]),
                    kind=str(edge.get("kind", "operational")),
                )
                for edge in value.get("dependencies", ())
            ),
            candidates=tuple(
                MigrationCandidate(
                    candidate_id=str(candidate["id"]),
                    asset_id=str(candidate["asset"]),
                    target_algorithm=str(candidate["target_algorithm"]),
                    migration_cost=float(candidate["migration_cost"]),
                    downtime=float(candidate.get("downtime", 0.0)),
                    risk_reduction=float(candidate["risk_reduction"]),
                    hybrid=bool(candidate.get("hybrid", False)),
                    compliance_satisfies=bool(
                        candidate.get("compliance_satisfies", False)
                    ),
                    incompatible_with=tuple(
                        str(item) for item in candidate.get("incompatible_with", ())
                    ),
                )
                for candidate in value["migration_candidates"]
            ),
        )

    def validate(self) -> None:
        asset_ids = {asset.asset_id for asset in self.assets}
        if len(asset_ids) != len(self.assets):
            raise ValueError("asset identifiers must be unique")
        for asset in self.assets:
            if asset.risk_weight < 0.0:
                raise ValueError(f"asset {asset.asset_id} has negative risk weight")
        candidate_ids = {candidate.candidate_id for candidate in self.candidates}
        if len(candidate_ids) != len(self.candidates):
            raise ValueError("candidate identifiers must be unique")
        for candidate in self.candidates:
            if candidate.asset_id not in asset_ids:
                raise ValueError(f"candidate {candidate.candidate_id} references unknown asset")
            if not 0.0 <= candidate.risk_reduction <= 1.0:
                raise ValueError(
                    f"candidate {candidate.candidate_id} has invalid risk reduction"
                )
        for dependency in self.dependencies:
            if dependency.asset_id not in asset_ids or dependency.depends_on not in asset_ids:
                raise ValueError("dependency references unknown asset")

    def to_dict(self) -> dict[str, Any]:
        return {
            "assets": [
                {
                    "id": asset.asset_id,
                    "name": asset.name,
                    "algorithm": asset.algorithm,
                    "risk_weight": asset.risk_weight,
                    "downtime_cost": asset.downtime_cost,
                    "compliance_required": asset.compliance_required,
                    "harvest_now_decrypt_later": asset.harvest_now_decrypt_later,
                }
                for asset in self.assets
            ],
            "dependencies": [
                {
                    "asset": dependency.asset_id,
                    "depends_on": dependency.depends_on,
                    "kind": dependency.kind,
                }
                for dependency in self.dependencies
            ],
            "migration_candidates": [
                {
                    "id": candidate.candidate_id,
                    "asset": candidate.asset_id,
                    "target_algorithm": candidate.target_algorithm,
                    "migration_cost": candidate.migration_cost,
                    "downtime": candidate.downtime,
                    "risk_reduction": candidate.risk_reduction,
                    "hybrid": candidate.hybrid,
                    "compliance_satisfies": candidate.compliance_satisfies,
                    "incompatible_with": list(candidate.incompatible_with),
                }
                for candidate in self.candidates
            ],
        }


@dataclass(frozen=True)
class MigrationPlan:
    ordered_steps: tuple[MigrationCandidate, ...]
    residual_risk: float
    blocking_dependencies: tuple[Dependency, ...]
    energy: float
    qubo: QuboModel
    certificate: EnergyCertificate

    def to_dict(self) -> dict[str, Any]:
        return {
            "ordered_steps": [
                {
                    "candidate_id": candidate.candidate_id,
                    "asset_id": candidate.asset_id,
                    "target_algorithm": candidate.target_algorithm,
                    "hybrid": candidate.hybrid,
                }
                for candidate in self.ordered_steps
            ],
            "residual_risk": self.residual_risk,
            "blocking_dependencies": [
                {
                    "asset": dependency.asset_id,
                    "depends_on": dependency.depends_on,
                    "kind": dependency.kind,
                }
                for dependency in self.blocking_dependencies
            ],
            "energy": self.energy,
            "qubo": self.qubo.to_dict(),
            "certificate": self.certificate.to_dict(),
        }


def optimize_migration_plan(
    graph: MigrationGraph,
    *,
    weights: MigrationWeights = MigrationWeights(),
    seed: int = 0,
) -> MigrationPlan:
    graph.validate()
    qubo = _build_migration_qubo(graph, weights)
    solution = qubo.exhaustive_solve()
    selected = tuple(
        candidate
        for candidate in graph.candidates
        if solution.assignment.get(candidate.candidate_id, False)
    )
    selected_by_asset = {candidate.asset_id: candidate for candidate in selected}
    ordered = _order_candidates(graph, selected)
    blocking = tuple(
        dependency
        for dependency in graph.dependencies
        if dependency.asset_id in selected_by_asset
        and dependency.depends_on not in selected_by_asset
    )
    residual_risk = _residual_risk(graph, selected_by_asset)
    terms = _qubo_energy_terms(qubo, solution.assignment)
    multiplicity_violations = _candidate_multiplicity_violations(selected)
    satisfied_constraints: list[CertificateConstraint] = []
    violated_constraints: list[CertificateConstraint] = []
    if multiplicity_violations:
        violated_constraints.append(
            CertificateConstraint(
                "one_candidate_per_asset",
                False,
                "selected assignment contains multiple candidates for an asset",
            )
        )
    else:
        satisfied_constraints.append(
            CertificateConstraint(
                "one_candidate_per_asset",
                True,
                "selected assignment contains at most one candidate per asset",
            )
        )
    if blocking:
        violated_constraints.append(
            CertificateConstraint(
                "dependencies_respected",
                False,
                "selected assets include dependencies that are not selected",
            )
        )
    else:
        satisfied_constraints.append(
            CertificateConstraint(
                "dependencies_respected",
                True,
                "selected migrations include required selected dependencies",
            )
        )
    compliance_gap = _compliance_gap(graph, selected_by_asset)
    if compliance_gap:
        violated_constraints.append(
            CertificateConstraint(
                "compliance_requirements",
                False,
                "one or more compliance-required assets lack a satisfying migration",
            )
        )
    else:
        satisfied_constraints.append(
            CertificateConstraint(
                "compliance_requirements",
                True,
                "all compliance-required assets have satisfying migrations",
            )
        )
    certificate = make_certificate(
        problem={"migration_graph": graph.to_dict(), "weights": weights.__dict__},
        algorithm_name="post_quantum_migration_optimizer",
        energy_terms=terms,
        selected_variables=solution.assignment,
        satisfied_constraints=tuple(satisfied_constraints),
        violated_constraints=tuple(violated_constraints),
        reproducibility_seed=seed,
    )
    return MigrationPlan(
        ordered_steps=ordered,
        residual_risk=residual_risk,
        blocking_dependencies=blocking,
        energy=solution.energy,
        qubo=qubo,
        certificate=certificate,
    )


def _build_migration_qubo(graph: MigrationGraph, weights: MigrationWeights) -> QuboModel:
    variables = [candidate.candidate_id for candidate in graph.candidates]
    linear = {variable: 0.0 for variable in variables}
    quadratic: list[QuadraticTerm] = []
    assets = {asset.asset_id: asset for asset in graph.assets}
    for candidate in graph.candidates:
        asset = assets[candidate.asset_id]
        risk_delta = -weights.risk * asset.risk_weight * candidate.risk_reduction
        cost = weights.cost * candidate.migration_cost
        downtime = weights.downtime * (candidate.downtime + asset.downtime_cost)
        compliance_delta = (
            -weights.compliance
            if asset.compliance_required and candidate.compliance_satisfies
            else 0.0
        )
        linear[candidate.candidate_id] += risk_delta + cost + downtime + compliance_delta
    by_asset: dict[str, list[MigrationCandidate]] = {}
    for candidate in graph.candidates:
        by_asset.setdefault(candidate.asset_id, []).append(candidate)
    for candidates in by_asset.values():
        for left_index, left in enumerate(candidates):
            for right in candidates[left_index + 1 :]:
                quadratic.append(
                    QuadraticTerm(
                        left=left.candidate_id,
                        right=right.candidate_id,
                        coefficient=weights.one_candidate,
                    )
                )
    candidate_by_id = {candidate.candidate_id: candidate for candidate in graph.candidates}
    incompatibility_pairs: set[tuple[str, str]] = set()
    for candidate in graph.candidates:
        for incompatible in candidate.incompatible_with:
            if incompatible in candidate_by_id and incompatible != candidate.candidate_id:
                pair = tuple(sorted((candidate.candidate_id, incompatible)))
                if pair in incompatibility_pairs:
                    continue
                incompatibility_pairs.add(pair)
                quadratic.append(
                    QuadraticTerm(
                        left=pair[0],
                        right=pair[1],
                        coefficient=weights.incompatibility,
                    )
                )
    for dependency in graph.dependencies:
        dependents = by_asset.get(dependency.asset_id, ())
        providers = by_asset.get(dependency.depends_on, ())
        for dependent in dependents:
            linear[dependent.candidate_id] += weights.dependency
            for provider in providers:
                quadratic.append(
                    QuadraticTerm(
                        left=dependent.candidate_id,
                        right=provider.candidate_id,
                        coefficient=-weights.dependency,
                    )
                )
    constant = sum(weights.risk * asset.risk_weight for asset in graph.assets)
    constant += sum(
        weights.compliance
        for asset in graph.assets
        if asset.compliance_required
    )
    return QuboModel(
        variables=variables,
        linear=linear,
        quadratic=quadratic,
        constant=constant,
    )


def _energy_terms(
    graph: MigrationGraph,
    selected_by_asset: Mapping[str, MigrationCandidate],
    weights: MigrationWeights,
) -> tuple[EnergyTerm, ...]:
    residual = _residual_risk(graph, selected_by_asset)
    migration_cost = sum(candidate.migration_cost for candidate in selected_by_asset.values())
    downtime = sum(candidate.downtime for candidate in selected_by_asset.values())
    incompatibility = _incompatibility_count(selected_by_asset.values())
    compliance_gap = _compliance_gap(graph, selected_by_asset)
    return (
        EnergyTerm("lambda_risk * R_residual", weights.risk, residual),
        EnergyTerm("lambda_cost * C_migration", weights.cost, migration_cost),
        EnergyTerm("lambda_downtime * D", weights.downtime, downtime),
        EnergyTerm("lambda_incompat * I", weights.incompatibility, incompatibility),
        EnergyTerm("lambda_compliance * G", weights.compliance, compliance_gap),
    )


def _qubo_energy_terms(
    qubo: QuboModel, assignment: Mapping[str, bool]
) -> tuple[EnergyTerm, ...]:
    terms = [EnergyTerm("qubo_constant", 1.0, qubo.constant)]
    for variable, coefficient in sorted(qubo.linear.items()):
        if assignment[variable]:
            terms.append(EnergyTerm(f"qubo_linear:{variable}", coefficient, 1.0))
    for term in qubo.quadratic:
        if assignment[term.left] and assignment[term.right]:
            terms.append(
                EnergyTerm(
                    f"qubo_quadratic:{term.left}:{term.right}",
                    term.coefficient,
                    1.0,
                )
            )
    return tuple(terms)


def _residual_risk(
    graph: MigrationGraph, selected_by_asset: Mapping[str, MigrationCandidate]
) -> float:
    residual = 0.0
    for asset in graph.assets:
        selected = selected_by_asset.get(asset.asset_id)
        multiplier = 1.0 - selected.risk_reduction if selected else 1.0
        exposure_multiplier = 1.25 if asset.harvest_now_decrypt_later else 1.0
        residual += asset.risk_weight * multiplier * exposure_multiplier
    return residual


def _compliance_gap(
    graph: MigrationGraph, selected_by_asset: Mapping[str, MigrationCandidate]
) -> float:
    gap = 0.0
    for asset in graph.assets:
        selected = selected_by_asset.get(asset.asset_id)
        if asset.compliance_required and not (selected and selected.compliance_satisfies):
            gap += 1.0
    return gap


def _incompatibility_count(candidates: Any) -> float:
    selected = tuple(candidates)
    selected_ids = {candidate.candidate_id for candidate in selected}
    pairs: set[tuple[str, str]] = set()
    for candidate in selected:
        for item in candidate.incompatible_with:
            if item in selected_ids and item != candidate.candidate_id:
                pairs.add(tuple(sorted((candidate.candidate_id, item))))
    return float(len(pairs))


def _candidate_multiplicity_violations(
    candidates: tuple[MigrationCandidate, ...]
) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.asset_id] = counts.get(candidate.asset_id, 0) + 1
    return tuple(sorted(asset for asset, count in counts.items() if count > 1))


def _order_candidates(
    graph: MigrationGraph, selected: tuple[MigrationCandidate, ...]
) -> tuple[MigrationCandidate, ...]:
    selected_by_asset = {candidate.asset_id: candidate for candidate in selected}
    emitted: list[MigrationCandidate] = []
    emitted_assets: set[str] = set()
    remaining = sorted(selected, key=lambda candidate: candidate.asset_id)
    while remaining:
        progressed = False
        for candidate in tuple(remaining):
            required = [
                dependency.depends_on
                for dependency in graph.dependencies
                if dependency.asset_id == candidate.asset_id
                and dependency.depends_on in selected_by_asset
            ]
            if all(asset in emitted_assets for asset in required):
                emitted.append(candidate)
                emitted_assets.add(candidate.asset_id)
                remaining.remove(candidate)
                progressed = True
        if not progressed:
            emitted.extend(remaining)
            break
    return tuple(emitted)
