---- MODULE consensus_safety ----
EXTENDS Naturals, FiniteSets

CONSTANTS Values

VARIABLES locked, committed, equivocated

Init ==
  /\ locked \in Values
  /\ committed = {}
  /\ equivocated = FALSE

Prepare(v) ==
  /\ v \in Values
  /\ committed = {}
  /\ locked' = v
  /\ committed' = committed
  /\ equivocated' = equivocated

Commit(v) ==
  /\ v \in Values
  /\ v = locked
  /\ locked' = locked
  /\ committed' = committed \cup {v}
  /\ equivocated' = equivocated

ByzantineEquivocation(v) ==
  /\ v \in Values
  /\ v # locked
  /\ locked' = locked
  /\ committed' = committed \cup {v}
  /\ equivocated' = TRUE

Next ==
  \/ \E v \in Values : Prepare(v)
  \/ \E v \in Values : Commit(v)
  \/ \E v \in Values : ByzantineEquivocation(v)

SingleCommitSafety ==
  Cardinality(committed) <= 1

Spec ==
  Init /\ [][Next]_<<locked, committed, equivocated>>

====
