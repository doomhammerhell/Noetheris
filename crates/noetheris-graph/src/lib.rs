use noetheris_core::{NoetherisError, Result};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::path::Path;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Transition {
    pub from: String,
    pub to: String,
    pub cost: f64,
    #[serde(default)]
    pub adversarial: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StateGraph {
    pub states: Vec<String>,
    pub transitions: Vec<Transition>,
    #[serde(default)]
    pub forbidden_states: Vec<String>,
    #[serde(default)]
    pub forbidden_transitions: Vec<[String; 2]>,
    #[serde(default)]
    pub initial_state: Option<String>,
}

impl StateGraph {
    pub fn from_json_file(path: impl AsRef<Path>) -> Result<Self> {
        let file = File::open(path)?;
        let graph = serde_json::from_reader(file)?;
        Ok(graph)
    }

    pub fn validate(&self) -> Result<()> {
        if self.states.is_empty() {
            return Err(NoetherisError::InvalidGraph(
                "state set must not be empty".to_string(),
            ));
        }
        let mut seen = BTreeSet::new();
        for state in &self.states {
            if state.trim().is_empty() {
                return Err(NoetherisError::InvalidGraph(
                    "state names must not be empty".to_string(),
                ));
            }
            if !seen.insert(state) {
                return Err(NoetherisError::InvalidGraph(format!(
                    "duplicate state {state}"
                )));
            }
        }
        for transition in &self.transitions {
            if !seen.contains(&transition.from) || !seen.contains(&transition.to) {
                return Err(NoetherisError::InvalidGraph(format!(
                    "transition {} -> {} references an unknown state",
                    transition.from, transition.to
                )));
            }
            if !transition.cost.is_finite() || transition.cost < 0.0 {
                return Err(NoetherisError::InvalidGraph(format!(
                    "transition {} -> {} has invalid cost",
                    transition.from, transition.to
                )));
            }
        }
        for state in &self.forbidden_states {
            if !seen.contains(state) {
                return Err(NoetherisError::InvalidGraph(format!(
                    "forbidden state {state} is not declared"
                )));
            }
        }
        if let Some(initial) = &self.initial_state {
            if !seen.contains(initial) {
                return Err(NoetherisError::InvalidGraph(format!(
                    "initial state {initial} is not declared"
                )));
            }
        }
        Ok(())
    }

    pub fn outgoing_by_state(&self) -> BTreeMap<&str, Vec<&Transition>> {
        let mut out: BTreeMap<&str, Vec<&Transition>> = BTreeMap::new();
        for transition in &self.transitions {
            out.entry(&transition.from).or_default().push(transition);
        }
        out
    }

    pub fn is_forbidden_transition(&self, from: &str, to: &str) -> bool {
        self.forbidden_transitions
            .iter()
            .any(|pair| pair[0] == from && pair[1] == to)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_valid_graph() {
        let graph = StateGraph {
            states: vec!["a".to_string(), "b".to_string()],
            transitions: vec![Transition {
                from: "a".to_string(),
                to: "b".to_string(),
                cost: 1.0,
                adversarial: false,
            }],
            forbidden_states: vec!["b".to_string()],
            forbidden_transitions: vec![],
            initial_state: Some("a".to_string()),
        };
        assert!(graph.validate().is_ok());
    }

    #[test]
    fn rejects_unknown_transition_endpoint() {
        let graph = StateGraph {
            states: vec!["a".to_string()],
            transitions: vec![Transition {
                from: "a".to_string(),
                to: "z".to_string(),
                cost: 1.0,
                adversarial: false,
            }],
            forbidden_states: vec![],
            forbidden_transitions: vec![],
            initial_state: None,
        };
        assert!(graph.validate().is_err());
    }
}
