# Benchmarks

The v0.1.0 benchmark runner is:

```bash
bash scripts/run_benchmarks.sh
```

It produces JSON and CSV artifacts under `benchmarks/results/`. Records include problem hash, compiled-model hash, assignment hash, problem size, variable count, constraint count, solver, seed, deterministic runtime policy, energy, replay status, solver boundary, embedding status, oracle depth estimate, and boundary leakage where applicable. The committed baseline records `runtime_seconds` as `null` because wall-clock timing is host-dependent.

For local timing, use:

```bash
python3 benchmarks/run_measured_benchmarks.py
```

Measured runs include Python, platform, machine, processor, and commit metadata. They are useful for local inspection but are not the committed reproducibility baseline.

Benchmarks are local baselines. They are not hardware comparisons and do not imply quantum speedup.
