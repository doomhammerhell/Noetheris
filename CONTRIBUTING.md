# Contributing

Noetheris accepts changes that improve correctness, reproducibility, formal clarity, or responsible security analysis.

## Engineering Standards

Contributions must preserve deterministic behavior, explicit error handling, and auditable outputs. New algorithms must define actors or inputs, state transitions or decision variables, objective terms, verification rules, and failure modes.

## Code Requirements

- Rust code must pass `cargo test --workspace` and `cargo fmt --check`.
- Python code must pass `pytest` and `python -m compileall python examples`.
- Examples must run without paid services or cloud credentials.
- Optional quantum integrations must fail closed and explain the missing dependency.
- Public claims must be backed by code, documentation, examples, tests, or explicit limitations.

## Documentation Requirements

Documentation must avoid unsupported claims of quantum advantage, cryptographic breaks, or production PQC assessment. If an algorithm is toy-scale, experimental, or bounded by exhaustive search, state that directly.

## Review Criteria

Reviews prioritize invariant preservation, threat model clarity, reproducibility, deterministic serialization, safe dependency boundaries, and correctness under malformed input.
