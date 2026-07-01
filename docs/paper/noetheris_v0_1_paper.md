# Noetheris v0.1.0: Structural Quantum Security Kernel

## Abstract

Noetheris is a research engineering framework for compiling security-critical system structures into optimization, quantum-inspired, quantum-circuit, continuous-variable diagnostic, and formally checkable representations. The v0.1.0 release introduces a Structural IR, QUBO/Ising lowering, bounded invariant search, PQC migration optimization, symbolic oracle compilation, formal energy certificates, CV/GKP diagnostics, Lean/TLA kernels, and reproducible local benchmarks.

## Keywords

Structural security, QUBO, Ising models, quantum circuits, post-quantum migration, formal certificates, GKP diagnostics, Fock truncation.

## Introduction

Security failures often arise from relations among states, actors, dependencies, schedules, policies, and cryptographic lifecycles. Noetheris treats those relations as first-class structural objects.

## Problem Statement

Given a structural system `S = (N, E, C, I, O, A)`, compile bounded verification or planning problems into objective functions and certificates whose outputs can be replayed deterministically.

## Structural IR

Nodes represent assets, states, actors, policies, and quantum modes. Edges represent transitions, dependencies, approvals, custody relations, messages, and couplings. Constraints and invariants define admissible or forbidden structure.

## QUBO/Ising Compilation

The compiler emits:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j.
```

The Ising lowering uses `x_i = (1 - z_i)/2` and yields a diagonal Hamiltonian:

```text
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j.
```

## Invariant Annealing Search

For bounded invariant search:

```text
E(x) = lambda_validity P_validity
     + lambda_initial P_initial
     + lambda_transition P_transition
     + lambda_invariant P_invariant
     + lambda_path C_path
     + lambda_adversary C_adversary
     + lambda_budget P_budget.
```

## PQC Migration Optimization

For migration:

```text
E(x) = lambda_risk R_residual
     + lambda_hndl H_harvest_exposure
     + lambda_cost C_migration
     + lambda_downtime D_operational
     + lambda_incompat I_incompatibility
     + lambda_dependency P_dependency
     + lambda_compliance G_compliance
     + lambda_downgrade P_downgrade.
```

## Gate-Model Oracle Mapping

For Boolean predicate `phi`:

```text
O_phi |x>|y> = |x>|y xor phi(x)>.
```

Noetheris emits symbolic gates, truth tables, and cost metrics.

## Formal Energy Certificates

Certificate validation checks:

```text
Verify(C, P) := hash(P) = C.problem_hash
             ∧ recompute_energy(C) = C.total_energy
             ∧ violated_constraints(C) = empty
             ∧ deterministic_metadata(C).
```

## Continuous-Variable Quantum Diagnostics

Finite Fock truncation modifies the canonical commutator:

```text
[a_K, a_K^\dagger] = I_K - K |K-1><K-1|.
```

GKP diagnostics estimate stabilizer expectations:

```text
<S_q> = <psi|exp(i sqrt(2π) q)|psi>,
<S_p> = <psi|exp(-i sqrt(2π) p)|psi>.
```

Boundary leakage is certified as part of the diagnostic witness.

## Formal Methods

Lean kernels define simplified validity predicates and small true lemmas. TLA+ specifications describe consensus, threshold policy, migration dependency, and saga terminal consistency models.

## Experiments And Benchmarks

The benchmark suite reports local QUBO size, solver, seed, deterministic runtime policy, energy, oracle metrics, and CV boundary leakage. The committed baseline omits wall-clock timing because host-dependent timing is not a stable release artifact. It does not compare against hardware backends.

## Limitations

Exact solving is exponential. Annealing is heuristic. Circuit-oracle compilation is small-instance. CV diagnostics are finite-cutoff diagnostics. Certificate validity is relative to model correctness.

## Related Work Categories

Related categories include bounded model checking, QUBO/Ising optimization, quantum annealing, QAOA, post-quantum migration planning, formal methods, and continuous-variable quantum information.

## Reproducibility Statement

All default examples run locally without cloud credentials. The release audit executes tests, examples, benchmarks, and formal builds.

## Ethical And Security Considerations

Noetheris is defensive research infrastructure. It does not claim cryptographic compromise, quantum advantage, or production fault tolerance.

## Citation

Use the BibTeX entry from the repository README.
