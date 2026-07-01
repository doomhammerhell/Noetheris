from __future__ import annotations

from pathlib import Path

from noetheris.annealing import search_invariant_violation
from noetheris.certificates import validate_certificate
from noetheris.graph import StateGraph


ROOT = Path(__file__).resolve().parents[1]


def test_invariant_violation_search() -> None:
    graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    result = search_invariant_violation(
        graph,
        max_depth=3,
        adversarial_budget=2,
        seed=42,
    )
    assert result.violation_found is True
    assert result.path[-1] == "conflicting_commit"
    assert validate_certificate(result.certificate).status == "verified"

