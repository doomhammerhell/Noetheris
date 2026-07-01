from __future__ import annotations

from pathlib import Path

from noetheris.certificates import validate_certificate
from noetheris.migration import MigrationGraph, optimize_migration_plan


ROOT = Path(__file__).resolve().parents[1]


def test_pq_migration_plan_generation() -> None:
    graph = MigrationGraph.from_json_file(ROOT / "examples" / "pqc_migration_graph.json")
    plan = optimize_migration_plan(graph, seed=42)
    selected_assets = {candidate.asset_id for candidate in plan.ordered_steps}
    assert {"hsm_kms", "tls_certs", "api_gateway", "firmware_signing"} <= selected_assets
    assert plan.residual_risk < sum(asset.risk_weight for asset in graph.assets)
    assert validate_certificate(plan.certificate).status == "verified"
    assert abs(plan.energy - plan.qubo.evaluate(plan.certificate.selected_variables)) < 1e-9
    assert abs(plan.energy - plan.certificate.total_energy) < 1e-9
