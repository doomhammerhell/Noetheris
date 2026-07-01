# PQC Migration Optimizer

The migration optimizer treats post-quantum migration as constrained graph optimization. Assets carry algorithm inventory, data lifetime, risk, compliance, and migration candidates. Edges represent dependencies such as KMS/HSM custody, certificate chain order, service mesh identity, and signing-key custody.

The energy surface is:

```text
E(x) =
  lambda_risk       R_residual(x)
+ lambda_hndl       H_harvest_exposure(x)
+ lambda_cost       C_migration(x)
+ lambda_downtime   D_operational(x)
+ lambda_incompat   I_incompatibility(x)
+ lambda_dependency P_dependency(x)
+ lambda_compliance G_compliance(x)
+ lambda_downgrade  P_downgrade(x)
```

Noetheris emits selected migration steps, residual risk, dependency blockers, QUBO energy, and certificates. Risk scoring is input-relative and must be reviewed by security owners.
