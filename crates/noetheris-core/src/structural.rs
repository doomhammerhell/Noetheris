use crate::{stable_problem_hash, NoetherisError, Result};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum NodeKind {
    Asset,
    State,
    Actor,
    Policy,
    QuantumMode,
    Constraint,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EdgeKind {
    Transition,
    Dependency,
    Approval,
    Custody,
    Message,
    Coupling,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RiskAnnotation {
    pub category: String,
    pub weight: f64,
    #[serde(default)]
    pub harvest_now_decrypt_later: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CryptoAsset {
    pub algorithm: String,
    #[serde(default)]
    pub key_lifetime_days: u64,
    #[serde(default)]
    pub compliance_required: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MigrationCandidate {
    pub candidate_id: String,
    pub target_algorithm: String,
    pub migration_cost: f64,
    pub downtime: f64,
    pub risk_reduction: f64,
    #[serde(default)]
    pub hybrid: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StructuralNode {
    pub id: String,
    pub kind: NodeKind,
    pub label: String,
    #[serde(default)]
    pub risk: Option<RiskAnnotation>,
    #[serde(default)]
    pub crypto: Option<CryptoAsset>,
    #[serde(default)]
    pub migration_candidates: Vec<MigrationCandidate>,
    #[serde(default)]
    pub annotations: BTreeMap<String, String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StructuralEdge {
    pub id: String,
    pub source: String,
    pub target: String,
    pub kind: EdgeKind,
    #[serde(default)]
    pub cost: f64,
    #[serde(default)]
    pub adversarial: bool,
    #[serde(default)]
    pub annotations: BTreeMap<String, String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConstraintKind {
    ForbiddenState,
    ForbiddenTransition,
    DependencyRequired,
    CardinalityAtLeast,
    CardinalityAtMost,
    Equality,
    Implication,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Constraint {
    pub id: String,
    pub kind: ConstraintKind,
    pub expression: String,
    pub weight: f64,
    #[serde(default)]
    pub nodes: Vec<String>,
    #[serde(default)]
    pub edges: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Objective {
    pub id: String,
    pub expression: String,
    pub weight: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct InvariantPredicate {
    pub id: String,
    pub expression: String,
    pub weight: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AdversaryAction {
    pub id: String,
    pub label: String,
    pub budget_cost: f64,
    #[serde(default)]
    pub edge_ids: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct WitnessAssignment {
    pub variables: BTreeMap<String, bool>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StructuralSystem {
    pub system_id: String,
    pub version: String,
    pub problem_type: String,
    pub nodes: Vec<StructuralNode>,
    pub edges: Vec<StructuralEdge>,
    #[serde(default)]
    pub constraints: Vec<Constraint>,
    #[serde(default)]
    pub invariants: Vec<InvariantPredicate>,
    #[serde(default)]
    pub objectives: Vec<Objective>,
    #[serde(default)]
    pub adversary_actions: Vec<AdversaryAction>,
    #[serde(default)]
    pub metadata: BTreeMap<String, String>,
}

impl StructuralSystem {
    pub fn validate(&self) -> Result<()> {
        if self.system_id.trim().is_empty() {
            return Err(NoetherisError::InvalidGraph(
                "structural system id must not be empty".to_string(),
            ));
        }
        let mut node_ids = BTreeSet::new();
        for node in &self.nodes {
            if node.id.trim().is_empty() {
                return Err(NoetherisError::InvalidGraph(
                    "structural node id must not be empty".to_string(),
                ));
            }
            if !node_ids.insert(node.id.as_str()) {
                return Err(NoetherisError::InvalidGraph(format!(
                    "duplicate structural node {}",
                    node.id
                )));
            }
            if let Some(risk) = &node.risk {
                if !risk.weight.is_finite() || risk.weight < 0.0 {
                    return Err(NoetherisError::InvalidGraph(format!(
                        "node {} has invalid risk weight",
                        node.id
                    )));
                }
            }
            for candidate in &node.migration_candidates {
                if !candidate.migration_cost.is_finite()
                    || !candidate.downtime.is_finite()
                    || !(0.0..=1.0).contains(&candidate.risk_reduction)
                {
                    return Err(NoetherisError::InvalidGraph(format!(
                        "node {} has invalid migration candidate {}",
                        node.id, candidate.candidate_id
                    )));
                }
            }
        }
        let mut edge_ids = BTreeSet::new();
        for edge in &self.edges {
            if edge.id.trim().is_empty() {
                return Err(NoetherisError::InvalidGraph(
                    "structural edge id must not be empty".to_string(),
                ));
            }
            if !edge_ids.insert(edge.id.as_str()) {
                return Err(NoetherisError::InvalidGraph(format!(
                    "duplicate structural edge {}",
                    edge.id
                )));
            }
            if !node_ids.contains(edge.source.as_str()) || !node_ids.contains(edge.target.as_str())
            {
                return Err(NoetherisError::InvalidGraph(format!(
                    "edge {} references an unknown endpoint",
                    edge.id
                )));
            }
            if !edge.cost.is_finite() || edge.cost < 0.0 {
                return Err(NoetherisError::InvalidGraph(format!(
                    "edge {} has invalid cost",
                    edge.id
                )));
            }
        }
        for constraint in &self.constraints {
            if !constraint.weight.is_finite() || constraint.weight < 0.0 {
                return Err(NoetherisError::InvalidGraph(format!(
                    "constraint {} has invalid weight",
                    constraint.id
                )));
            }
            for node in &constraint.nodes {
                if !node_ids.contains(node.as_str()) {
                    return Err(NoetherisError::InvalidGraph(format!(
                        "constraint {} references unknown node {}",
                        constraint.id, node
                    )));
                }
            }
            for edge in &constraint.edges {
                if !edge_ids.contains(edge.as_str()) {
                    return Err(NoetherisError::InvalidGraph(format!(
                        "constraint {} references unknown edge {}",
                        constraint.id, edge
                    )));
                }
            }
        }
        for invariant in &self.invariants {
            if !invariant.weight.is_finite() || invariant.weight < 0.0 {
                return Err(NoetherisError::InvalidGraph(format!(
                    "invariant {} has invalid weight",
                    invariant.id
                )));
            }
        }
        for objective in &self.objectives {
            if !objective.weight.is_finite() {
                return Err(NoetherisError::InvalidGraph(format!(
                    "objective {} has invalid weight",
                    objective.id
                )));
            }
        }
        for action in &self.adversary_actions {
            if !action.budget_cost.is_finite() || action.budget_cost < 0.0 {
                return Err(NoetherisError::InvalidGraph(format!(
                    "adversary action {} has invalid budget cost",
                    action.id
                )));
            }
            for edge in &action.edge_ids {
                if !edge_ids.contains(edge.as_str()) {
                    return Err(NoetherisError::InvalidGraph(format!(
                        "adversary action {} references unknown edge {}",
                        action.id, edge
                    )));
                }
            }
        }
        Ok(())
    }

    pub fn canonical_hash(&self) -> Result<String> {
        self.validate()?;
        stable_problem_hash(self)
    }
}

pub type TransitionSystem = StructuralSystem;
pub type DependencyGraph = StructuralSystem;
pub type CanonicalHash = String;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_and_hashes_structural_system() {
        let system = StructuralSystem {
            system_id: "unit".to_string(),
            version: "0.1.0".to_string(),
            problem_type: "invariant".to_string(),
            nodes: vec![
                StructuralNode {
                    id: "a".to_string(),
                    kind: NodeKind::State,
                    label: "A".to_string(),
                    risk: None,
                    crypto: None,
                    migration_candidates: vec![],
                    annotations: BTreeMap::new(),
                },
                StructuralNode {
                    id: "b".to_string(),
                    kind: NodeKind::State,
                    label: "B".to_string(),
                    risk: None,
                    crypto: None,
                    migration_candidates: vec![],
                    annotations: BTreeMap::new(),
                },
            ],
            edges: vec![StructuralEdge {
                id: "e".to_string(),
                source: "a".to_string(),
                target: "b".to_string(),
                kind: EdgeKind::Transition,
                cost: 1.0,
                adversarial: false,
                annotations: BTreeMap::new(),
            }],
            constraints: vec![],
            invariants: vec![],
            objectives: vec![],
            adversary_actions: vec![],
            metadata: BTreeMap::new(),
        };
        assert!(system.validate().is_ok());
        assert!(system.canonical_hash().unwrap().starts_with("sha256:"));
    }
}
