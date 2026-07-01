namespace Noetheris

def oracleMap (phi : Bool → Bool) (x y : Bool) : Bool × Bool :=
  (x, xor y (phi x))

theorem oracle_identity_truth (x y : Bool) :
    oracleMap (fun bit => bit) x y = (x, xor y x) := by
  rfl

theorem oracle_false_preserves_target (x y : Bool) :
    oracleMap (fun _ => false) x y = (x, y) := by
  cases y <;> rfl

end Noetheris
