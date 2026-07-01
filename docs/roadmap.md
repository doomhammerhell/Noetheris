# Roadmap

## Phase 1 — v0.1 Structural Quantum Security Kernel

Deliver Structural IR, QUBO/Ising lowering, bounded invariant search, PQC migration optimization, circuit-oracle compilation, CV/GKP diagnostics, certificates, CLI, local benchmarks, Lean/TLA kernels, and paper draft.

Validation target: full release audit passes locally.

## Phase 2 — v0.2 Annealing And Embedding Layer

Add richer penalty calibration, decomposition, Ocean-native model export, embedding metadata capture, and certificate replay for external annealing results.

Validation target: differential tests across exact, seeded annealing, and exported models.

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
