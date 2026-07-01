import Noetheris.Basic

namespace Noetheris

structure EnergyTerm where
  name : String
  weight : Nat
  value : Nat
deriving Repr, DecidableEq

def EnergyTerm.contribution (term : EnergyTerm) : Energy :=
  term.weight * term.value

structure EnergyCertificate where
  algorithmName : String
  energyTerms : List EnergyTerm
  selectedVariables : List (String × Bool)
  satisfiedConstraints : List Constraint
  violatedConstraints : List Constraint
  totalEnergy : Energy
deriving Repr

def CertificateValid (certificate : EnergyCertificate) : Prop :=
  certificate.violatedConstraints = [] ∧
    allSatisfied certificate.satisfiedConstraints = true

theorem certificate_valid_when_no_violations
    (certificate : EnergyCertificate)
    (hNoViolations : certificate.violatedConstraints = [])
    (hSatisfied : allSatisfied certificate.satisfiedConstraints = true) :
    CertificateValid certificate := by
  exact And.intro hNoViolations hSatisfied

def exampleCertificate : EnergyCertificate :=
  {
    algorithmName := "invariant_annealing_search",
    energyTerms := [{ name := "path", weight := 1, value := 2 }],
    selectedVariables := [("path_0", true)],
    satisfiedConstraints := [acceptedConstraint],
    violatedConstraints := [],
    totalEnergy := 2
  }

#eval allSatisfied exampleCertificate.satisfiedConstraints

end Noetheris
