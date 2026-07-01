namespace Noetheris

abbrev Energy := Nat

structure Constraint where
  name : String
  satisfied : Bool
deriving Repr, DecidableEq

def allSatisfied (constraints : List Constraint) : Bool :=
  constraints.all (fun constraint => constraint.satisfied)

def acceptedConstraint : Constraint :=
  { name := "graph_valid", satisfied := true }

#eval allSatisfied [acceptedConstraint]

end Noetheris
