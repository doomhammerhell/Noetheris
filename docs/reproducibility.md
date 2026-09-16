# Reproducibility

Noetheris v0.1.0 is designed around deterministic local replay.

## Deterministic Inputs

Primary inputs are JSON Structural IR files under `examples/structural_ir/`. Each IR object has canonical serialization and a SHA-256 hash. Legacy graph examples remain runnable for compatibility, but the release kernel centers on Structural IR.

## Deterministic Solvers

The exact solver enumerates binary assignments in lexical variable order and is bounded to small instances. The simulated annealing baseline is deterministic under explicit seed.

## Certificates

Certificates bind problem hash, selected variables, witness data, energy terms, constraints, proof obligations, deterministic seed, and canonical fingerprint. Validation recomputes energy terms and rejects arithmetic or status inconsistencies.

## Release Gate

```bash
bash scripts/run_audit.sh
```

The audit gate runs Rust check/test/format/clippy, Python compilation, pytest, examples, CLI commands, benchmark generation, certificate validation and replay, deterministic-output checks, optional backend availability checks, Lean build when Lake is available, and source scans for release-residue terms.

## Benchmark Artifacts

```bash
bash scripts/run_benchmarks.sh
```

The benchmark runner regenerates `benchmarks/results/noetheris_v0_1_baseline.json` and `.csv`. The committed baseline sets `runtime_seconds` to `null` and records a `runtime_policy` field because local timing is machine-dependent. Structural fields, hashes, seeds, replay status, energies, solver labels, oracle metrics, CV leakage, and model sizes are the reproducibility-critical data. Use `python3 benchmarks/run_measured_benchmarks.py` for host-specific timing with environment metadata.

## Solver-Boundary Evidence

```bash
python3 scripts/generate_release_results.py
```

The release evidence generator writes `docs/results/solver_boundary_evidence.json`. That artifact records the QUBO exchange hash, replay artifact hash, replay status, replay authority, rejection-code coverage, and solver/embedding metadata boundaries. Optional Ocean and Qiskit availability are intentionally represented as deterministic policy fields with runtime probe commands. The committed baseline does not encode whether a contributor's local machine happened to have `dimod` or Qiskit installed.
