# CV Quantum Bridge

Noetheris includes a bounded continuous-variable diagnostic bridge for truncated Fock spaces and approximate GKP states.

Implemented diagnostics include annihilation and creation operators, number, parity, position and momentum quadratures, commutator boundary profiles, restricted commutator error, boundary population, displacement, squeezing, GKP stabilizer expectations, entanglement measures, Gaussian/Fock moment extraction, and Lindblad evolution.

The quadrature convention is:

```text
q = (a + a^\dagger) / sqrt(2),
p = (a - a^\dagger) / (i sqrt(2)),
[q, p] = i
```

Under this convention, the square-lattice GKP logical shifts are separated by `sqrt(pi)` and the stabilizer translations are separated by `2 sqrt(pi)`. The implementation exposes this as `gkp_stabilizer_spacing()`.

Finite Fock truncation creates a boundary artifact:

```text
[a_K, a_K^\dagger] = I_K - K |K-1><K-1|.
```

Global canonical commutation therefore fails in finite dimension. Local low-energy diagnostics remain useful when boundary population is small and explicitly certified.

The CV/GKP module does not claim production fault tolerance. It provides finite-dimensional diagnostics for structural certificates and reproducible research scenarios.
