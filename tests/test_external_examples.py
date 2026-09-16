from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _run_example(name: str) -> dict[str, object]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT / 'python'}{os.pathsep}{env.get('PYTHONPATH', '')}"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples" / name)],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return json.loads(completed.stdout)


def test_dwave_ocean_exchange_example_replays_locally() -> None:
    payload = _run_example("dwave_ocean_exchange.py")
    assert payload["credential_required"] is False
    assert payload["exchange"]["format"] == "noetheris.qubo.exchange.v1"
    assert payload["replay"]["status"] == "verified"
    assert payload["replay"]["energy_recomputed"] is True
    assert payload["local_solution"]["energy"] == payload["replay"]["energy"]
    ocean_report = payload["ocean_bqm_report"]
    assert ocean_report["credential_required"] is False
    if ocean_report["available"]:
        assert ocean_report["energy_agreement"] is True
        assert ocean_report["assignment_reports"][0]["ocean_energy"] == payload["local_solution"]["energy"]
    else:
        assert ocean_report["bqm_summary"] is None


def test_qiskit_oracle_export_example_has_exact_local_semantics() -> None:
    payload = _run_example("qiskit_oracle_export.py")
    assert payload["credential_required"] is False
    assert payload["oracle_metrics"]["logical_variables"] == 5
    assert payload["oracle_metrics"]["cleanup_gate_count"] >= 1
    assert payload["truth_table"]["11111"] == 1
    assert payload["truth_table"]["10011"] == 0


def test_external_solver_replay_example_has_accept_and_reject_evidence() -> None:
    payload = _run_example("external_solver_replay.py")
    assert payload["credential_required"] is False
    assert payload["verification_authority"] == "noetheris.local_replay"
    assert payload["accepted_candidate"]["status"] == "verified"
    assert payload["accepted_candidate"]["artifact_hash"].startswith("sha256:")
    rejected = {item["case"]: item for item in payload["rejected_candidates"]}
    assert "problem_hash_mismatch" in rejected["problem_hash_mismatch"]["reason_codes"]
    assert (
        "compiled_model_hash_mismatch"
        in rejected["compiled_model_hash_mismatch"]["reason_codes"]
    )
    assert "assignment_missing_variables" in rejected["missing_variables"]["reason_codes"]
    assert "assignment_unknown_variables" in rejected["unknown_variables"]["reason_codes"]
    assert "reported_energy_mismatch" in rejected["energy_mismatch"]["reason_codes"]
    assert "solver_metadata_malformed" in rejected["malformed_metadata"]["reason_codes"]
    assert "embedding_metadata_malformed" in rejected["malformed_metadata"]["reason_codes"]
