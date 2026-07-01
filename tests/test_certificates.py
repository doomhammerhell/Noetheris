from __future__ import annotations

import json
from pathlib import Path

from noetheris.certificates import (
    CertificateConstraint,
    EnergyTerm,
    certificate_fingerprint,
    make_certificate,
    validate_certificate,
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
