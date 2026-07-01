# Structural IR

Structural IR is the internal representation for Noetheris v0.1.0. It describes security-critical systems as typed nodes, typed edges, constraints, invariants, objectives, adversarial actions, risk annotations, cryptographic annotations, and witness variables.

The canonical object is:

```text
S = (N, E, C, I, O, A, M)
```

where `N` are structural nodes, `E` typed directed edges, `C` constraints, `I` invariant predicates, `O` objective terms, `A` adversary actions, and `M` deterministic metadata. Canonical serialization uses sorted JSON and SHA-256 hashing.

The IR supports state-transition systems, dependency graphs, threshold policies, migration graphs, and CV/GKP diagnostic scenarios. Validation rejects unknown endpoints, duplicate identifiers, invalid weights, invalid risk annotations, and invalid migration candidates.
