namespace Noetheris

structure BinaryTerm where
  varName : String
  coeff : Nat
deriving Repr

def evalLinearTerm (assignment : String → Bool) (term : BinaryTerm) : Nat :=
  if assignment term.varName then term.coeff else 0

def evalPenaltyOnly (assignment : String → Bool) (terms : List BinaryTerm) : Nat :=
  terms.foldl (fun acc term => acc + evalLinearTerm assignment term) 0

theorem penalty_only_energy_nonnegative
    (assignment : String → Bool)
    (terms : List BinaryTerm) :
    0 ≤ evalPenaltyOnly assignment terms := by
  exact Nat.zero_le _

end Noetheris
