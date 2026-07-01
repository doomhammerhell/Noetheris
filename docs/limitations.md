# Limitations

Noetheris v0.1.0 is a bounded research kernel. Its boundaries are part of the scientific model.

- Structural IR validity is syntactic and semantic only to the extent encoded by the declared constraints.
- Certificate validity is relative to model correctness, canonical hashing, and replayed energy arithmetic. A correct certificate cannot repair an incorrect model.
- Exact QUBO solving is exponential and bounded to small instances.
- Simulated annealing is a deterministic heuristic baseline under seed, not a global optimality guarantee.
- QUBO penalty calibration remains a modeling responsibility; weak penalties can encode the wrong preference order.
- Circuit oracle compilation is limited to small Boolean predicates and symbolic reversible circuits.
- Optional Qiskit and D-Wave adapters are export boundaries, not default hardware benchmark paths.
- CV/GKP diagnostics use finite Fock cutoffs. Boundary artifacts are measured and certified, not ignored.
- Approximate GKP states in this release are finite-dimensional diagnostic objects, not production fault-tolerant logical states.
- Lean and TLA+ artifacts cover simplified kernels and scenario models, not the entire implementation.
- Benchmark artifacts are local baselines and do not compare against IBM Quantum or D-Wave hardware.

These boundaries define the next research frontier: stronger certificate semantics, richer model checking, penalty calibration, sparse/tensor acceleration, and externally replayed solver integrations.
