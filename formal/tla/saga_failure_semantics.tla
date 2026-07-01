---- MODULE saga_failure_semantics ----
EXTENDS Naturals, FiniteSets

VARIABLES debit, credit, compensated, terminal

Init ==
  /\ debit = FALSE
  /\ credit = FALSE
  /\ compensated = FALSE
  /\ terminal = FALSE

Debit ==
  /\ debit' = TRUE
  /\ credit' = credit
  /\ compensated' = compensated
  /\ terminal' = terminal

Credit ==
  /\ debit
  /\ credit' = TRUE
  /\ debit' = debit
  /\ compensated' = compensated
  /\ terminal' = terminal

Compensate ==
  /\ debit
  /\ ~credit
  /\ compensated' = TRUE
  /\ debit' = debit
  /\ credit' = credit
  /\ terminal' = terminal

Finish ==
  /\ terminal' = TRUE
  /\ debit' = debit
  /\ credit' = credit
  /\ compensated' = compensated

Next ==
  \/ Debit
  \/ Credit
  \/ Compensate
  \/ Finish

ConsistentTerminal ==
  terminal => ((debit /\ credit /\ ~compensated) \/ (debit /\ ~credit /\ compensated) \/ (~debit /\ ~credit /\ ~compensated))

Spec ==
  Init /\ [][Next]_<<debit, credit, compensated, terminal>>

====
