# IBM Quantum Mapping

## Gate-Model Mapping

Security predicates can be represented as Boolean functions over state bits. For a predicate `phi(x)`, the oracle-like mapping is:

```text
O_phi |x> |y> = |x> |y xor phi(x)>
```

This is the bridge from invariant checking to gate-model reasoning.

## Oracle Construction

Noetheris builds a symbolic circuit description with input bits, a target bit, predicate computation, xor application, and predicate uncomputation. The base implementation simulates the mapping exactly for tiny examples.

## Dynamic Circuit Relevance

Dynamic circuits are relevant when verification, branching, or mid-circuit measurement changes control flow. Noetheris v0.1.0 limits executable gate-model artifacts to deterministic symbolic oracles, exact truth-table checks, and local QASM-like export. Dynamic-circuit execution is outside this release boundary.

## Simulator-First Approach

The repository runs locally without IBM Quantum credentials. Optional Qiskit export is skipped when Qiskit is unavailable and does not affect certificate validation.

## QAOA Relevance

QAOA is represented locally as ideal statevector evolution over a diagonal cost Hamiltonian and a transverse-field mixer. This is useful for checking the mathematical bridge from security objectives to gate-model optimization workflows. It does not model backend noise, scheduling, transpilation, calibration, or hardware queue behavior.

## No Quantum Advantage Claim

Noetheris does not claim that gate-model circuits outperform classical verification. The mapping is a research interface for checking whether structural security predicates can be encoded coherently as reversible Boolean oracles before any backend-specific compilation work is attempted.
