namespace Noetheris

inductive NodeKind where
  | asset
  | state
  | actor
  | policy
  | quantumMode
deriving Repr, DecidableEq

structure StructuralNode where
  id : String
  kind : NodeKind
deriving Repr, DecidableEq

structure StructuralEdge where
  source : String
  target : String
deriving Repr, DecidableEq

def NodeIdsUnique (nodes : List StructuralNode) : Prop :=
  nodes.map (fun node => node.id) |>.Nodup

def EdgeEndpointsDeclared (nodes : List StructuralNode) (edge : StructuralEdge) : Prop :=
  edge.source ∈ nodes.map (fun node => node.id) ∧
  edge.target ∈ nodes.map (fun node => node.id)

theorem empty_nodes_unique : NodeIdsUnique [] := by
  simp [NodeIdsUnique]

end Noetheris
