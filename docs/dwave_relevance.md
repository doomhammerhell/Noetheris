# D-Wave Relevance

Noetheris lowers structural security problems into QUBO and Ising forms with explicit constraints, penalty weights, variables, and reverse witness mappings.

The relevant workflow is:

```text
Structural IR -> QUBO -> Ising -> exact or seeded annealing baseline -> certificate replay
```

The optional Ocean boundary exports a QUBO-compatible dictionary and reports availability without requiring credentials. Hardware performance claims require separately documented runs with solver configuration, embedding context, and replayed certificates.
