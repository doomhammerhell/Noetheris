# Circuit Oracle Compiler

The oracle compiler maps small Boolean structural predicates into symbolic reversible circuits. Supported expressions include variables, constants, AND, OR, XOR, negation, implication, and equality.

For predicate `phi`, the oracle relation is:

```text
O_phi |x>|y> = |x>|y xor phi(x)>.
```

The compiler emits symbolic gates, a truth table, QASM-like text, cost metrics, and a reversibility check. Optional Qiskit export is available when Qiskit is installed; no IBM Quantum credentials are required.
