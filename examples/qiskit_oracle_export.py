from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.backends import export_bool_expr_to_qiskit
from noetheris.circuits import AND, OR, BoolExpr


def main() -> None:
    signer_a = BoolExpr.var("hsm_a")
    signer_b = BoolExpr.var("hsm_b")
    recovery = BoolExpr.var("recovery_key")
    whitelist = BoolExpr.var("whitelist")
    time_window = BoolExpr.var("time_window")
    two_of_three = OR(
        AND(signer_a, signer_b),
        AND(signer_a, recovery),
        AND(signer_b, recovery),
    )
    authorization = AND(two_of_three, whitelist, time_window)
    exported = export_bool_expr_to_qiskit(
        authorization,
        name="threshold_custody_authorization",
    )
    print(
        json.dumps(
            {
                "example": "qiskit_oracle_export",
                "policy": "2-of-3 custody authorization with whitelist and time window",
                "qiskit_status": exported["status"],
                "oracle_metrics": exported["oracle_metrics"],
                "truth_table": exported["truth_table"],
                "qiskit_circuit_summary": exported["qiskit_circuit_summary"],
                "qasm_like": exported["qasm_like"].splitlines(),
                "credential_required": exported["credential_required"],
                "export_policy": exported["export_policy"],
                "trust_boundary": (
                    "The local truth table is the reference behavior; any Qiskit "
                    "circuit summary is an optional local representation."
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
