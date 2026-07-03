# Release Results

This directory contains deterministic evidence artifacts for Noetheris v0.1.0.
They are generated from checked-in examples and can be rebuilt with:

```bash
python3 scripts/generate_release_results.py
```

## Artifacts

- `release_evidence_index.json`: index of generated evidence files.
- `invariant_witness.json`: bounded consensus-safety counterexample witness with certificate data.
- `compiled_qubo_solution.json`: Structural IR compilation, exact QUBO solution, energy breakdown, D-Wave exchange payload, and local replay of a solver sample.
- `pqc_migration_plan.json`: migration optimizer output, residual risk, dependency analysis, QUBO model, and certificate.
- `oracle_truth_table.json`: Boolean predicate truth table, reversible compute/apply/uncompute metrics, and QASM-like text.
- `qaoa_hamiltonian_report.json`: QUBO-to-Ising lowering and exact local QAOA p=1 statevector check.
- `cv_gkp_diagnostic_certificate.json`: finite Fock/GKP diagnostic certificate and truncation metrics.
- `benchmark_report.json`: deterministic benchmark baseline with hashes, model sizes, energies, solver labels, replay status, solver boundary, and embedding status.

## Interpretation

These files are release evidence, not hardware benchmark claims. The D-Wave payload is a BINARY QUBO exchange representation; any external solver sample must be replayed locally before it is trusted. The Qiskit-facing oracle artifacts are small-predicate circuit mappings; they do not claim backend advantage. The CV/GKP certificate uses finite Fock truncation and records boundary effects explicitly.
