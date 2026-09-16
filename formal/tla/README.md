# TLA+ Specifications

The TLA+ files model small safety surfaces used by Noetheris examples.

- `consensus_safety.tla` models single-value commit safety.
- `threshold_policy.tla` models authorization threshold, whitelist, and time-window safety.
- `pq_migration_policy.tla` models migration dependency ordering.
- `saga_failure_semantics.tla` models terminal consistency for a small compensating-transaction flow.
- `external_candidate_replay.tla` models the submitted, verified, and rejected states for a single external solver candidate under hash, energy, assignment-domain, and metadata checks.

They are compact specifications intended for review and bounded model-checking harnesses. The replay specification is scoped to a single candidate and does not assert correctness of the full executable implementation.
