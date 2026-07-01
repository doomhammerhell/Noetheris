# TLA+ Specifications

The TLA+ files model small safety surfaces used by Noetheris examples.

- `consensus_safety.tla` models single-value commit safety.
- `threshold_policy.tla` models authorization threshold, whitelist, and time-window safety.
- `pq_migration_policy.tla` models migration dependency ordering.
- `saga_failure_semantics.tla` models terminal consistency for a small compensating-transaction flow.

They are compact specifications intended for review and later bounded model-checking harnesses.
