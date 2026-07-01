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

The benchmark runner regenerates `benchmarks/results/noetheris_v0_1_baseline.json` and `.csv`. The committed baseline omits wall-clock timing and records a `runtime_policy` field instead, because local timing is machine-dependent. Structural fields, seeds, energies, solver labels, oracle metrics, CV leakage, and model sizes are the reproducibility-critical data.
