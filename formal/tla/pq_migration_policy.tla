---- MODULE pq_migration_policy ----
EXTENDS FiniteSets

CONSTANTS Assets, Dependencies, ComplianceAssets

VARIABLES migrated

Init ==
  migrated = {}

CanMigrate(asset) ==
  /\ asset \in Assets
  /\ \A dep \in Dependencies :
        dep[1] = asset => dep[2] \in migrated

Migrate(asset) ==
  /\ CanMigrate(asset)
  /\ migrated' = migrated \cup {asset}

Next ==
  \E asset \in Assets : Migrate(asset)

DependenciesRespected ==
  \A dep \in Dependencies :
    dep[1] \in migrated => dep[2] \in migrated

ComplianceSatisfied ==
  ComplianceAssets \subseteq migrated

Spec ==
  Init /\ [][Next]_migrated

====
