# Architecture

Noetheris v0.1.0 is a hybrid Rust/Python research kernel.

## Rust Core

- `noetheris-core`: errors, stable hashing, certificate schema, and Structural IR types.
- `noetheris-graph`: deterministic state-transition graph validation.
- `noetheris-qubo`: QUBO model, Ising model, Hamiltonian terms, exact solver, deterministic simulated annealing, compiled-problem metadata, and energy breakdown.
- `noetheris-certificates`: certificate validation rules.

Rust owns deterministic schema surfaces and validation invariants.

## Python Runtime

- `noetheris.ir`: Structural IR loading, validation, serialization, and hashing.
- `noetheris.qubo`: compilers, solvers, reverse mapping, energy evaluation, and solution explanation.
- `noetheris.annealing`: invariant search and optional dimod BQM export.
- `noetheris.migration`: enterprise PQC migration optimizer.
- `noetheris.circuits`: Boolean AST, symbolic oracle compiler, QAOA statevector simulation, and Qiskit boundary.
- `noetheris.cv`: Fock-space operators, truncation diagnostics, displacement, squeezing, GKP diagnostics, entanglement, Gaussian bridge, and Lindblad dynamics.
- `noetheris.certificates`: certificate generation, validation, replay, and fingerprinting.
- `noetheris.backends`: optional Qiskit and D-Wave/Ocean boundaries with structured exchange payloads and local replay.
- `noetheris.cli`: release CLI.

## Trust Boundary

Solver output is untrusted until deterministic replay validates energy arithmetic, constraints, hashes, and metadata. Optional backends cannot bypass local certificate verification.

## Operational Model

Default execution is local. CI invokes the release audit script, which exercises Rust, Python, examples, CLI, benchmarks, optional backend boundaries, and formal artifacts when tooling is installed.
