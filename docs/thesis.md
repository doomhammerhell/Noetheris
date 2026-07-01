# Noetheris Thesis

## Abstract

Noetheris v0.1.0 studies security-critical systems as structural objects that can be compiled into optimization models, quantum-circuit oracles, continuous-variable diagnostics, and formally checkable certificates. The release provides an executable kernel rather than a claim of quantum advantage.

## Motivation

Many failures in distributed systems and cryptographic migration programs are structural: invalid state reachability, adversarial schedules, broken dependency order, threshold-policy gaps, long-lived cryptographic exposure, or finite-simulation boundary artifacts. A useful research system must make those structures explicit, executable, and replayable.

## Core Thesis

Security-critical structures can be represented as:

```text
S = (N, E, C, I, O, A, M)
```

where nodes, edges, constraints, invariants, objectives, adversary actions, and metadata define a bounded model. Noetheris compiles supported instances into QUBO/Ising objectives, symbolic oracles, CV diagnostics, and certificates whose arithmetic can be replayed locally.

## Invariant Objective

For bounded transition systems:

```text
E(x) =
  lambda_validity   P_validity(x)
+ lambda_initial    P_initial(x)
+ lambda_transition P_transition(x)
+ lambda_invariant  P_invariant(x)
+ lambda_path       C_path(x)
+ lambda_adversary  C_adversary(x)
+ lambda_budget     P_budget(x).
```

The v0.1 compiler uses bounded path variables for small systems so witnesses remain explicit.

## Migration Objective

For PQC migration:

```text
E(x) =
  lambda_risk       R_residual(x)
+ lambda_hndl       H_harvest_exposure(x)
+ lambda_cost       C_migration(x)
+ lambda_downtime   D_operational(x)
+ lambda_incompat   I_incompatibility(x)
+ lambda_dependency P_dependency(x)
+ lambda_compliance G_compliance(x)
+ lambda_downgrade  P_downgrade(x).
```

The release includes enterprise-style assets for TLS, API gateways, service mesh, firmware signing, CI/CD signing, KMS/HSM custody, archives, databases, and client compatibility.

## QUBO And Ising Lowering

Noetheris emits:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j.
```

Using `x_i = (1 - z_i)/2`, the equivalent diagonal Hamiltonian is:

```text
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j.
```

Energy equivalence is tested for small instances.

## Circuit Oracles

Boolean structural predicates are mapped as:

```text
O_phi |x>|y> = |x>|y xor phi(x)>.
```

The compiler emits symbolic gates, truth tables, QASM-like text, and cost metrics. Qiskit export is optional.

## Formal Certificates

Certificate verification is a deterministic relation:

```text
Verify(C, P) :=
  hash(P) = C.problem_hash
  and recompute_energy(C) = C.total_energy
  and no violated constraints remain
  and deterministic metadata is declared.
```

The certificate validates an encoded model and witness. It does not validate unmodeled assumptions.

## CV/Fock/GKP Diagnostics

Finite Fock spaces introduce boundary artifacts:

```text
[a_K, a_K^\dagger] = I_K - K |K-1><K-1|.
```

Noetheris measures commutator boundary profiles, boundary population, Weyl residuals, GKP stabilizer expectations, entanglement diagnostics, and Lindblad leakage. These diagnostics are finite-cutoff research tools, not production fault-tolerance claims.

## Formal Methods

Lean kernels define small true lemmas for certificates, graph invariants, Structural IR, QUBO penalty energy, migration dependencies, circuit oracles, and Ising energy. TLA+ models cover consensus, threshold policy, PQC migration, and saga terminal consistency.

## Limitations

The kernel is bounded: exact solving is exponential, annealing is heuristic, oracle compilation is small-instance, CV simulation is finite-cutoff, and certificates are relative to model correctness. These are explicit scientific boundaries.
