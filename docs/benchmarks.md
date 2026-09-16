# Benchmarks

The v0.1.0 benchmark runner is:

```bash
bash scripts/run_benchmarks.sh
```

It produces JSON and CSV artifacts under `benchmarks/results/`. Records include problem hash, compiled-model hash, assignment hash, problem size, variable count, constraint count, solver, seed, deterministic runtime policy, energy, replay status, solver boundary, embedding status, oracle depth estimate, and boundary leakage where applicable. The committed baseline records `runtime_seconds` as `null` because wall-clock timing is host-dependent.

Solver-boundary release evidence lives under `docs/results/solver_boundary_evidence.json`. It records the canonical QUBO exchange hash, local replay status, replay artifact hash, metadata boundary policy, and deterministic optional-ecosystem availability policy for Ocean and Qiskit. Actual local availability of optional packages is reported by examples at runtime and is kept out of committed deterministic benchmark baselines.

For local timing, use:

```bash
python3 benchmarks/run_measured_benchmarks.py
```

Measured runs include Python, platform, machine, processor, and commit metadata. They are useful for local inspection but are not the committed reproducibility baseline.

Benchmarks are local baselines. They are not hardware comparisons and do not imply quantum speedup.
