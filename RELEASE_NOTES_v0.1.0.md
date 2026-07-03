## Noetheris v0.1.0 — Structural Quantum Security Kernel

Initial public research release of Noetheris: a local-first structural security kernel for compiling security-critical system models into QUBO/Ising objectives, symbolic oracle mappings, deterministic certificates, CV/Fock/GKP diagnostics, release evidence artifacts, benchmarks, and small formal models.

### Included

- Structural IR for states, assets, dependencies, constraints, adversary annotations, risk metadata, and migration models.
- QUBO/Ising compiler with exact small-instance solving, deterministic annealing, energy breakdowns, reverse witness mapping, and canonical exchange payloads.
- D-Wave/Ocean boundary with structured BINARY QUBO export, optional `dimod.BinaryQuadraticModel` construction, and local replay of external solver samples.
- IBM/Qiskit boundary with Boolean expression AST, exact truth tables, symbolic compute/apply/uncompute oracle metrics, QASM-like text, and optional small-predicate Qiskit circuit synthesis.
- Invariant search, PQC migration optimization, threshold-policy analysis, saga failure semantics, and certificate validation examples.
- Certificate validation and replay with deterministic hashes, energy checks, constraints, witnesses, proof obligations, and reproducibility metadata.
- CV/Fock/GKP diagnostics using finite Fock operators, truncation metrics, `2 sqrt(pi)` square-lattice GKP stabilizer spacing, Lindblad leakage checks, and diagnostic certificates.
- Deterministic release evidence under `docs/results/`.
- Local deterministic benchmark artifacts in JSON and CSV.
- Lean and TLA+ artifacts for small formal kernels and scenario models.

### Positioning

Noetheris v0.1.0 is a bounded research kernel. It does not claim quantum advantage, cryptographic compromise, production fault tolerance, IBM Quantum backend performance, or D-Wave hardware performance. IBM Quantum and D-Wave credentials are not required for default execution. External solver output is treated as an untrusted witness until Noetheris replays hashes, assignment variables, and energy locally.

### Validation

The release audit runs Rust check/test/fmt/clippy, Python compilation and pytest, examples, CLI checks, deterministic evidence generation, benchmark generation, certificate validation/replay, optional backend availability checks, source-residue scans, and Lean build when available.

```bash
bash scripts/run_audit.sh
```
