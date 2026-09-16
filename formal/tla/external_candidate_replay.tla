---- MODULE external_candidate_replay ----
EXTENDS FiniteSets

CONSTANTS
  ExpectedProblemHash,
  ExpectedCompiledModelHash,
  SubmittedProblemHash,
  SubmittedCompiledModelHash,
  ReportedEnergy,
  RecomputedEnergy,
  AssignmentComplete,
  MetadataWellFormed

VARIABLES state, reasons

Init ==
  /\ state = "submitted"
  /\ reasons = {}

HashIdentityHolds ==
  /\ SubmittedProblemHash = ExpectedProblemHash
  /\ SubmittedCompiledModelHash = ExpectedCompiledModelHash

EnergyAgreementHolds ==
  ReportedEnergy = RecomputedEnergy

CandidateWellFormed ==
  /\ AssignmentComplete
  /\ MetadataWellFormed

Verify ==
  /\ state = "submitted"
  /\ HashIdentityHolds
  /\ EnergyAgreementHolds
  /\ CandidateWellFormed
  /\ state' = "verified"
  /\ reasons' = {}

RejectHash ==
  /\ state = "submitted"
  /\ ~HashIdentityHolds
  /\ state' = "rejected"
  /\ reasons' = reasons \cup {"hash_mismatch"}

RejectEnergy ==
  /\ state = "submitted"
  /\ HashIdentityHolds
  /\ ~EnergyAgreementHolds
  /\ state' = "rejected"
  /\ reasons' = reasons \cup {"energy_mismatch"}

RejectDomain ==
  /\ state = "submitted"
  /\ HashIdentityHolds
  /\ EnergyAgreementHolds
  /\ ~AssignmentComplete
  /\ state' = "rejected"
  /\ reasons' = reasons \cup {"assignment_incomplete"}

RejectMetadata ==
  /\ state = "submitted"
  /\ HashIdentityHolds
  /\ EnergyAgreementHolds
  /\ AssignmentComplete
  /\ ~MetadataWellFormed
  /\ state' = "rejected"
  /\ reasons' = reasons \cup {"metadata_malformed"}

Next ==
  \/ Verify
  \/ RejectHash
  \/ RejectEnergy
  \/ RejectDomain
  \/ RejectMetadata

StatusDomain ==
  state \in {"submitted", "verified", "rejected"}

VerifiedImpliesEnergyAgreement ==
  state = "verified" => EnergyAgreementHolds

VerifiedImpliesHashIdentity ==
  state = "verified" => HashIdentityHolds

Spec ==
  Init /\ [][Next]_<<state, reasons>>

====
