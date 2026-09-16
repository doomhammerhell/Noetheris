from __future__ import annotations

import json
from pathlib import Path

from noetheris.certificates import (
    CertificateConstraint,
    EnergyTerm,
    certificate_fingerprint,
    make_certificate,
    stable_problem_hash,
    validate_certificate,
)
from noetheris.qubo import (
    CompiledProblem,
    QuboModel,
    external_solver_replay_artifact,
)

ROOT = Path(__file__).resolve().parents[1]


def test_correct_certificate_validation() -> None:
    certificate = make_certificate(
        problem={"kind": "unit"},
        algorithm_name="unit",
        energy_terms=(EnergyTerm("lambda_path * C_path", 1.0, 2.0),),
        selected_variables={"x": True},
        satisfied_constraints=(
            CertificateConstraint("validity", True, "accepted"),
        ),
        reproducibility_seed=1,
    )
    assert validate_certificate(certificate).status == "verified"


def test_incorrect_certificate_rejection() -> None:
    certificate = make_certificate(
        problem={"kind": "unit"},
        algorithm_name="unit",
        energy_terms=(EnergyTerm("lambda_path * C_path", 1.0, 2.0),),
        selected_variables={"x": True},
        satisfied_constraints=(
            CertificateConstraint("validity", True, "accepted"),
        ),
        reproducibility_seed=1,
    ).to_dict()
    certificate["total_energy"] = 3.0
    validation = validate_certificate(certificate)
    assert validation.status == "rejected"
    assert "total energy mismatch" in validation.reasons


def test_incorrect_energy_term_contribution_rejection() -> None:
    certificate = make_certificate(
        problem={"kind": "unit"},
        algorithm_name="unit",
        energy_terms=(EnergyTerm("lambda_path * C_path", 1.0, 2.0),),
        selected_variables={"x": True},
        satisfied_constraints=(
            CertificateConstraint("validity", True, "accepted"),
        ),
        reproducibility_seed=1,
    ).to_dict()
    certificate["energy_model"][0]["contribution"] = 3.0
    validation = validate_certificate(certificate)
    assert validation.status == "rejected"
    assert "energy term lambda_path * C_path contribution mismatch" in validation.reasons


def test_committed_certificate_artifact_validates() -> None:
    with (ROOT / "examples" / "example_energy_certificate.json").open(
        "r", encoding="utf-8"
    ) as handle:
        certificate = json.load(handle)
    assert certificate["certificate_version"] == "energy-certificate-v1"
    assert certificate["repository_version"] == "0.1.0"
    assert certificate["timestamp_strategy"] == "deterministic-no-wall-clock"
    assert certificate["witness_assignment"]["selected_variable"].startswith("path_")
    assert certificate["witness_assignment"]["path"]
    assert certificate["objective_value"] == certificate["total_energy"]
    assert "recompute_problem_hash" in certificate["proof_obligations"]
    assert validate_certificate(certificate).status == "verified"
    assert certificate_fingerprint(certificate).startswith("sha256:")


def test_certificate_fingerprint_changes_on_mutation() -> None:
    certificate = make_certificate(
        problem={"kind": "unit"},
        algorithm_name="unit",
        energy_terms=(EnergyTerm("lambda_path * C_path", 1.0, 2.0),),
        selected_variables={"x": True},
        satisfied_constraints=(
            CertificateConstraint("validity", True, "accepted"),
        ),
        reproducibility_seed=1,
    ).to_dict()
    original = certificate_fingerprint(certificate)
    certificate["selected_variables"]["x"] = False
    assert certificate_fingerprint(certificate) != original


def test_certificate_external_replay_evidence_fails_closed() -> None:
    problem = {"kind": "unit-external-replay"}
    compiled = CompiledProblem(
        problem_type="unit",
        problem_hash=stable_problem_hash(problem),
        compiled_model_hash="sha256:compiled",
        model=QuboModel(variables=["x"], linear={"x": -1.0}),
        variable_metadata={"x": "unit"},
    )
    replay = external_solver_replay_artifact(
        compiled,
        {"x": True},
        reported_energy=-1.0,
        problem_hash=compiled.problem_hash,
        compiled_model_hash=compiled.compiled_model_hash,
        solver_metadata={"solver": "local_reference"},
    )
    certificate = make_certificate(
        problem=problem,
        algorithm_name="unit",
        energy_terms=(EnergyTerm("qubo_energy", 1.0, -1.0),),
        selected_variables={"x": True},
        satisfied_constraints=(
            CertificateConstraint("external_replay", True, "accepted"),
        ),
        reproducibility_seed=1,
        compiled_model_hash=compiled.compiled_model_hash,
        energy_breakdown={"external_replay_artifact": replay},
    )
    assert validate_certificate(certificate).status == "verified"

    rejected_replay = external_solver_replay_artifact(
        compiled,
        {"x": True},
        reported_energy=0.0,
        problem_hash=compiled.problem_hash,
        compiled_model_hash=compiled.compiled_model_hash,
    )
    rejected_certificate = certificate.to_dict()
    rejected_certificate["energy_breakdown"]["external_replay_artifact"] = rejected_replay
    validation = validate_certificate(rejected_certificate)
    assert validation.status == "rejected"
    assert "external_replay_artifact evidence is not verified" in validation.reasons

    tampered_certificate = certificate.to_dict()
    tampered_certificate["energy_breakdown"]["external_replay_artifact"][
        "artifact_hash"
    ] = "sha256:tampered"
    validation = validate_certificate(tampered_certificate)
    assert validation.status == "rejected"
    assert "external_replay_artifact artifact hash mismatch" in validation.reasons
