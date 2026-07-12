# Noetheris v0.1.0 — Structural Quantum Security Kernel

**A verifiable quantum-structural framework for invariant search, PQC migration, annealing encodings, circuit-oracle mappings, continuous-variable quantum diagnostics, and security-critical systems.**

[![CI](https://github.com/doomhammerhell/Noetheris/actions/workflows/ci.yml/badge.svg)](https://github.com/doomhammerhell/Noetheris/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Noetheris is a research engineering framework for compiling security-critical system structures into optimization, quantum-inspired, quantum-circuit, continuous-variable diagnostic, and formally checkable representations.

The release thesis is precise: security failures often emerge from structure. State transitions, dependency graphs, adversarial schedules, threshold policies, cryptographic migration dependencies, certificate obligations, and finite quantum-system diagnostics can be represented as executable structural objects. Noetheris provides a bounded but real kernel for compiling those objects into QUBO/Ising models, oracle mappings, certificate artifacts, formal kernels, and reproducible local benchmarks.

Noetheris does not claim quantum advantage, does not assess deployed cryptography as compromised, does not claim production fault tolerance, and does not depend on IBM Quantum or D-Wave credentials. External solvers and cloud backends are optional export boundaries; local verification remains deterministic.

## Implemented Kernel

- **Structural IR:** typed entities, states, assets, directed edges, dependency graphs, constraints, invariants, adversarial actions, risk annotations, migration candidates, canonical JSON, and deterministic hashes.
- **QUBO/Ising compiler:** binary variables, linear/quadratic terms, penalty constraints, exact small solver, deterministic simulated annealing, Ising/Hamiltonian lowering, reverse witness mapping, and energy breakdowns.
- **Invariant search:** bounded transition-system counterexample search with adversarial cost and forbidden-state witnesses.
- **PQC migration optimizer:** risk-weighted migration selection over asset/dependency graphs, including HSM/KMS, TLS edge, service mesh, firmware signing, CI/CD signing, archive, database encryption, compatibility constraints, residual risk, and dependency blockers.
- **Formal certificates:** canonical problem hashes, selected variables, witness assignments, deterministic seeds, energy terms, constraints, proof obligations, fingerprinting, validation, and replay commands.
- **Circuit oracle compiler:** Boolean expression AST, symbolic reversible gates, truth-table simulation, cost metrics, QASM-like fallback, and optional Qiskit export.
- **CV/Fock/GKP diagnostics:** truncated Fock operators, commutator boundary profiles, displacement, squeezing, GKP stabilizer diagnostics, entanglement measures, Gaussian/Fock bridge, Lindblad evolution, and diagnostic certificates.
- **Formal models:** Lean kernels for Structural IR, certificate validity, graph invariants, Ising energy, QUBO penalty energy, migration dependencies, and Boolean oracles; TLA+ models for consensus, threshold policy, PQC migration, and saga failure semantics.
- **Benchmarks:** local deterministic baseline runner with JSON/CSV outputs for structural QUBOs, annealing, oracle metrics, and CV/GKP diagnostics.

## Release Evidence

| Claim | Evidence |
| --- | --- |
| Structural IR validation and hashing | `tests/test_structural_ir.py`, `examples/structural_ir/*.json`, `docs/results/compiled_qubo_solution.json` |
| QUBO/Ising energy preservation | `tests/test_qubo.py`, `examples/qubo_ising_qaoa.py`, `docs/results/qaoa_hamiltonian_report.json` |
| D-Wave/Ocean boundary | `tests/test_optional_integrations.py`, `tests/test_external_examples.py`, `examples/dwave_ocean_exchange.py`, `docs/results/compiled_qubo_solution.json`, `docs/dwave_mapping.md` |
| IBM/Qiskit oracle boundary | `tests/test_circuits.py`, `tests/test_optional_integrations.py`, `tests/test_external_examples.py`, `examples/qiskit_oracle_export.py`, `docs/results/oracle_truth_table.json` |
| Certificate replay | `tests/test_certificates.py`, `examples/example_energy_certificate.json`, `docs/results/invariant_witness.json` |
| CV/GKP diagnostics | `tests/test_cv.py`, `examples/cv_gkp_stabilizer_diagnostics.py`, `docs/results/cv_gkp_diagnostic_certificate.json` |
| Release benchmark baseline | `benchmarks/results/noetheris_v0_1_baseline.json`, `benchmarks/results/noetheris_v0_1_baseline.csv`, `docs/results/benchmark_report.json` |

## Installation

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e '.[dev]'
```

Optional adapters:

```bash
python3 -m pip install -e '.[qiskit]'
python3 -m pip install -e '.[dwave]'
```

The default path requires no paid APIs, no IBM Quantum credentials, and no D-Wave credentials.

## Tests And Audit

```bash
bash scripts/run_audit.sh
```

The audit gate runs Python compilation, pytest, Rust check/test/format/clippy, examples, CLI checks, benchmarks, Lean build when available, optional-backend availability checks, deterministic-output checks, and a source scan for development-residue terms.

Individual commands:

```bash
bash scripts/run_all_python_tests.sh
bash scripts/run_rust_tests.sh
cd formal/lean && lake build
```

## Examples

```bash
bash scripts/run_examples.sh

python3 examples/invariant_annealing_search.py
python3 examples/pq_migration_optimizer.py
python3 examples/consensus_safety_violation.py
python3 examples/threshold_policy_analysis.py
python3 examples/certificate_validation.py
python3 examples/qubo_ising_qaoa.py
python3 examples/dwave_ocean_exchange.py
python3 examples/qiskit_oracle_export.py
python3 examples/saga_failure_semantics.py
python3 examples/cv_fock_truncation_diagnostics.py
python3 examples/cv_gkp_stabilizer_diagnostics.py
python3 examples/cv_lindblad_leakage_report.py
python3 examples/cv_entanglement_diagnostics.py
```

Structural IR inputs live under `examples/structural_ir/`.

The Ocean and Qiskit examples run without D-Wave or IBM Quantum credentials. If optional packages are installed, they add local object summaries and energy parity checks; they do not perform cloud execution.

## CLI

```bash
python3 -m noetheris validate-ir examples/structural_ir/consensus_safety_ir.json
python3 -m noetheris compile-qubo examples/structural_ir/consensus_safety_ir.json --problem invariant --output /tmp/noetheris_compiled.json
python3 -m noetheris solve /tmp/noetheris_compiled.json --solver exact --output /tmp/noetheris_solution.json
python3 -m noetheris run-scenario consensus
python3 -m noetheris run-scenario saga
python3 -m noetheris run-scenario migration
python3 -m noetheris run-scenario threshold
python3 -m noetheris cv-diagnostics examples/structural_ir/cv_gkp_diagnostic_ir.json
python3 -m noetheris benchmark --small
```

Certificate commands:

```bash
python3 -m noetheris.certificates.validate examples/example_energy_certificate.json
python3 -m noetheris.certificates.replay examples/example_energy_certificate.json
```

## QUBO, Ising, And Hamiltonian Lowering

Noetheris lowers binary objectives

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j
```

into the Pauli-Z Ising convention `x_i = (1 - z_i) / 2`, producing

```text
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j.
```

Tests check energy equivalence over all assignments for small instances. The exact solver is intentionally bounded; deterministic simulated annealing provides a local heuristic baseline for larger research examples.

## Circuit Oracle Mapping

Boolean predicates over structural variables are compiled into symbolic reversible oracles:

```text
O_phi |x>|y> = |x>|y xor phi(x)>.
```

The local compiler emits symbolic gates, truth tables, cost metrics, reversibility checks, and QASM-like text. Qiskit export is optional and never requires IBM Quantum credentials.

## Certificates

Optimization and diagnostics emit deterministic certificate objects containing problem hashes, compiled model hashes where available, selected variables, witnesses, energy terms, satisfied and violated constraints, proof obligations, reproducibility metadata, and canonical fingerprints. Certificates fail closed: arithmetic mismatches, status inconsistencies, violated constraints, and nondeterministic timestamp strategies are rejected.

## Benchmarks

```bash
bash scripts/run_benchmarks.sh
```

This writes:

- `benchmarks/results/noetheris_v0_1_baseline.json`
- `benchmarks/results/noetheris_v0_1_baseline.csv`

Benchmarks are local baselines with problem hashes, compiled-model hashes, assignment hashes, replay status, solver boundary, and embedding status. The committed baseline records `runtime_seconds: null`; use `python3 benchmarks/run_measured_benchmarks.py` for host-specific timing with environment metadata. Benchmarks do not compare against IBM or D-Wave hardware unless such runs are explicitly performed and documented.

## Formal Methods

Lean files under `formal/lean/Noetheris/` define small kernels for certificate validity, graph invariants, structural nodes/edges, penalty energy, migration dependency validity, circuit oracle truth, and diagonal Ising energy. TLA+ files under `formal/tla/` specify small consensus, threshold-policy, migration, and saga models.

These formal artifacts cover simplified kernels. They do not prove the entire implementation.

## Citation

```bibtex
@software{noetheris_v0_1,
  title = {Noetheris v0.1.0: Structural Quantum Security Kernel},
  author = {Giovani, Mayckon},
  year = {2026},
  license = {Apache-2.0}
}
```

## Responsible Extension

New encodings must define the structural model, adversary assumptions, binary variables, objective terms, constraints, certificate obligations, solver boundaries, and replay strategy. Contributions must avoid unsupported cryptographic claims, unsupported hardware-performance claims, and unverifiable solver output.
