# Circuit Oracle Compiler

The oracle compiler maps small Boolean structural predicates into symbolic reversible circuits. Supported expressions include variables, constants, AND, OR, XOR, negation, implication, and equality.

For predicate `phi`, the oracle relation is:

```text
O_phi |x>|y> = |x>|y xor phi(x)>.
```

The compiler emits symbolic compute/apply/uncompute gates, a truth table, QASM-like text, cost metrics, cleanup-gate counts, and a reversibility check. Optional Qiskit truth-table synthesis is available for small predicates when Qiskit is installed; no IBM Quantum credentials are required.

The Qiskit semantic report checks direct `BoolExpr` evaluation against the symbolic oracle truth table. If Qiskit is installed, Noetheris also records local `QuantumCircuit` summary metadata produced from that verified table. This is intentionally exponential in logical variable count and is scoped to small predicates.
