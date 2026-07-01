# D-Wave Mapping

## QUBO And Ising Formulation

Noetheris expresses structural security problems as binary objectives compatible with QUBO-style reasoning. A QUBO can be transformed into an Ising model by choosing a spin convention. The implementation uses the Pauli-Z convention `x = (1 - z) / 2`, where `z = +1` corresponds to computational-basis bit `0` and `z = -1` corresponds to bit `1`.

## Annealing Compatibility

Invariant search and migration planning produce binary variables, linear terms, quadratic terms, and constants. These are the components expected by annealing and hybrid optimization workflows.

## Hybrid Solver Relevance

Hybrid solvers are relevant when exact enumeration becomes infeasible. Noetheris treats any external solver result as a proposal that must be checked by local certificate validation.

## Local Fallback Solver

The repository includes an exhaustive deterministic solver for small instances. This allows CI and examples to run without D-Wave credentials or Ocean SDK installation.

## Ocean SDK Boundary

The optional D-Wave adapter translates `QuboModel` into a `dimod.BinaryQuadraticModel` only when Ocean is installed. If Ocean is absent, the adapter reports controlled unavailability and leaves local execution unaffected. Any external solver result is treated as an untrusted witness until Noetheris recomputes the energy, checks the structural hash, and validates the certificate locally.
