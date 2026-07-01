# Algorithms

Noetheris v0.1.0 treats security analysis as deterministic compilation from structural models into small binary optimization, certificate, and diagnostic artifacts. The algorithms below are intentionally bounded: they are designed to make invariants explicit, produce reproducible witnesses, and reject unverifiable solver output.

## Structural IR Compilation

The Structural IR represents finite systems using typed nodes, directed edges, constraints, objectives, adversary actions, risk annotations, cryptographic assets, and migration candidates. The Python and Rust validators reject references to absent nodes, malformed constraints, and ambiguous empty systems. Canonical hashes are computed from sorted JSON representations so equivalent inputs produce stable problem identifiers.

## Invariant Annealing Search

Inputs are a finite state graph, allowed transitions, forbidden states or transitions, transition costs, optional adversarial labels, and an adversarial budget. The algorithm enumerates bounded valid paths, assigns one binary variable per path, builds an exactly-one QUBO objective, and selects the minimum-energy candidate. The certificate records the chosen path variable and energy terms.

Failure modes include invalid graphs, insufficient search depth, adversarial budget rejection, and absence of a reachable forbidden condition.

## Post-Quantum Migration Optimizer

Inputs are assets, current cryptographic algorithms, dependencies, migration candidates, risk weights, downtime costs, incompatibility constraints, and compliance requirements. The optimizer selects candidates with deterministic exhaustive QUBO solving, orders selected assets by dependencies, computes residual risk, and emits blocking dependencies.

The plan is valid only if compliance requirements are satisfied, at most one candidate is selected per asset, and selected dependency constraints are respected.

## Formal Energy Certificates

Certificates are JSON objects containing problem hash, algorithm name, energy model, selected variables, satisfied constraints, violated constraints, total energy, objective value, witness assignment, reproducibility metadata, proof obligations, and version metadata. Verification recomputes contributions and rejects inconsistent energy, violated constraints, unstable timestamp strategy, or incompatible objective values.

## Security Invariant Circuit Mapping

The circuit module represents Boolean invariant predicates as oracle-like transformations. The exact simulator evaluates all tiny input states. Qiskit export is optional and intentionally limited to an integration boundary.

## Continuous-Variable Diagnostics

The CV module builds finite Fock-basis approximations for displacement, squeezing, GKP-like states, Lindblad evolution, leakage checks, quadrature moments, covariance matrices, and entanglement diagnostics. These routines are truncation diagnostics, not a claim about physical fault tolerance or hardware-calibrated optical execution.

## Hamiltonian And QAOA Mapping

The QUBO module converts binary objectives into Ising fields, couplers, and diagonal Pauli-Z Hamiltonian terms. The QAOA module performs exact statevector simulation for tiny instances using a diagonal cost phase and transverse-field mixer. This is a mathematical verification path, not a hardware performance claim.

## Lattice Fragility Mapping

The lattice module represents tiny integer lattice instances, computes nearest vectors by exhaustive bounded enumeration, estimates noise sensitivity, and emits a small QUBO-style coefficient selection surface. It is bounded by dimension and coefficient range.
