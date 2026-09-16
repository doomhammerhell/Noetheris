from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_solver_boundary_evidence_schema_is_host_independent() -> None:
    payload = json.loads(
        (ROOT / "docs" / "results" / "solver_boundary_evidence.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["schema"] == "noetheris.solver_boundary_evidence.v1"
    assert payload["host_independent"] is True
    assert payload["runtime_seconds"] is None
    assert payload["qubo_exchange"]["model_hash"].startswith("sha256:")
    assert payload["candidate_replay"]["status"] == "verified"
    assert payload["candidate_replay"]["artifact_hash"].startswith("sha256:")
    assert payload["candidate_replay"]["verification_authority"] == "noetheris.local_replay"
    assert payload["optional_ecosystem_availability"]["ocean"] == {
        "availability_field": "ocean_bqm_report.available",
        "committed_availability": "not_assumed",
        "credential_required": False,
        "host_independent": True,
        "runtime_probe_command": "python3 examples/dwave_ocean_exchange.py",
    }
    assert payload["optional_ecosystem_availability"]["qiskit"] == {
        "availability_field": "qiskit_status.available",
        "committed_availability": "not_assumed",
        "credential_required": False,
        "host_independent": True,
        "runtime_probe_command": "python3 examples/qiskit_oracle_export.py",
    }
    assert payload["metadata_boundaries"]["hardware_claims"] == {
        "hardware_benchmark": False,
        "quantum_advantage": False,
    }


def test_release_evidence_index_records_solver_boundary_schema() -> None:
    payload = json.loads(
        (ROOT / "docs" / "results" / "release_evidence_index.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["schema"] == "noetheris.release_evidence_index.v1"
    artifacts = {item["file"]: item for item in payload["artifacts"]}
    solver_boundary = artifacts["docs/results/solver_boundary_evidence.json"]
    assert solver_boundary["schema"] == "noetheris.solver_boundary_evidence.v1"
    assert solver_boundary["scope"] == "v0.2 deterministic solver-boundary evidence"
