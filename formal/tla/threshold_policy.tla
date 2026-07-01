---- MODULE threshold_policy ----
EXTENDS Naturals, FiniteSets

CONSTANTS Signers, Threshold

VARIABLES approved, whitelisted, insideWindow, authorized

Init ==
  /\ approved = {}
  /\ whitelisted = FALSE
  /\ insideWindow = FALSE
  /\ authorized = FALSE

Approve(signer) ==
  /\ signer \in Signers
  /\ approved' = approved \cup {signer}
  /\ whitelisted' = whitelisted
  /\ insideWindow' = insideWindow
  /\ authorized' = authorized

SetWhitelist ==
  /\ whitelisted' = TRUE
  /\ approved' = approved
  /\ insideWindow' = insideWindow
  /\ authorized' = authorized

SetWindow ==
  /\ insideWindow' = TRUE
  /\ approved' = approved
  /\ whitelisted' = whitelisted
  /\ authorized' = authorized

Authorize ==
  /\ Cardinality(approved) >= Threshold
  /\ whitelisted
  /\ insideWindow
  /\ authorized' = TRUE
  /\ approved' = approved
  /\ whitelisted' = whitelisted
  /\ insideWindow' = insideWindow

Next ==
  \/ \E signer \in Signers : Approve(signer)
  \/ SetWhitelist
  \/ SetWindow
  \/ Authorize

Safety ==
  authorized => /\ Cardinality(approved) >= Threshold
                /\ whitelisted
                /\ insideWindow

Spec ==
  Init /\ [][Next]_<<approved, whitelisted, insideWindow, authorized>>

====
