# Roadmap

## Phase 1 — v0.1 Structural Quantum Security Kernel

Shipped Structural IR, QUBO/Ising lowering, bounded invariant search, PQC migration optimization, circuit-oracle compilation, CV/GKP diagnostics, certificates, CLI, local benchmarks, release evidence artifacts, Lean/TLA kernels, and a technical note.

Validation target: full release audit passes locally and release evidence regenerates deterministically.

## Phase 2 — v0.2 External Solver Boundary

Keep the scope deliberately small. The v0.2 line should make the external solver boundary easier to inspect, replay, and extend without introducing hardware dependence.

Planned deliverables:

- Ocean-compatible QUBO exchange examples with canonical linear and quadratic terms.
- Optional `dimod.BinaryQuadraticModel` parity checks when Ocean is installed.
- Qiskit truth-table oracle examples for small Boolean predicates without IBM Runtime credentials.
- External assignment replay examples that verify problem hashes, compiled model hashes, assignments, and energies locally.
- Documentation for solver metadata and embedding metadata as external evidence, not local inference.

Out of scope for v0.2: hardware execution, minor-embedding optimization, cloud solver benchmarking, quantum advantage claims, cryptographic compromise claims, and production security certification.

Validation target: every v0.2 example runs without credentials; optional Ocean/Qiskit packages only enrich the local export report.

## Phase 3 — v0.3 Gate-Model Oracle Research

Extend Boolean expression lowering, ancilla management, reversible cleanup checks, QASM export, and Qiskit integration.

Validation target: truth-table equivalence for all small generated predicates.

## Phase 4 — v0.4 PQC Migration Enterprise Engine

Expand enterprise asset models, downgrade risk, client compatibility, staged rollout, and dependency blocker reports.

Validation target: migration plans replay against compiled model hashes.

## Phase 5 — v0.5 Formal Certificate Kernel

Strengthen certificate schema, replay semantics, Lean kernels, and TLA+ scenario alignment.

Validation target: certificate rejection tests cover arithmetic, hash, status, and witness inconsistencies.

## Phase 6 — v0.6 CV/GKP Quantum Diagnostics Expansion

Add sparse operators, better open-system solvers, richer GKP diagnostics, and truncation mitigation metrics.

Validation target: numerical invariants remain stable under cutoff sweeps.

## Phase 7 — v0.7 Hybrid Solver Interfaces

Add controlled adapters for external solvers while preserving local validation.

Validation target: all external results replay through local certificates.

## Phase 8 — v0.8 Tensor/Sparse Acceleration

Introduce sparse linear algebra and tensor-product acceleration for larger diagnostics.

Validation target: dense/sparse equivalence on small instances.

## Phase 9 — v0.9 Research Paper And Reproducibility Pack

Freeze benchmark datasets, paper figures, release artifacts, and reproducibility scripts.

Validation target: clean environment rebuilds all published artifacts.

## Phase 10 — v1.0 Verifiable Quantum-Structural Security Platform

Stabilize APIs, schemas, extension contracts, and reproducible research workflows.

Validation target: public API compatibility policy and independent replay package.
