from __future__ import annotations

from noetheris.annealing import export_to_dimod_bqm
from noetheris.backends import export_oracle_to_qiskit, export_qubo_to_dwave
from noetheris.circuits import BooleanOracle
from noetheris.qubo import QuboModel


def test_dwave_ocean_export_gracefully_reports_availability() -> None:
    model = QuboModel(variables=["x"], linear={"x": -1.0})
    bqm, status = export_to_dimod_bqm(model)
    assert (bqm is None and status.startswith("dwave ocean unavailable")) or (
        bqm is not None and status == "dimod binary quadratic model exported"
    )


def test_qiskit_export_gracefully_reports_availability() -> None:
    oracle = BooleanOracle(("x",), lambda bits: bits[0], name="identity")
    circuit, status = oracle.qiskit_export()
    assert (circuit is None and status.startswith("qiskit unavailable")) or (
        circuit is not None and status.startswith("qiskit")
    )


def test_backend_wrappers_never_require_credentials() -> None:
    model = QuboModel(variables=["x"], linear={"x": -1.0})
    dwave_payload = export_qubo_to_dwave(model)
    assert dwave_payload["credential_required"] is False
    oracle = BooleanOracle(("x",), lambda bits: bits[0], name="identity")
    qiskit_payload = export_oracle_to_qiskit(oracle)
    assert qiskit_payload["credential_required"] is False
    assert "OPENQASM-LIKE" in qiskit_payload["qasm_like"]
