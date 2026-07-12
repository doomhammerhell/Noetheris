#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/python"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"${PYTHON_BIN}" examples/invariant_annealing_search.py >/tmp/noetheris_invariant.json
"${PYTHON_BIN}" examples/pq_migration_optimizer.py >/tmp/noetheris_migration.json
"${PYTHON_BIN}" examples/consensus_safety_violation.py >/tmp/noetheris_consensus.json
"${PYTHON_BIN}" examples/threshold_policy_analysis.py >/tmp/noetheris_threshold.json
"${PYTHON_BIN}" examples/certificate_validation.py >/tmp/noetheris_certificate.json
"${PYTHON_BIN}" examples/qubo_ising_qaoa.py >/tmp/noetheris_qaoa.json
"${PYTHON_BIN}" examples/dwave_ocean_exchange.py >/tmp/noetheris_dwave_ocean.json
"${PYTHON_BIN}" examples/qiskit_oracle_export.py >/tmp/noetheris_qiskit_oracle.json
"${PYTHON_BIN}" examples/saga_failure_semantics.py >/tmp/noetheris_saga.json
"${PYTHON_BIN}" examples/cv_fock_truncation_diagnostics.py >/tmp/noetheris_cv_fock.json
"${PYTHON_BIN}" examples/cv_gkp_stabilizer_diagnostics.py >/tmp/noetheris_cv_gkp.json
"${PYTHON_BIN}" examples/cv_lindblad_leakage_report.py >/tmp/noetheris_cv_lindblad.json
"${PYTHON_BIN}" examples/cv_entanglement_diagnostics.py >/tmp/noetheris_cv_entanglement.json
