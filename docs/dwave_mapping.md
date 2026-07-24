# D-Wave Mapping

## QUBO And Ising Formulation

Noetheris expresses supported structural security problems as binary objectives:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j.
```

The Ising lowering uses the Pauli-Z convention `x = (1 - z) / 2`, where `z = +1` is bit `0` and `z = -1` is bit `1`. Tests check QUBO/Ising energy equivalence on small instances.

## Export Contract

The D-Wave/Ocean boundary exports a structured BINARY QUBO payload:

- schema: `noetheris.qubo.exchange.v1`;
- variable ordering;
- constant offset;
- structured linear terms;
- structured quadratic terms;
- canonical model hash;
- normalization policy for duplicate, reversed, and self-quadratic terms.

Self-quadratic binary terms are folded into linear terms because `x*x = x` for `x in {0,1}`. Duplicate and reversed pairs are aggregated before export. This preserves the internal energy surface while producing a deterministic exchange artifact.

The exchange payload has the same assignment domain as the source model. For any complete assignment `x`, the replay energy is:

```text
E_exchange(x) =
  offset
  + sum(linear_terms[i].coefficient where x[linear_terms[i].variable] = 1)
  + sum(quadratic_terms[j].coefficient
        where x[quadratic_terms[j].left] = 1
          and x[quadratic_terms[j].right] = 1).
```

The v0.2 parity harness checks:

- original `QuboModel.evaluate(x)`;
- canonicalized `QuboModel.evaluate(x)`;
- structured exchange-payload evaluation;
- optional Ocean `dimod.BinaryQuadraticModel.energy(x)` when Ocean is installed.

These values must agree for every assignment of each small parity fixture. Larger export-only models are validated and serialized without invoking the bounded exhaustive solver.

When Ocean is installed, Noetheris also constructs a `dimod.BinaryQuadraticModel` locally. This does not require D-Wave credentials. The BQM summary records variable count, interaction count, vartype, and `to_qubo` offset.

The executable local example is:

```bash
python3 examples/dwave_ocean_exchange.py
```

It emits the canonical exchange payload, optional local Ocean parity data, the exact local reference assignment, and a replay result that verifies hashes and energy.

## Solver Boundary

Exact local solving is capped to small instances. QUBO validation and export are not capped by that exact-solver bound. This separation matters: large models may be valid exchange artifacts even when exhaustive local search is infeasible.

External solver samples are treated as untrusted witnesses. Replay must check:

- problem hash;
- compiled-model hash;
- exact assignment variable set;
- reported energy against local `model.evaluate`;
- solver metadata;
- embedding metadata when a hardware or hybrid run supplies it.

Local baselines use `embedding_status: "not_requested"` and `embedding: null`. Hardware embedding, chain strength, anneal parameters, chain-break fraction, solver topology, and sample provenance must come from an actual external run and are never inferred by Noetheris.

## No Hardware Claim

The repository runs without Ocean, D-Wave credentials, or paid APIs. The v0.1.0 benchmark artifacts are local replay baselines. They are not hardware comparisons and do not imply quantum speedup.
