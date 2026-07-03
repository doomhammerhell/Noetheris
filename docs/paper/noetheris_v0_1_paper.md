# Noetheris v0.1.0: Structural Quantum Security Kernel

## Abstract

Noetheris is a local-first research engineering kernel for representing security-critical systems as structural objects and compiling bounded instances into QUBO/Ising objectives, reversible Boolean-oracle artifacts, deterministic certificates, continuous-variable diagnostics, and small formal models. The v0.1.0 release is intentionally bounded: it provides executable encodings, replayable witnesses, and release evidence artifacts without claiming quantum advantage, cryptographic compromise, or hardware performance.

## Problem Statement

Security failures often arise from structure rather than from isolated components: invalid state reachability, adversarial schedules, dependency-order violations, threshold-policy gaps, long-lived cryptographic exposure, and finite-simulation boundary artifacts. Noetheris models these systems as:

```text
S = (N, E, C, I, O, A, M)
```

where `N` are typed nodes, `E` are typed edges, `C` are constraints, `I` are invariants, `O` are objectives, `A` are adversary annotations, and `M` is deterministic metadata. A useful release kernel must make this structure executable and must bind solver output to replayable checks.

## Structural IR

The Structural IR supports states, assets, actors, policies, quantum modes, directed transitions, dependencies, constraints, objectives, adversarial labels, risk annotations, cryptographic assets, and migration candidates. Python and Rust validators reject malformed references and produce canonical hashes over sorted JSON representations. These hashes are used as problem identifiers in compiled artifacts and certificates.

## QUBO And Ising Compilation

Supported structural problems lower into:

```text
E_Q(x) = c + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j,
```

with binary variables, linear terms, quadratic terms, constants, constraints, objective labels, and reverse witness maps. The Ising convention is:

```text
x_i = (1 - z_i) / 2,
H_C = c' I + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j.
```

The exchange boundary canonicalizes QUBO terms before export: duplicate and reversed pairs are aggregated, while self-quadratic binary terms are folded into linear terms because `x*x = x` for `x in {0,1}`. Exact local solving is capped to small instances, but structural validation and D-Wave/Ocean export are not capped by that solver bound.

## Bounded Invariant Search

For transition-system search, Noetheris enumerates bounded paths and chooses one path variable:

```text
E(x) =
  lambda_validity  P_validity(x)
+ lambda_invariant P_invariant(x)
+ lambda_path      C_path(x)
+ lambda_adversary C_adversary(x).
```

The v0.1.0 encoding is deliberately simple and inspectable. It is a bounded witness compiler, not a full temporal-logic model checker.

## PQC Migration Optimization

The migration optimizer models assets, dependencies, candidates, compliance requirements, harvest-now-decrypt-later exposure, downtime, incompatibility, and dependency blockers:

```text
E(x) =
  lambda_risk       R_residual(x)
+ lambda_cost       C_migration(x)
+ lambda_downtime   D_operational(x)
+ lambda_incompat   I_incompatibility(x)
+ lambda_dependency P_dependency(x)
+ lambda_compliance G_compliance(x).
```

The output includes an ordered migration plan, residual risk, blocking dependencies, QUBO model, and certificate. The v0.1.0 weights are research defaults; production use would require domain-specific calibration and sensitivity analysis.

## D-Wave/Ocean Boundary

Noetheris exports a structured BINARY QUBO payload with schema version, variables, offset, linear terms, quadratic terms, normalization policy, and model hash. When Ocean is installed, the same canonical model is used to construct a local `dimod.BinaryQuadraticModel`. No D-Wave credentials are required.

External solver output is treated as an untrusted witness until replay verifies:

- `problem_hash`;
- `compiled_model_hash`;
- exact assignment variable set;
- reported energy against local `model.evaluate`;
- solver metadata;
- embedding metadata when supplied by a real external run.

Local release evidence records `embedding_status: "not_requested"`.

## IBM/Qiskit Boundary

Boolean predicates are represented as:

```text
O_phi |x>|y> = |x>|y xor phi(x)>.
```

