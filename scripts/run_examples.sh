#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="${PYTHONPATH}:$(pwd)/python"
else
  export PYTHONPATH="$(pwd)/python"
fi
source "$(dirname "${BASH_SOURCE[0]}")/python_env.sh"
"${NOETHERIS_PYTHON_CMD[@]}" examples/invariant_annealing_search.py >/tmp/noetheris_invariant.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/pq_migration_optimizer.py >/tmp/noetheris_migration.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/consensus_safety_violation.py >/tmp/noetheris_consensus.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/threshold_policy_analysis.py >/tmp/noetheris_threshold.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/certificate_validation.py >/tmp/noetheris_certificate.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/qubo_ising_qaoa.py >/tmp/noetheris_qaoa.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/dwave_ocean_exchange.py >/tmp/noetheris_dwave_ocean.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/external_solver_replay.py >/tmp/noetheris_external_replay.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/qiskit_oracle_export.py >/tmp/noetheris_qiskit_oracle.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/saga_failure_semantics.py >/tmp/noetheris_saga.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/cv_fock_truncation_diagnostics.py >/tmp/noetheris_cv_fock.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/cv_gkp_stabilizer_diagnostics.py >/tmp/noetheris_cv_gkp.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/cv_lindblad_leakage_report.py >/tmp/noetheris_cv_lindblad.json
"${NOETHERIS_PYTHON_CMD[@]}" examples/cv_entanglement_diagnostics.py >/tmp/noetheris_cv_entanglement.json
