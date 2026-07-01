from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_problem_hash(value: Any) -> str:
    encoded = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class EnergyTerm:
    name: str
    weight: float
    value: float
    declared_contribution: float | None = None

    @property
    def contribution(self) -> float:
        if self.declared_contribution is not None:
            return self.declared_contribution
        return self.computed_contribution

    @property
    def computed_contribution(self) -> float:
        return self.weight * self.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "weight": self.weight,
            "value": self.value,
            "contribution": self.contribution,
        }


@dataclass(frozen=True)
class CertificateConstraint:
    name: str
    satisfied: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "satisfied": self.satisfied, "detail": self.detail}


@dataclass(frozen=True)
class ValidationResult:
    status: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class EnergyCertificate:
    problem_hash: str
    algorithm_name: str
    energy_model: tuple[EnergyTerm, ...]
    selected_variables: Mapping[str, bool]
    satisfied_constraints: tuple[CertificateConstraint, ...]
    violated_constraints: tuple[CertificateConstraint, ...]
    total_energy: float
    verification_status: str
    reproducibility_seed: int
    certificate_version: str = "energy-certificate-v1"
    repository_version: str = "0.1.0"
    problem_type: str = "structural_optimization"
    witness_assignment: Mapping[str, Any] = field(default_factory=dict)
    objective_value: float | None = None
    energy_breakdown: Mapping[str, Any] = field(default_factory=dict)
    input_file_hash: str | None = None
    compiled_model_hash: str | None = None
    residual_risk: float | None = None
    proof_obligations: tuple[str, ...] = ()
    timestamp_strategy: str = "deterministic-no-wall-clock"
    reproducibility_metadata: Mapping[str, str] = field(default_factory=dict)
    version: Mapping[str, str] = field(
        default_factory=lambda: {
            "project": "noetheris",
            "version": "0.1.0",
            "schema": "energy-certificate-v1",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certificate_version": self.certificate_version,
            "repository_version": self.repository_version,
            "problem_type": self.problem_type,
            "problem_hash": self.problem_hash,
            "algorithm_name": self.algorithm_name,
            "energy_model": [term.to_dict() for term in self.energy_model],
            "selected_variables": dict(sorted(self.selected_variables.items())),
            "witness_assignment": dict(self.witness_assignment),
            "satisfied_constraints": [
                constraint.to_dict() for constraint in self.satisfied_constraints
            ],
            "violated_constraints": [
                constraint.to_dict() for constraint in self.violated_constraints
            ],
            "total_energy": self.total_energy,
            "objective_value": self.objective_value,
            "energy_breakdown": dict(self.energy_breakdown),
            "input_file_hash": self.input_file_hash,
            "compiled_model_hash": self.compiled_model_hash,
            "residual_risk": self.residual_risk,
            "proof_obligations": list(self.proof_obligations),
            "verification_status": self.verification_status,
            "reproducibility_seed": self.reproducibility_seed,
            "timestamp_strategy": self.timestamp_strategy,
            "reproducibility_metadata": dict(self.reproducibility_metadata),
            "version": dict(self.version),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EnergyCertificate":
        return cls(
            certificate_version=str(value.get("certificate_version", "energy-certificate-v1")),
            repository_version=str(value.get("repository_version", "0.1.0")),
            problem_type=str(value.get("problem_type", "structural_optimization")),
            problem_hash=str(value["problem_hash"]),
            algorithm_name=str(value["algorithm_name"]),
            energy_model=tuple(
                EnergyTerm(
                    name=str(term["name"]),
                    weight=float(term["weight"]),
                    value=float(term["value"]),
                    declared_contribution=(
                        float(term["contribution"])
                        if "contribution" in term
                        else None
                    ),
                )
                for term in value["energy_model"]
            ),
            selected_variables={
                str(name): bool(enabled)
                for name, enabled in value["selected_variables"].items()
            },
            witness_assignment=dict(value.get("witness_assignment", {})),
            satisfied_constraints=tuple(
                CertificateConstraint(
                    name=str(item["name"]),
                    satisfied=bool(item["satisfied"]),
                    detail=str(item["detail"]),
                )
                for item in value.get("satisfied_constraints", ())
            ),
            violated_constraints=tuple(
                CertificateConstraint(
                    name=str(item["name"]),
                    satisfied=bool(item["satisfied"]),
                    detail=str(item["detail"]),
                )
                for item in value.get("violated_constraints", ())
            ),
            total_energy=float(value["total_energy"]),
            objective_value=(
                float(value["objective_value"])
                if value.get("objective_value") is not None
                else None
            ),
            energy_breakdown=dict(value.get("energy_breakdown", {})),
            input_file_hash=(
                str(value["input_file_hash"]) if value.get("input_file_hash") else None
            ),
            compiled_model_hash=(
                str(value["compiled_model_hash"])
                if value.get("compiled_model_hash")
                else None
            ),
            residual_risk=(
                float(value["residual_risk"]) if value.get("residual_risk") is not None else None
            ),
            proof_obligations=tuple(
                str(item) for item in value.get("proof_obligations", ())
            ),
            verification_status=str(value["verification_status"]),
            reproducibility_seed=int(value["reproducibility_seed"]),
            timestamp_strategy=str(
                value.get("timestamp_strategy", "deterministic-no-wall-clock")
            ),
            reproducibility_metadata={
                str(k): str(v) for k, v in value.get("reproducibility_metadata", {}).items()
            },
            version={str(k): str(v) for k, v in value["version"].items()},
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2)

    def fingerprint(self) -> str:
        return certificate_fingerprint(self)


def make_certificate(
    *,
    problem: Any,
    algorithm_name: str,
    energy_terms: tuple[EnergyTerm, ...],
    selected_variables: Mapping[str, bool],
    satisfied_constraints: tuple[CertificateConstraint, ...],
    violated_constraints: tuple[CertificateConstraint, ...] = (),
    reproducibility_seed: int,
    problem_type: str = "structural_optimization",
    input_file_hash: str | None = None,
    compiled_model_hash: str | None = None,
    witness_assignment: Mapping[str, Any] | None = None,
    objective_value: float | None = None,
    energy_breakdown: Mapping[str, Any] | None = None,
    residual_risk: float | None = None,
    proof_obligations: tuple[str, ...] = (),
) -> EnergyCertificate:
    total_energy = sum(term.computed_contribution for term in energy_terms)
    status = "verified" if not violated_constraints else "rejected"
    return EnergyCertificate(
        problem_hash=stable_problem_hash(problem),
        problem_type=problem_type,
        algorithm_name=algorithm_name,
        energy_model=energy_terms,
        selected_variables=selected_variables,
        witness_assignment=witness_assignment or {},
        satisfied_constraints=satisfied_constraints,
        violated_constraints=violated_constraints,
        total_energy=total_energy,
        objective_value=objective_value if objective_value is not None else total_energy,
        energy_breakdown=energy_breakdown or {},
        input_file_hash=input_file_hash,
        compiled_model_hash=compiled_model_hash,
        residual_risk=residual_risk,
        proof_obligations=proof_obligations,
        verification_status=status,
        reproducibility_seed=reproducibility_seed,
        reproducibility_metadata={"seed": str(reproducibility_seed)},
    )


def validate_certificate(
    certificate: EnergyCertificate | Mapping[str, Any],
    *,
    expected_problem_hash: str | None = None,
    tolerance: float = 1e-9,
) -> ValidationResult:
    cert = (
        EnergyCertificate.from_dict(certificate)
        if not isinstance(certificate, EnergyCertificate)
        else certificate
    )
    reasons: list[str] = []
    if expected_problem_hash is not None and cert.problem_hash != expected_problem_hash:
        reasons.append("problem hash mismatch")
    recomputed = sum(term.computed_contribution for term in cert.energy_model)
    if abs(recomputed - cert.total_energy) > tolerance:
        reasons.append("total energy mismatch")
    for term in cert.energy_model:
        if abs(term.computed_contribution - term.contribution) > tolerance:
            reasons.append(f"energy term {term.name} contribution mismatch")
    for constraint in cert.satisfied_constraints:
        if not constraint.satisfied:
            reasons.append(f"satisfied constraint {constraint.name} is marked false")
    for constraint in cert.violated_constraints:
        if constraint.satisfied:
            reasons.append(f"violated constraint {constraint.name} is marked true")
        reasons.append(f"constraint {constraint.name} is violated")
    derived_status = "verified" if not reasons else "rejected"
    if cert.verification_status != derived_status:
        reasons.append("declared verification status is inconsistent")
        derived_status = "rejected"
    if cert.timestamp_strategy != "deterministic-no-wall-clock":
        reasons.append("timestamp strategy is not deterministic")
        derived_status = "rejected"
    if cert.objective_value is not None and abs(cert.objective_value - cert.total_energy) > tolerance:
        reasons.append("objective value mismatch")
        derived_status = "rejected"
    return ValidationResult(status=derived_status, reasons=tuple(reasons))


def certificate_fingerprint(certificate: EnergyCertificate | Mapping[str, Any]) -> str:
    cert = (
        EnergyCertificate.from_dict(certificate)
        if not isinstance(certificate, EnergyCertificate)
        else certificate
    )
    return stable_problem_hash(cert.to_dict())
