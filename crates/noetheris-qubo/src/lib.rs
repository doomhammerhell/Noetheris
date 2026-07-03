use noetheris_core::{NoetherisError, Result};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BinaryVariable {
    pub name: String,
    pub description: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct QuadraticTerm {
    pub left: String,
    pub right: String,
    pub coefficient: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct QuboModel {
    pub variables: Vec<String>,
    #[serde(default)]
    pub linear: BTreeMap<String, f64>,
    #[serde(default)]
    pub quadratic: Vec<QuadraticTerm>,
    #[serde(default)]
    pub constant: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct QuboSolution {
    pub assignment: BTreeMap<String, bool>,
    pub energy: f64,
}

pub type Solution = QuboSolution;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PenaltyTerm {
    pub name: String,
    pub weight: f64,
    pub value: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ObjectiveTerm {
    pub name: String,
    pub weight: f64,
    pub value: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ConstraintEncoding {
    pub name: String,
    pub variables: Vec<String>,
    pub penalty_weight: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EnergyComponent {
    pub name: String,
    pub contribution: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EnergyBreakdown {
    pub total: f64,
    pub components: Vec<EnergyComponent>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CompiledProblem {
    pub problem_hash: String,
    pub model: QuboModel,
    pub variable_metadata: BTreeMap<String, String>,
    pub constraints: Vec<ConstraintEncoding>,
    pub objectives: Vec<ObjectiveTerm>,
}

pub struct ExactSolver {
    pub max_variables: usize,
}

impl Default for ExactSolver {
    fn default() -> Self {
        Self { max_variables: 24 }
    }
}

impl ExactSolver {
    pub fn solve(&self, model: &QuboModel) -> Result<QuboSolution> {
        if model.variables.len() > self.max_variables {
            return Err(NoetherisError::InvalidQubo(format!(
                "exact solver bound {} exceeded by {} variables",
                self.max_variables,
                model.variables.len()
            )));
        }
        model.exhaustive_solve()
    }
}

pub struct SimulatedAnnealingSolver {
    pub sweeps: usize,
    pub seed: u64,
}

impl SimulatedAnnealingSolver {
    pub fn solve(&self, model: &QuboModel) -> Result<QuboSolution> {
        model.validate()?;
        let mut rng = DeterministicRng::new(self.seed);
        let mut assignment = model
            .variables
            .iter()
            .map(|variable| (variable.clone(), rng.next_bool()))
            .collect::<BTreeMap<_, _>>();
        let mut current = model.evaluate(&assignment);
        let mut best = QuboSolution {
            assignment: assignment.clone(),
            energy: current,
        };
        for sweep in 0..self.sweeps.max(1) {
            let temperature = 1.0 / (1.0 + sweep as f64 / self.sweeps.max(1) as f64);
            for variable in &model.variables {
                let previous = *assignment.get(variable).unwrap_or(&false);
                assignment.insert(variable.clone(), !previous);
                let candidate = model.evaluate(&assignment);
                let delta = candidate - current;
                let accept = delta <= 0.0 || rng.next_unit() < (-delta / temperature).exp();
                if accept {
                    current = candidate;
                    if current < best.energy {
                        best = QuboSolution {
                            assignment: assignment.clone(),
                            energy: current,
                        };
                    }
                } else {
                    assignment.insert(variable.clone(), previous);
                }
            }
        }
        Ok(best)
    }
}

struct DeterministicRng {
    state: u64,
}

impl DeterministicRng {
    fn new(seed: u64) -> Self {
        Self {
            state: seed ^ 0x9E37_79B9_7F4A_7C15,
        }
    }

    fn next_u64(&mut self) -> u64 {
        self.state = self
            .state
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        self.state
    }

    fn next_bool(&mut self) -> bool {
        (self.next_u64() & 1) == 1
    }

    fn next_unit(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / ((1_u64 << 53) as f64)
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IsingCoupling {
    pub left: String,
    pub right: String,
    pub coefficient: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct HamiltonianTerm {
    pub operator: String,
    pub coefficient: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IsingModel {
    pub variables: Vec<String>,
    pub fields: BTreeMap<String, f64>,
    pub couplings: Vec<IsingCoupling>,
    pub offset: f64,
}

impl IsingModel {
    pub fn evaluate(&self, spins: &BTreeMap<String, i8>) -> Result<f64> {
        let mut energy = self.offset;
        for (variable, field) in &self.fields {
            let spin = spin_value(spins.get(variable).copied().unwrap_or(1), variable)?;
            energy += field * f64::from(spin);
        }
        for coupling in &self.couplings {
            let left = spin_value(
                spins.get(&coupling.left).copied().unwrap_or(1),
                &coupling.left,
            )?;
            let right = spin_value(
                spins.get(&coupling.right).copied().unwrap_or(1),
                &coupling.right,
            )?;
            energy += coupling.coefficient * f64::from(left) * f64::from(right);
        }
        Ok(energy)
    }

    pub fn hamiltonian_terms(&self) -> Vec<HamiltonianTerm> {
        let mut terms = vec![HamiltonianTerm {
            operator: "I".to_string(),
            coefficient: self.offset,
        }];
        for variable in &self.variables {
            let coefficient = *self.fields.get(variable).unwrap_or(&0.0);
            if coefficient != 0.0 {
                terms.push(HamiltonianTerm {
                    operator: format!("Z[{variable}]"),
                    coefficient,
                });
            }
        }
        for coupling in &self.couplings {
            if coupling.coefficient != 0.0 {
                terms.push(HamiltonianTerm {
                    operator: format!("Z[{}] Z[{}]", coupling.left, coupling.right),
                    coefficient: coupling.coefficient,
                });
            }
        }
        terms
    }
}

impl QuboModel {
    pub fn validate(&self) -> Result<()> {
        for variable in &self.variables {
            if variable.trim().is_empty() {
                return Err(NoetherisError::InvalidQubo(
                    "variable names must not be empty".to_string(),
                ));
            }
        }
        for (variable, coefficient) in &self.linear {
            if !self.variables.contains(variable) {
                return Err(NoetherisError::InvalidQubo(format!(
                    "linear term references unknown variable {variable}"
                )));
            }
            if !coefficient.is_finite() {
                return Err(NoetherisError::InvalidQubo(format!(
                    "linear coefficient for {variable} is not finite"
                )));
            }
        }
        for term in &self.quadratic {
            if !self.variables.contains(&term.left) || !self.variables.contains(&term.right) {
                return Err(NoetherisError::InvalidQubo(format!(
                    "quadratic term {} * {} references an unknown variable",
                    term.left, term.right
                )));
            }
            if !term.coefficient.is_finite() {
                return Err(NoetherisError::InvalidQubo(format!(
                    "quadratic coefficient for {} * {} is not finite",
                    term.left, term.right
                )));
            }
        }
        Ok(())
    }

    pub fn evaluate(&self, assignment: &BTreeMap<String, bool>) -> f64 {
        let mut energy = self.constant;
        for (variable, coefficient) in &self.linear {
            if *assignment.get(variable).unwrap_or(&false) {
                energy += coefficient;
            }
        }
        for term in &self.quadratic {
            if *assignment.get(&term.left).unwrap_or(&false)
                && *assignment.get(&term.right).unwrap_or(&false)
            {
                energy += term.coefficient;
            }
        }
        energy
    }

    pub fn energy_breakdown(&self, assignment: &BTreeMap<String, bool>) -> EnergyBreakdown {
        let mut components = vec![EnergyComponent {
            name: "constant".to_string(),
            contribution: self.constant,
        }];
        for (variable, coefficient) in &self.linear {
            if *assignment.get(variable).unwrap_or(&false) {
                components.push(EnergyComponent {
                    name: format!("linear:{variable}"),
                    contribution: *coefficient,
                });
            }
        }
        for term in &self.quadratic {
            if *assignment.get(&term.left).unwrap_or(&false)
                && *assignment.get(&term.right).unwrap_or(&false)
            {
                components.push(EnergyComponent {
                    name: format!("quadratic:{}:{}", term.left, term.right),
                    contribution: term.coefficient,
                });
            }
        }
        let total = components
            .iter()
            .map(|component| component.contribution)
            .sum();
        EnergyBreakdown { total, components }
    }

    pub fn to_ising(&self) -> Result<IsingModel> {
        self.validate()?;
        let mut fields = self
            .variables
            .iter()
            .map(|variable| (variable.clone(), 0.0))
            .collect::<BTreeMap<_, _>>();
        let mut offset = self.constant;
        let mut couplings = Vec::new();
        for (variable, coefficient) in &self.linear {
            offset += coefficient / 2.0;
            *fields.entry(variable.clone()).or_insert(0.0) -= coefficient / 2.0;
        }
        for term in &self.quadratic {
            offset += term.coefficient / 4.0;
            *fields.entry(term.left.clone()).or_insert(0.0) -= term.coefficient / 4.0;
            *fields.entry(term.right.clone()).or_insert(0.0) -= term.coefficient / 4.0;
            couplings.push(IsingCoupling {
                left: term.left.clone(),
                right: term.right.clone(),
                coefficient: term.coefficient / 4.0,
            });
        }
        Ok(IsingModel {
            variables: self.variables.clone(),
            fields,
            couplings,
            offset,
        })
    }

    pub fn assignment_to_spins(&self, assignment: &BTreeMap<String, bool>) -> BTreeMap<String, i8> {
        self.variables
            .iter()
            .map(|variable| {
                (
                    variable.clone(),
                    if *assignment.get(variable).unwrap_or(&false) {
                        -1
                    } else {
                        1
                    },
                )
            })
            .collect()
    }

    pub fn exhaustive_solve(&self) -> Result<QuboSolution> {
        self.validate()?;
        let n = self.variables.len();
        if n > 24 {
            return Err(NoetherisError::InvalidQubo(
                "local exhaustive QUBO solver is bounded to 24 variables".to_string(),
            ));
        }
        let limit = 1_u64 << n;
        let mut best: Option<QuboSolution> = None;
        for mask in 0..limit {
            let assignment = self
                .variables
                .iter()
                .enumerate()
                .map(|(idx, variable)| (variable.clone(), ((mask >> idx) & 1) == 1))
                .collect::<BTreeMap<_, _>>();
            let energy = self.evaluate(&assignment);
            match &best {
                Some(current) if current.energy <= energy => {}
                _ => best = Some(QuboSolution { assignment, energy }),
            }
        }
        best.ok_or_else(|| NoetherisError::InvalidQubo("empty search space".to_string()))
    }
}

fn spin_value(value: i8, variable: &str) -> Result<i8> {
    if value == -1 || value == 1 {
        Ok(value)
    } else {
        Err(NoetherisError::InvalidQubo(format!(
            "spin for {variable} must be -1 or +1"
        )))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exhaustive_solver_finds_minimum() {
        let model = QuboModel {
            variables: vec!["x".to_string(), "y".to_string()],
            linear: BTreeMap::from([("x".to_string(), -2.0), ("y".to_string(), 1.0)]),
            quadratic: vec![QuadraticTerm {
                left: "x".to_string(),
                right: "y".to_string(),
                coefficient: 5.0,
            }],
            constant: 0.0,
        };
        let solution = model.exhaustive_solve().unwrap();
        assert!(solution.assignment["x"]);
        assert!(!solution.assignment["y"]);
        assert_eq!(solution.energy, -2.0);
    }

    #[test]
    fn ising_conversion_preserves_energy() {
        let model = QuboModel {
            variables: vec!["x".to_string(), "y".to_string()],
            linear: BTreeMap::from([("x".to_string(), -2.0), ("y".to_string(), 1.0)]),
            quadratic: vec![QuadraticTerm {
                left: "x".to_string(),
                right: "y".to_string(),
                coefficient: 5.0,
            }],
            constant: 0.5,
        };
        let ising = model.to_ising().unwrap();
        for x in [false, true] {
            for y in [false, true] {
                let assignment = BTreeMap::from([("x".to_string(), x), ("y".to_string(), y)]);
                let spins = model.assignment_to_spins(&assignment);
                let qubo_energy = model.evaluate(&assignment);
                let ising_energy = ising.evaluate(&spins).unwrap();
                assert!((qubo_energy - ising_energy).abs() < 1e-9);
            }
        }
        assert!(!ising.hamiltonian_terms().is_empty());
    }

    #[test]
    fn simulated_annealing_is_deterministic() {
        let model = QuboModel {
            variables: vec!["x".to_string(), "y".to_string()],
            linear: BTreeMap::from([("x".to_string(), -1.0), ("y".to_string(), 2.0)]),
            quadratic: vec![],
            constant: 0.0,
        };
        let solver = SimulatedAnnealingSolver {
            sweeps: 16,
            seed: 1337,
        };
        let first = solver.solve(&model).unwrap();
        let second = solver.solve(&model).unwrap();
        assert_eq!(first, second);
    }

    #[test]
    fn structural_validation_allows_large_export_models() {
        let model = QuboModel {
            variables: (0..25).map(|idx| format!("x{idx}")).collect(),
            linear: BTreeMap::new(),
            quadratic: vec![],
            constant: 0.0,
        };
        assert!(model.validate().is_ok());
        assert!(model.exhaustive_solve().is_err());
    }
}
