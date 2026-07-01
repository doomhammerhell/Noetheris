namespace Noetheris

def bitToSpin (bit : Bool) : Int :=
  if bit then -1 else 1

def pairContribution (left right coefficient : Int) : Int :=
  coefficient * left * right

def linearEnergy (fields spins : List Int) : Int :=
  (List.zip fields spins).foldl
    (fun acc pair => acc + pair.fst * pair.snd)
    0

def diagonalIsingEnergy
    (offset : Int)
    (fields spins : List Int)
    (couplings : List (Int × Int × Int)) : Int :=
  offset +
    linearEnergy fields spins +
    couplings.foldl
      (fun acc coupling =>
        acc + pairContribution coupling.fst coupling.snd.fst coupling.snd.snd)
      0

theorem bit_true_maps_to_negative_spin : bitToSpin true = -1 := by
  rfl

theorem bit_false_maps_to_positive_spin : bitToSpin false = 1 := by
  rfl

theorem empty_diagonal_energy (offset : Int) :
    diagonalIsingEnergy offset [] [] [] = offset := by
  simp [diagonalIsingEnergy, linearEnergy]

#eval diagonalIsingEnergy 2 [3] [bitToSpin true] []

end Noetheris
