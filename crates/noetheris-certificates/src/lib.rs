use noetheris_core::{EnergyCertificate, Result, VerificationStatus};

#[derive(Debug, Clone, PartialEq)]
pub struct CertificateValidation {
    pub status: VerificationStatus,
    pub reasons: Vec<String>,
}

pub fn validate_certificate(
    certificate: &EnergyCertificate,
    expected_problem_hash: Option<&str>,
) -> Result<CertificateValidation> {
    let mut reasons = Vec::new();
    if let Some(expected) = expected_problem_hash {
        if certificate.problem_hash != expected {
            reasons.push("problem hash mismatch".to_string());
        }
    }
    for constraint in certificate.satisfied_constraints() {
        if !constraint.satisfied {
            reasons.push(format!(
                "satisfied constraint {} is not marked satisfied",
                constraint.name
            ));
        }
    }
    for constraint in certificate.violated_constraints() {
        if constraint.satisfied {
            reasons.push(format!(
                "violated constraint {} is marked satisfied",
                constraint.name
            ));
        }
        reasons.push(format!("constraint {} is violated", constraint.name));
    }
    let recomputed = certificate.recomputed_energy();
    if (recomputed - certificate.total_energy).abs() > 1e-9 {
        reasons.push("total energy does not match energy terms".to_string());
    }
    for term in &certificate.energy_model {
        if (term.weight * term.value - term.contribution).abs() > 1e-9 {
            reasons.push(format!(
                "energy term {} has inconsistent contribution",
                term.name
            ));
        }
    }
    if !certificate.total_energy.is_finite() {
        reasons.push("total energy is not finite".to_string());
    }
    let mut status = if reasons.is_empty() {
        VerificationStatus::Verified
    } else {
        VerificationStatus::Rejected
    };
    if certificate.verification_status != status {
        reasons.push("declared verification status is inconsistent".to_string());
        status = VerificationStatus::Rejected;
    }
    let _ = certificate.deterministic_status(1e-9);
    Ok(CertificateValidation { status, reasons })
}

#[cfg(test)]
mod tests {
    use super::*;
    use noetheris_core::{CertificateConstraint, EnergyTerm, VersionMetadata};
    use std::collections::BTreeMap;

    #[test]
    fn validates_correct_certificate() {
        let certificate = EnergyCertificate {
            problem_hash: "sha256:abc".to_string(),
            algorithm_name: "unit".to_string(),
            energy_model: vec![EnergyTerm::new("path", 1.0, 2.0)],
            selected_variables: BTreeMap::new(),
            satisfied_constraints: vec![CertificateConstraint {
                name: "validity".to_string(),
                satisfied: true,
                detail: "accepted".to_string(),
            }],
            violated_constraints: vec![],
            total_energy: 2.0,
            verification_status: VerificationStatus::Verified,
            reproducibility_seed: 1,
            version: VersionMetadata::default(),
        };
        let validation = validate_certificate(&certificate, Some("sha256:abc")).unwrap();
        assert_eq!(validation.status, VerificationStatus::Verified);
    }

    #[test]
    fn rejects_constraint_violation() {
        let certificate = EnergyCertificate {
            problem_hash: "sha256:abc".to_string(),
            algorithm_name: "unit".to_string(),
            energy_model: vec![EnergyTerm::new("path", 1.0, 2.0)],
            selected_variables: BTreeMap::new(),
            satisfied_constraints: vec![],
            violated_constraints: vec![CertificateConstraint {
                name: "validity".to_string(),
                satisfied: false,
                detail: "rejected".to_string(),
            }],
            total_energy: 2.0,
            verification_status: VerificationStatus::Rejected,
            reproducibility_seed: 1,
            version: VersionMetadata::default(),
        };
        let validation = validate_certificate(&certificate, Some("sha256:abc")).unwrap();
        assert_eq!(validation.status, VerificationStatus::Rejected);
    }
}
