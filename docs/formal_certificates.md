# Formal Energy Certificates

## Purpose

Noetheris treats optimization and diagnostic outputs as untrusted until replayed by a deterministic verifier.

## Schema

Certificates include:

- certificate version and repository version;
- problem type;
- canonical problem hash;
- solver or algorithm name;
- deterministic seed;
- input file hash where supplied;
- compiled model hash where supplied;
- selected variables;
- witness assignment;
- objective value and energy breakdown;
- satisfied and violated constraints;
- residual risk where applicable;
- proof obligations;
- verification status;
- deterministic timestamp strategy;
- reproducibility metadata.

## Validation

Validation recomputes energy contributions, recomputes total energy, checks constraint polarity, rejects violated constraints for accepted certificates, checks optional problem hash, checks status consistency, and rejects nondeterministic timestamp strategies.

## Replay

```bash
python3 -m noetheris.certificates.validate examples/example_energy_certificate.json
python3 -m noetheris.certificates.replay examples/example_energy_certificate.json
```

Replay emits validation status and certificate fingerprint. Stronger model-specific replay is represented by compiled model hashes and strict QUBO energy evaluation in the compiler layer.

## Formal Surface

Lean models a simplified certificate-validity predicate and small true lemmas. The executable Python/Rust validators are the release enforcement path; Lean artifacts define reviewable kernels rather than whole-repository proofs.
