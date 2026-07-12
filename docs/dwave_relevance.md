# D-Wave Relevance

Noetheris is relevant to annealing and hybrid optimization because it turns structural security questions into explicit binary objectives with replayable witnesses. The useful engineering boundary is:

```text
Structural IR
  -> QUBO with variables, penalties, objectives, reverse map
  -> canonical BINARY exchange payload
  -> optional dimod.BinaryQuadraticModel
  -> solver sample
  -> local replay against hashes and energy
```

## What Is Implemented

- QUBO models with linear, quadratic, and constant terms.
- Canonicalization that aggregates duplicate and reversed pairs and folds self-quadratic binary terms into linear coefficients.
- QUBO-to-Ising lowering under `x = (1 - z) / 2`.
- Exact local solving for small instances.
- Deterministic seeded annealing baseline for local experiments.
- Structured D-Wave exchange payload with schema version and model hash.
- Optional `dimod.BinaryQuadraticModel` construction when Ocean is installed.
- External-sample replay against `problem_hash`, `compiled_model_hash`, assignment variables, and reported energy.

## What Is Deliberately Outside v0.1.0

- Hardware submission.
- Embedding search.
- Chain-strength selection.
- Chain-break handling.
- Advantage or Advantage2 performance claims.
- Hybrid solver benchmarking.

These fields are represented as explicit metadata boundaries. Local artifacts use `embedding_status: "not_requested"`. A future external run must supply solver id, topology, embedding, chain settings, anneal parameters, sample counts, and chain-break statistics before Noetheris can replay the sample as a documented external witness.

## Minimal Local Export

```python
from noetheris.backends import export_qubo_to_dwave
from noetheris.qubo import QuboModel

model = QuboModel(variables=["x"], linear={"x": -1.0})
payload = export_qubo_to_dwave(model)
assert payload["credential_required"] is False
assert payload["exchange"]["vartype"] == "BINARY"
```

For a fuller no-credential exchange and replay report:

```bash
python3 examples/dwave_ocean_exchange.py
```

## Minimal Replay

```python
from noetheris.qubo import replay_external_solution

result = replay_external_solution(
    compiled_problem,
    {"x": True},
    reported_energy=-1.0,
    problem_hash=compiled_problem.problem_hash,
    compiled_model_hash=compiled_problem.compiled_model_hash,
)
assert result["status"] == "verified"
```

The replay relation is the trust boundary: a solver result is useful only after local deterministic verification.
