# Benchmarks

The v0.1.0 benchmark runner is:

```bash
bash scripts/run_benchmarks.sh
```

It produces JSON and CSV artifacts under `benchmarks/results/`. Records include problem name, problem size, variable count, constraint count, solver, seed, deterministic runtime policy, energy, certificate validity, oracle depth estimate, and boundary leakage where applicable. The committed baseline deliberately omits wall-clock timing because that value is host-dependent.

Benchmarks are local baselines. They are not hardware comparisons and do not imply quantum speedup.