Noetheris emits exact truth tables, symbolic compute/apply/uncompute oracle gates, cleanup-gate metrics, QASM-like text, and optional Qiskit `QuantumCircuit` summaries for small predicates. Truth-table synthesis is exponential in predicate width and is used only as a correctness artifact in v0.1.0.

The QAOA example performs exact local statevector simulation for a tiny QUBO-derived diagonal Hamiltonian. It is a mapping check, not a backend-performance result.

## Continuous-Variable Diagnostics

The CV module uses finite Fock spaces with:

```text
q = (a + a^\dagger) / sqrt(2),
p = (a - a^\dagger) / (i sqrt(2)),
[q, p] = i.
```

Finite truncation modifies the annihilation/creation commutator:

```text
[a_K, a_K^\dagger] = I_K - K |K-1><K-1|.
```

For the square-lattice GKP convention used in Noetheris, logical shifts are separated by `sqrt(pi)` and stabilizer translations by `2 sqrt(pi)`. The diagnostic stabilizers therefore use:

```text
S_q = exp(-i 2 sqrt(pi) p),
S_p = exp( i 2 sqrt(pi) q).
```

Boundary population, restricted commutator error, stabilizer expectations, entanglement diagnostics, Gaussian/Fock moments, and Lindblad leakage are certificate inputs. These are finite-cutoff diagnostics, not a claim of production fault tolerance.

## Certificate Semantics

Certificate verification is model-relative:

```text
Verify(C, P) :=
  hash(P) = C.problem_hash
  and recompute_energy(C) = C.total_energy
  and no violated constraints remain
  and deterministic metadata is declared.
```

A valid certificate proves that the encoded witness satisfies the encoded checks. It does not prove that the input model captures all real-world assumptions.

## Release Evidence

The release evidence is generated with:

```bash
python3 scripts/generate_release_results.py
```

| Artifact | Purpose |
| --- | --- |
| `docs/results/invariant_witness.json` | bounded consensus-safety witness and certificate data |
| `docs/results/compiled_qubo_solution.json` | Structural IR compilation, exact QUBO solution, D-Wave exchange payload, and external-sample replay |
| `docs/results/pqc_migration_plan.json` | PQC migration plan, residual risk, blockers, QUBO, and certificate |
| `docs/results/oracle_truth_table.json` | Boolean truth table, reversible oracle metrics, and QASM-like text |
| `docs/results/qaoa_hamiltonian_report.json` | QUBO-to-Ising lowering and exact local QAOA check |
| `docs/results/cv_gkp_diagnostic_certificate.json` | finite Fock/GKP diagnostic certificate |
| `docs/results/benchmark_report.json` | deterministic benchmark baseline with hashes and replay status |

## Experiments

The benchmark baseline is deterministic and records `runtime_seconds: null` by design. It captures problem hashes, compiled-model hashes, assignment hashes, solver labels, energies, replay status, oracle metrics, CV leakage, and embedding status. Host-specific timing can be collected separately with:

```bash
python3 benchmarks/run_measured_benchmarks.py
```

Measured runs include Python, platform, machine, processor, and commit metadata and should be interpreted as local observations rather than release invariants.

## Formal Artifacts

Lean files define small kernels for graph invariants, certificate consistency, Structural IR validity, QUBO energy, migration policy predicates, circuit-oracle truth, and Ising energy. TLA+ files define compact scenario models for consensus, threshold policy, PQC migration, and saga terminal consistency. These artifacts are formal anchors for small kernels, not whole-repository proofs.

## Limitations

Noetheris v0.1.0 is bounded by design:

- exact solving is exponential and locally capped;
- seeded annealing is a deterministic heuristic baseline;
- penalty calibration remains a modeling responsibility;
- truth-table circuit synthesis is small-predicate only;
- CV/GKP diagnostics are finite-cutoff approximations;
- external solver results require local replay before trust;
- hardware performance requires separately documented runs with solver and embedding provenance.

## Security And Ethics

Noetheris is defensive research infrastructure. It does not claim that deployed cryptography is broken, does not claim quantum advantage, and does not claim production fault tolerance.
