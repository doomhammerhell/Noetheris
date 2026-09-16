import Noetheris.Basic

namespace Noetheris

structure ReplayContext where
  expectedProblemHash : String
  expectedCompiledModelHash : String
deriving Repr, DecidableEq

structure ReplayCandidate where
  submittedProblemHash : String
  submittedCompiledModelHash : String
  reportedEnergy : Energy
  recomputedEnergy : Energy
  assignmentComplete : Bool
  metadataWellFormed : Bool
deriving Repr, DecidableEq

def HashIdentityHolds (context : ReplayContext) (candidate : ReplayCandidate) : Prop :=
  candidate.submittedProblemHash = context.expectedProblemHash ∧
    candidate.submittedCompiledModelHash = context.expectedCompiledModelHash

def EnergyAgreementHolds (candidate : ReplayCandidate) : Prop :=
  candidate.reportedEnergy = candidate.recomputedEnergy

def ReplayAccepted (context : ReplayContext) (candidate : ReplayCandidate) : Prop :=
  HashIdentityHolds context candidate ∧
    EnergyAgreementHolds candidate ∧
    candidate.assignmentComplete = true ∧
    candidate.metadataWellFormed = true

theorem accepted_candidate_preserves_energy_agreement
    (context : ReplayContext)
    (candidate : ReplayCandidate)
    (hAccepted : ReplayAccepted context candidate) :
    candidate.reportedEnergy = candidate.recomputedEnergy := by
  exact hAccepted.right.left

theorem accepted_candidate_matches_problem_hash
    (context : ReplayContext)
    (candidate : ReplayCandidate)
    (hAccepted : ReplayAccepted context candidate) :
    candidate.submittedProblemHash = context.expectedProblemHash := by
  exact hAccepted.left.left

theorem accepted_candidate_has_complete_assignment
    (context : ReplayContext)
    (candidate : ReplayCandidate)
    (hAccepted : ReplayAccepted context candidate) :
    candidate.assignmentComplete = true := by
  exact hAccepted.right.right.left

def replayContextExample : ReplayContext :=
  {
    expectedProblemHash := "sha256:problem",
    expectedCompiledModelHash := "sha256:compiled"
  }

def acceptedReplayCandidateExample : ReplayCandidate :=
  {
    submittedProblemHash := "sha256:problem",
    submittedCompiledModelHash := "sha256:compiled",
    reportedEnergy := 10,
    recomputedEnergy := 10,
    assignmentComplete := true,
    metadataWellFormed := true
  }

#eval acceptedReplayCandidateExample.reportedEnergy

end Noetheris
