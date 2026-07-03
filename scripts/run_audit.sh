#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/python"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cargo fmt --check --all
cargo check --workspace
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings
"${PYTHON_BIN}" -m compileall python examples benchmarks
"${PYTHON_BIN}" -m pytest
bash scripts/run_examples.sh
"${PYTHON_BIN}" scripts/generate_release_results.py
bash scripts/run_benchmarks.sh >/tmp/noetheris_benchmarks.json
if command -v lake >/dev/null 2>&1; then
  (cd formal/lean && lake build)
fi
tmp_dir="$(mktemp -d)"
"${PYTHON_BIN}" -m noetheris validate-ir examples/structural_ir/consensus_safety_ir.json >/tmp/noetheris_cli_validate.json
"${PYTHON_BIN}" -m noetheris compile-qubo examples/structural_ir/consensus_safety_ir.json --problem invariant --output "${tmp_dir}/compiled.json"
"${PYTHON_BIN}" -m noetheris solve "${tmp_dir}/compiled.json" --solver exact --output "${tmp_dir}/solution.json"
"${PYTHON_BIN}" -m noetheris run-scenario consensus >/tmp/noetheris_cli_scenario.json
"${PYTHON_BIN}" -m noetheris cv-diagnostics examples/structural_ir/cv_gkp_diagnostic_ir.json >/tmp/noetheris_cli_cv.json
"${PYTHON_BIN}" -m noetheris.certificates.validate examples/example_energy_certificate.json >/tmp/noetheris_cli_cert_validate.json
"${PYTHON_BIN}" -m noetheris.certificates.replay examples/example_energy_certificate.json >/tmp/noetheris_cli_cert_replay.json
"${PYTHON_BIN}" - <<'PY'
from noetheris.backends import export_oracle_to_qiskit, export_qubo_to_dwave
from noetheris.circuits import BooleanOracle
from noetheris.qubo import QuboModel
assert export_qubo_to_dwave(QuboModel(variables=["x"], linear={"x": -1.0}))["credential_required"] is False
assert export_oracle_to_qiskit(BooleanOracle(("x",), lambda bits: bits[0]))["credential_required"] is False
PY
for script in invariant_annealing_search.py pq_migration_optimizer.py consensus_safety_violation.py threshold_policy_analysis.py certificate_validation.py; do
  "${PYTHON_BIN}" "examples/${script}" > "${tmp_dir}/${script}.a"
  "${PYTHON_BIN}" "examples/${script}" > "${tmp_dir}/${script}.b"
  cmp "${tmp_dir}/${script}.a" "${tmp_dir}/${script}.b"
done
hex_terms=(
  "544f444f"
  "4649584d45"
  "706c616365686f6c646572"
  "6d6f636b"
  "64756d6d79"
  "636f6d696e6720736f6f6e"
  "6e6f7420696d706c656d656e746564"
  "66616b65"
  "73747562"
)
pattern="$(for encoded in "${hex_terms[@]}"; do printf '%s\n' "${encoded}" | xxd -r -p; done | paste -sd '|' -)"
if rg -n -i "${pattern}" \
  README.md RELEASE_NOTES_v0.1.0.md SECURITY.md CONTRIBUTING.md CODE_OF_CONDUCT.md ROADMAP.md CHANGELOG.md \
  docs python crates examples tests formal scripts benchmarks .github; then
  echo "audit phrase scan failed" >&2
  exit 1
fi
