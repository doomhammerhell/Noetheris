use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct WeightedTerm {
    pub name: String,
    pub weight: f64,
    pub value: f64,
}

impl WeightedTerm {
    pub fn contribution(&self) -> f64 {
        self.weight * self.value
    }
}
