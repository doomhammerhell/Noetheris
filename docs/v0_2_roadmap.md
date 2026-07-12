# Noetheris v0.2.0 Roadmap

Noetheris v0.2.0 should be a narrow external solver boundary release, not a broad platform expansion.

The purpose is to make the handoff between Noetheris and optional solver ecosystems more precise: what is exported, what an external tool may return, and what Noetheris verifies locally before treating the result as evidence.

## Scope

1. Canonical QUBO exchange

   Export canonical binary QUBO models with explicit variables, offset, linear terms, quadratic terms, normalization rules, and deterministic model hashes.

2. Ocean local parity

   When `dimod` is installed, build a `dimod.BinaryQuadraticModel` locally and compare assignment energy against Noetheris energy. No sampler, cloud token, or D-Wave credential is required.

3. Qiskit local oracle boundary

   Export small Boolean predicates into exact truth-table oracle reports and, when Qiskit is installed, local `QuantumCircuit` summaries. IBM Runtime and IBM Quantum credentials remain outside the default path.

4. External witness replay

   Treat solver output as an untrusted witness. Replay must verify the problem hash, compiled model hash, assignment domain, reported energy, and solver metadata.

5. Documentation

   Make embedding metadata explicit. Noetheris may record externally supplied embedding data, but it must not infer hardware embedding quality locally.

## Non-Goals

- Hardware execution.
- Cloud solver benchmarking.
- Minor-embedding optimization.
- Quantum advantage claims.
- Claims that deployed cryptography is compromised.
- Production security certification.

## Acceptance Gate

The v0.2.0 release is ready only if:

- `bash scripts/run_audit.sh` passes.
- Ocean and Qiskit examples run without credentials.
- Example outputs are deterministic on the default local path.
- Optional Ocean/Qiskit packages enrich reports without changing the trust boundary.
- Documentation states that local replay, not external solver output alone, is the verification authority.
