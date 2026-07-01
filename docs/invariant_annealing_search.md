# Invariant Annealing Search

Invariant search compiles bounded transition paths into a QUBO. Candidate paths become binary variables. Penalties enforce single-witness selection and objective components penalize path cost, adversarial transitions, budget pressure, and failure to reach a declared forbidden condition when counterexamples are requested.

The model is:

```text
E(x) =
  lambda_validity   P_validity(x)
+ lambda_initial    P_initial(x)
+ lambda_transition P_transition(x)
+ lambda_invariant  P_invariant(x)
+ lambda_path       C_path(x)
+ lambda_adversary  C_adversary(x)
+ lambda_budget     P_budget(x)
```

The v0.1.0 implementation uses bounded path enumeration for small transition systems. This makes witness extraction and certificate replay direct.
