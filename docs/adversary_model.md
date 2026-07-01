# Adversary Model

## Byzantine Adversary

For distributed protocols, the adversary may cause a bounded set of participants or transitions to behave inconsistently with the honest path. The model captures this through adversarial transition labels and budget constraints.

## Delayed Messages

Delayed messages are represented as state transitions that move the system into alternate schedule states. The current examples do not model network timing continuously; they encode schedule-relevant states directly.

## Partial Compromise

Partial compromise is modeled as local control over assets, keys, signers, or transition choices. Noetheris assumes that compromise is bounded by the input model and does not infer hidden trust relationships.

## Cryptographic Transition Risk

Migration risk includes current algorithm exposure, compliance pressure, operational downtime, dependency order, and incompatibility. The model is designed to expose the tradeoff rather than produce an absolute security score.

## Harvest-Now-Decrypt-Later Exposure

Long-lived encrypted archives are treated differently from ephemeral authentication assets. Captured ciphertext may become valuable under future cryptanalytic capability, so the migration optimizer can assign amplified residual exposure to archive assets.

## Supply-Chain Constraints

HSMs, KMS services, firmware signing systems, and certificate chains create supply-chain dependencies. Migration plans that move dependent assets without their key custody or signing dependencies are penalized and surfaced as blocking dependencies.

## Forbidden Irresponsible Interpretations

Noetheris must not be interpreted as a tool for breaking production cryptography, validating real-world PQC hardness, or asserting that a quantum solver has produced a trustworthy result. Solver output is evidence only after deterministic certificate verification.
