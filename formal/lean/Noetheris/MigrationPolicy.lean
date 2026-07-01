namespace Noetheris

structure Dependency where
  asset : String
  dependsOn : String
deriving Repr, DecidableEq

def DependencySatisfied (selected : String → Bool) (dep : Dependency) : Prop :=
  selected dep.asset → selected dep.dependsOn

def AllDependenciesSatisfied (selected : String → Bool) (deps : List Dependency) : Prop :=
  ∀ dep, dep ∈ deps → DependencySatisfied selected dep

theorem empty_dependencies_satisfied (selected : String → Bool) :
    AllDependenciesSatisfied selected [] := by
  intro dep impossible
  cases impossible

end Noetheris
