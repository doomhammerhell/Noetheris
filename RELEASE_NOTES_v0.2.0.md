## Noetheris v0.2.0 — External Solver Boundary

Noetheris v0.2.0 is a narrow research-kernel release focused on the boundary between deterministic local models and optional external solver ecosystems.

The release strengthens what Noetheris exports, what an external tool may return, and what Noetheris verifies locally before treating a solver candidate as evidence.

### Included

- Canonical QUBO exchange parity across internal QUBO evaluation, canonicalized models, structured exchange payloads, and optional local Ocean `dimod.BinaryQuadraticModel` energy checks.
- Local Ocean BQM reporting that runs without D-Wave credentials, sampler calls, cloud tokens, or hardware submission.
- Qiskit-facing oracle semantic reports for small predicates, with exact local truth-table authority and optional local circuit summaries when Qiskit is installed.
- External solver replay artifacts using schema `noetheris.external_solver_replay.v1`.
- Explicit replay rejection reasons for problem-hash mismatch, compiled-model-hash mismatch, missing variables, unknown variables, reported-energy mismatch, malformed solver metadata, and malformed embedding metadata.
- Certificate validation that fails closed when embedded external replay evidence is rejected, inconsistent, or artifact-hash invalid.
- Deterministic solver-boundary evidence under `docs/results/solver_boundary_evidence.json`.
- Lean replay-boundary kernel and TLA+ single-candidate replay state sketch, scoped to simplified formal predicates.
- macOS Python runner selection hardened for universal Python environments where shell architecture and installed NumPy architecture can differ.

### Positioning

Noetheris v0.2.0 does not execute IBM Quantum or D-Wave hardware, does not benchmark cloud solvers, does not infer hardware embedding quality, and does not claim quantum advantage.

External solver metadata and embedding metadata are recorded as supplied evidence. Local replay remains the verification authority: hashes, assignment domains, and energies must verify locally before a candidate can be accepted.

### Validation

The release gate is:

```bash
bash scripts/run_audit.sh
```

The audit covers Rust check/test/fmt/clippy, Python compilation and pytest, examples, CLI checks, deterministic release evidence generation, benchmarks, optional-backend boundary checks, Lean build when available, and release-residue source scans.
