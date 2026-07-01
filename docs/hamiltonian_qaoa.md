# Hamiltonian And QAOA Mapping

## QUBO To Ising

Noetheris represents a QUBO objective as:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j
```

with `x_i in {0, 1}`. The Ising mapping uses `x_i = (1 - z_i) / 2`, where `z_i in {-1, +1}`. Under this convention, binary `false` maps to spin `+1` and binary `true` maps to spin `-1`.

The equivalent Ising energy is:

```text
E_I(z) = c' + sum_i h_i z_i + sum_{i<j} J_ij z_i z_j
```

where:

```text
c'   = c + (1/2) sum_i a_i + (1/4) sum_{i<j} b_ij
h_i  = -a_i / 2 - (1/4) sum_j b_ij
J_ij = b_ij / 4
```

The implementation tests the invariant `E_Q(x) = E_I(z(x))` over all assignments for small instances.

## Diagonal Hamiltonian

The Ising objective corresponds to a diagonal cost Hamiltonian:

```text
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j
```

This Hamiltonian is an exact mathematical representation of the classical objective over computational-basis states. It is not a hardware noise model and does not include control errors, decoherence, readout error, embedding distortion, or calibration dynamics.

## QAOA Simulation

The local QAOA simulator applies the p-layer idealized evolution:

```text
|psi(gamma, beta)> =
  product_l exp(-i beta_l sum_i X_i) exp(-i gamma_l H_C) |+>^n
```

It computes the exact statevector for tiny instances, derives the output probability distribution, and evaluates:

```text
<H_C> = sum_x Pr[x] E_Q(x)
```

The simulator is bounded to small variable counts because it is exponential in `n`. It exists to verify mappings and study behavior on small structural security objectives, not to assert performance on quantum hardware.

## Verification Boundary

QAOA output is treated as a candidate distribution. Any selected assignment still needs deterministic objective evaluation and certificate validation. This is the same trust boundary used for annealing or external solver workflows.
