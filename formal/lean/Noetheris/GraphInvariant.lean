import Noetheris.Basic

namespace Noetheris

structure Edge where
  source : String
  target : String
deriving Repr, DecidableEq

structure FiniteGraph where
  states : List String
  edges : List Edge
deriving Repr

def containsString (needle : String) (values : List String) : Bool :=
  values.any (fun value => value == needle)

def NoForbiddenState (path forbidden : List String) : Prop :=
  ∀ state, state ∈ path → state ∉ forbidden

theorem empty_forbidden_states_safe (path : List String) :
    NoForbiddenState path [] := by
  intro state _ impossible
  cases impossible

def consensusPath : List String :=
  ["round0_locked_a", "round1_prepared_a", "commit_a"]

#eval containsString "commit_a" consensusPath

end Noetheris
