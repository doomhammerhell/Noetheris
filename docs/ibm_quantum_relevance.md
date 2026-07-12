# IBM Quantum Relevance

Noetheris is relevant to gate-model research because structural security predicates can be expressed as Boolean relations, reversible oracle mappings, and diagonal cost Hamiltonians. The v0.1.0 workflow is:

```text
Structural predicate
  -> Boolean expression
  -> truth table
  -> symbolic compute/apply/uncompute oracle
  -> QASM-like text
  -> optional Qiskit QuantumCircuit summary
  -> local certificate or replay artifact
```

## What Is Implemented

- Boolean expression AST: variables, constants, AND, OR, XOR, NOT, implication, and equality.
- Exact truth-table evaluation for small predicates.
- Symbolic reversible oracle with explicit compute, target XOR, and uncompute phases.
- Metrics for logical variables, ancilla count, cleanup gates, gate count, and depth estimate.
- QASM-like text for review without Qiskit.
- Optional Qiskit circuit synthesis from truth tables for small predicates when Qiskit is installed.
- Exact local QAOA p=1 statevector check over tiny QUBO-derived Hamiltonians.

## Trust Boundary

The Qiskit export path is an integration boundary, not a backend-execution claim. It requires no IBM Quantum credentials. It does not model transpilation, calibration, noise, scheduling, dynamic circuits, queue behavior, or fault-tolerant resources.

The symbolic oracle and Qiskit export are exponential in predicate width when synthesized from truth tables. That is acceptable for v0.1.0 release evidence because the goal is semantic correctness for small predicates, not scalable circuit synthesis.

## Minimal Local Export

```python
from noetheris.backends import export_bool_expr_to_qiskit
from noetheris.circuits import AND, BoolExpr

expr = AND(BoolExpr.var("a"), BoolExpr.var("b"))
payload = export_bool_expr_to_qiskit(expr, name="and_policy")
assert payload["credential_required"] is False
assert payload["truth_table"]["11"] == 1
```

For a fuller no-credential threshold-policy oracle report:

```bash
python3 examples/qiskit_oracle_export.py
```

## No Quantum Advantage Claim

Noetheris does not claim that these circuits outperform classical verification. The release provides a precise encoding and replay boundary so that structural predicates can be inspected before any backend-specific research is attempted.
