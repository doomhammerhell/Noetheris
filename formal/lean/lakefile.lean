import Lake
open Lake DSL

package «noetheris» where
  version := v!"0.1.0"

@[default_target]
lean_lib Noetheris where
  roots := #[`Noetheris]
