from __future__ import annotations

from types import SimpleNamespace

from noetheris.annealing import export_to_dimod_bqm
from noetheris.backends import (
    export_bool_expr_to_qiskit,
    export_oracle_to_qiskit,
    export_qubo_to_dwave,
    ocean_bqm_parity_report,
    qubo_exchange_payload,
    replay_external_sample,
)
from noetheris.circuits import AND, BooleanOracle, BoolExpr
from noetheris.qubo import QuadraticTerm, QuboModel


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
    assert dwave_payload["exchange"]["vartype"] == "BINARY"
    assert dwave_payload["ocean_bqm_report"]["credential_required"] is False
    assert dwave_payload["external_solver_policy"].startswith("solver samples are untrusted")
    oracle = BooleanOracle(("x",), lambda bits: bits[0], name="identity")
    qiskit_payload = export_oracle_to_qiskit(oracle)
    assert qiskit_payload["credential_required"] is False
    assert "OPENQASM-LIKE" in qiskit_payload["qasm_like"]


def test_dwave_exchange_payload_and_replay_are_local() -> None:
    model = QuboModel(variables=["x"], linear={"x": -1.0})
    payload = qubo_exchange_payload(model)
    assert payload["format"] == "noetheris.qubo.exchange.v1"
    assert payload["linear_terms"] == [{"variable": "x", "coefficient": -1.0}]
    replay = replay_external_sample(model, {"x": 1}, solver_metadata={"solver": "local"})
    assert replay["status"] == "replayed"
    assert replay["energy"] == -1.0
    assert replay["embedding_metadata"]["provided"] is False


def test_ocean_bqm_parity_report_handles_optional_dependency() -> None:
    model = QuboModel(variables=["x"], linear={"x": -1.0})
    report = ocean_bqm_parity_report(model, assignments=({"x": True},))
    assert report["credential_required"] is False
    if report["available"]:
        assert report["bqm_summary"]["class"] == "dimod.BinaryQuadraticModel"
        assert report["assignment_reports"][0]["agreement"] is True
    else:
        assert report["reason"] == "ModuleNotFoundError"
        assert report["bqm_summary"] is None
        assert report["energy_agreement"] is None


def test_ocean_bqm_parity_report_verifies_local_bqm_fields(monkeypatch) -> None:
    class LocalBqm:
        def __init__(self, linear, quadratic, offset, vartype):
            self.linear = dict(linear)
            self.quadratic = dict(quadratic)
            self.offset = float(offset)
            self.vartype = vartype
            variables = set(self.linear)
            for left, right in self.quadratic:
                variables.add(left)
                variables.add(right)
            self.variables = tuple(sorted(variables))

        def to_qubo(self):
            terms = {
                (variable, variable): coefficient
                for variable, coefficient in self.linear.items()
                if coefficient != 0.0
            }
            terms.update(self.quadratic)
            return terms, self.offset

        def energy(self, assignment):
            value = self.offset
            for variable, coefficient in self.linear.items():
                if assignment[variable]:
                    value += coefficient
            for (left, right), coefficient in self.quadratic.items():
                if assignment[left] and assignment[right]:
                    value += coefficient
            return value

    local_dimod = SimpleNamespace(
        __version__="local-test",
        BINARY="BINARY",
        BinaryQuadraticModel=LocalBqm,
    )
    monkeypatch.setitem(__import__("sys").modules, "dimod", local_dimod)
    model = QuboModel(
        variables=["a", "b", "c"],
        linear={"a": -1.0},
        quadratic=[
            QuadraticTerm("b", "a", 2.0),
            QuadraticTerm("a", "a", 3.0),
        ],
        constant=0.25,
    )
    report = ocean_bqm_parity_report(
        model,
        assignments=(
            {"a": True, "b": False, "c": False},
            {"a": True, "b": True, "c": True},
        ),
    )
    assert report["available"] is True
    assert report["credential_required"] is False
    assert report["energy_agreement"] is True
    assert report["bqm_summary"] == {
        "class": "dimod.BinaryQuadraticModel",
        "vartype": "BINARY",
        "num_variables": 3,
        "num_interactions": 1,
        "offset": 0.25,
        "to_qubo_terms": 2,
        "to_qubo_offset": 0.25,
    }
    assert report["assignment_reports"][0]["noetheris_energy"] == 2.25
    assert report["assignment_reports"][0]["ocean_energy"] == 2.25
    assert report["assignment_reports"][1]["noetheris_energy"] == 4.25
    assert report["assignment_reports"][1]["ocean_energy"] == 4.25


def test_dwave_exchange_handles_large_and_comma_named_models() -> None:
    variables = [f"x,{idx}" for idx in range(25)]
    model = QuboModel(variables=variables, linear={variables[0]: -1.0})
    payload = qubo_exchange_payload(model)
    assert payload["variables"][0] == "x,0"
    assert payload["linear_terms"][0]["variable"] == "x,0"
    exported = export_qubo_to_dwave(model)
    assert exported["exchange"]["model_hash"] == payload["model_hash"]


def test_bool_expr_qiskit_export_has_truth_table_and_policy() -> None:
    expression = AND(BoolExpr.var("a"), BoolExpr.var("b"))
    payload = export_bool_expr_to_qiskit(expression, name="and_policy")
    assert payload["credential_required"] is False
    assert payload["truth_table"] == {"00": 0, "01": 0, "10": 0, "11": 1}
    assert payload["oracle_metrics"]["cleanup_gate_count"] >= 1
    assert payload["export_policy"].startswith("truth-table synthesis")
