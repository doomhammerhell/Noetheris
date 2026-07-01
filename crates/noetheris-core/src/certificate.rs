use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VerificationStatus {
    Verified,
    Rejected,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EnergyTerm {
    pub name: String,
    pub weight: f64,
    pub value: f64,
    pub contribution: f64,
}

impl EnergyTerm {
    pub fn new(name: impl Into<String>, weight: f64, value: f64) -> Self {
        let contribution = weight * value;
        Self {
            name: name.into(),
            weight,
            value,
            contribution,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CertificateConstraint {
    pub name: String,
    pub satisfied: bool,
    pub detail: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct VersionMetadata {
    pub project: String,
    pub version: String,
    pub schema: String,
}

impl Default for VersionMetadata {
    fn default() -> Self {
        Self {
            project: "noetheris".to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            schema: "energy-certificate-v1".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EnergyCertificate {
    pub problem_hash: String,
    pub algorithm_name: String,
    pub energy_model: Vec<EnergyTerm>,
    pub selected_variables: BTreeMap<String, bool>,
    pub satisfied_constraints: Vec<CertificateConstraint>,
    pub violated_constraints: Vec<CertificateConstraint>,
    pub total_energy: f64,
    pub verification_status: VerificationStatus,
    pub reproducibility_seed: u64,
    pub version: VersionMetadata,
}

impl EnergyCertificate {
    pub fn violated_constraints(&self) -> Vec<&CertificateConstraint> {
        self.violated_constraints.iter().collect()
    }

    pub fn satisfied_constraints(&self) -> Vec<&CertificateConstraint> {
        self.satisfied_constraints.iter().collect()
    }

    pub fn recomputed_energy(&self) -> f64 {
        self.energy_model.iter().map(|term| term.contribution).sum()
    }

    pub fn deterministic_status(&self, tolerance: f64) -> VerificationStatus {
        let energy_matches = (self.recomputed_energy() - self.total_energy).abs() <= tolerance;
        let satisfied_are_marked = self
            .satisfied_constraints
            .iter()
            .all(|constraint| constraint.satisfied);
        let violated_are_marked = self
            .violated_constraints
            .iter()
            .all(|constraint| !constraint.satisfied);
        if self.violated_constraints().is_empty()
            && satisfied_are_marked
            && violated_are_marked
            && energy_matches
            && self.total_energy.is_finite()
            && self.energy_model.iter().all(|term| {
                term.weight.is_finite()
                    && term.value.is_finite()
                    && term.contribution.is_finite()
                    && (term.weight * term.value - term.contribution).abs() <= tolerance
            })
        {
            VerificationStatus::Verified
        } else {
            VerificationStatus::Rejected
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn certificate_status_detects_energy_mismatch() {
        let certificate = EnergyCertificate {
            problem_hash: "sha256:00".to_string(),
            algorithm_name: "test".to_string(),
            energy_model: vec![EnergyTerm::new("risk", 2.0, 3.0)],
            selected_variables: BTreeMap::new(),
            satisfied_constraints: vec![CertificateConstraint {
                name: "graph_valid".to_string(),
                satisfied: true,
                detail: "graph accepted".to_string(),
            }],
            violated_constraints: vec![],
            total_energy: 7.0,
            verification_status: VerificationStatus::Rejected,
            reproducibility_seed: 7,
            version: VersionMetadata::default(),
        };
        assert_eq!(
            certificate.deterministic_status(1e-9),
            VerificationStatus::Rejected
        );
    }
}
