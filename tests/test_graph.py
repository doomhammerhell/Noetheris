from __future__ import annotations

from pathlib import Path

import pytest

from noetheris.graph import StateGraph, Transition


ROOT = Path(__file__).resolve().parents[1]


def test_graph_loading() -> None:
    graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    graph.validate()
    assert graph.initial_state == "round0_locked_a"
    assert "conflicting_commit" in graph.forbidden_states


def test_invalid_graph_detection() -> None:
    graph = StateGraph(
        states=("a",),
        transitions=(Transition(source="a", target="z", cost=1.0),),
    )
    with pytest.raises(ValueError, match="unknown state"):
        graph.validate()

