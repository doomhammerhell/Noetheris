# Benchmarks

Noetheris v0.1.0 ships a local deterministic benchmark baseline. It is a reproducibility artifact, not a hardware-performance claim.

Run:

```bash
bash scripts/run_benchmarks.sh
```

The runner writes:

- `benchmarks/results/noetheris_v0_1_baseline.json`
- `benchmarks/results/noetheris_v0_1_baseline.csv`

Records include problem hash, compiled-model hash, assignment hash, problem size, variable count, constraint count, solver, seed, deterministic runtime policy, energy, replay status, solver boundary, embedding status, residual risk where applicable, oracle depth estimate, and CV boundary leakage where applicable. Wall-clock timing is intentionally outside the committed baseline because it depends on host load and CPU characteristics.

For local timing with environment metadata:

```bash
python3 benchmarks/run_measured_benchmarks.py
```

The baseline exercises Structural IR compilation, exact solving, deterministic annealing, oracle metrics, and CV/GKP diagnostics. It does not compare against IBM Quantum or D-Wave hardware.
