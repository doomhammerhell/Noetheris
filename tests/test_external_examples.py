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
    ocean_check = payload["ocean_energy_check"]
    if ocean_check["available"]:
        assert ocean_check["energy"] == payload["local_solution"]["energy"]


def test_qiskit_oracle_export_example_has_exact_local_semantics() -> None:
    payload = _run_example("qiskit_oracle_export.py")
    assert payload["credential_required"] is False
    assert payload["oracle_metrics"]["logical_variables"] == 5
    assert payload["oracle_metrics"]["cleanup_gate_count"] >= 1
    assert payload["truth_table"]["11111"] == 1
    assert payload["truth_table"]["10011"] == 0
