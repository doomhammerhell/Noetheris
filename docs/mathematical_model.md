# Mathematical Model

## Structural System

Noetheris models a system as:

```text
S = (N, E, C, I, O, A, M)
```

`N` are typed nodes, `E` typed directed edges, `C` constraints, `I` invariants, `O` objectives, `A` adversary actions, and `M` deterministic metadata.

## Transition Systems

For invariant search, a bounded witness is a path:

```text
p = (s_0, s_1, ..., s_k), k <= d.
```

Edges must exist in the Structural IR. Forbidden-state and forbidden-transition invariants define counterexample targets.

## QUBO

Compiled objectives have the form:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j.
```

Assignments are strict: all model variables must be present and unknown variables are rejected.

## Ising And Hamiltonian

Using `x_i = (1 - z_i)/2`:

```text
E_I(z) = c' + sum_i h_i z_i + sum_{i<j} J_ij z_i z_j.
```

The corresponding diagonal Hamiltonian is:

```text
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j.
```

## Certificate Semantics

Certificates bind problem hash, compiled-model hash where available, selected variables, witness assignment, energy terms, constraints, proof obligations, solver metadata, seed, and deterministic timestamp strategy.

Validation recomputes energy contributions and rejects inconsistent totals, violated constraints, invalid status, and nondeterministic timestamp strategy.

## PQC Migration Risk

Migration risk is input-relative:

```text
R_residual = sum_a risk(a) * remaining_exposure(a).
```

Harvest-now-decrypt-later assets may carry an exposure multiplier. Dependency penalties encode the rule that dependent assets should not migrate ahead of required custody or compatibility assets.

## CV/Fock Boundary

In a finite Fock cutoff `K`:

```text
[a_K, a_K^\dagger] = I_K - K |K-1><K-1|.
```

Boundary population and restricted commutator error quantify whether a diagnostic is operating away from the truncation boundary.
