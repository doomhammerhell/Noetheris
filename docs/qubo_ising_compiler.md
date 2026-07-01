# QUBO/Ising Compiler

The compiler lowers supported Structural IR problems into binary quadratic models:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j.
```

Compiled problems contain variable metadata, named constraints, objective components, reverse mapping from binary solutions to structural witnesses, canonical problem hash, and compiled model hash.

The Ising mapping uses:

```text
x_i = (1 - z_i) / 2
```

which yields fields `h_i`, couplers `J_ij`, and a diagonal Hamiltonian:

```text
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j.
```

The exact solver is bounded. The deterministic simulated annealing solver is a local heuristic baseline with explicit seed control.
