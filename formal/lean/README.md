# Lean Artifacts

The Lean files define a compact formal surface for graph invariants, structural IR records, QUBO/Ising energy, migration policy predicates, circuit-oracle truth tables, and energy-certificate consistency. The release does not claim machine-checked end-to-end correctness; it provides small definitions and lemmas that compile and can be extended into a larger proof development.

Included modules:

- `Basic.lean`: elementary Boolean and list lemmas used by the package.
- `GraphInvariant.lean`: finite graph reachability and forbidden-state predicates.
- `EnergyCertificate.lean`: certificate consistency over explicit energy terms.
- `IsingEnergy.lean`: diagonal Ising energy definitions for Hamiltonian mapping.
- `StructuralIR.lean`: nodes, edges, constraints, and structural validity predicates.
- `QuboEnergy.lean`: binary assignments and QUBO energy evaluation.
- `MigrationPolicy.lean`: simple policy predicates for asset migration choices.
- `CircuitOracle.lean`: finite truth-table semantics for Boolean oracle evaluation.

Build with:

```bash
cd formal/lean
lake build
```
