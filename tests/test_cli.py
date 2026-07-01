from __future__ import annotations

import json
from pathlib import Path

from noetheris.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_validate_compile_and_solve(tmp_path: Path) -> None:
    ir_path = ROOT / "examples" / "structural_ir" / "consensus_safety_ir.json"
    assert main(["validate-ir", str(ir_path)]) == 0
    compiled = tmp_path / "compiled.json"
    assert main(["compile-qubo", str(ir_path), "--problem", "invariant", "--output", str(compiled)]) == 0
    assert compiled.exists()
    solution = tmp_path / "solution.json"
    assert main(["solve", str(compiled), "--solver", "exact", "--output", str(solution)]) == 0
    payload = json.loads(solution.read_text(encoding="utf-8"))
    assert payload["energy"] <= 200.0


def test_cli_cv_diagnostics() -> None:
    scenario = ROOT / "examples" / "structural_ir" / "cv_gkp_diagnostic_ir.json"
    assert main(["cv-diagnostics", str(scenario)]) == 0
