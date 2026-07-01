from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from noetheris.certificates import (
    CertificateConstraint,
    EnergyCertificate,
    EnergyTerm,
    make_certificate,
)
from noetheris.graph import StateGraph, Transition
from noetheris.qubo import QuboModel


@dataclass(frozen=True)
class InvariantWeights:
    validity: float = 50.0
    invariant: float = 40.0
    path: float = 1.0
    adversary: float = 3.0
    exactly_one_path: float = 100.0


@dataclass(frozen=True)
class CandidatePath:
    states: tuple[str, ...]
    transitions: tuple[Transition, ...]

    @property
    def path_cost(self) -> float:
        return sum(transition.cost for transition in self.transitions)

    @property
    def adversarial_steps(self) -> int:
        return sum(1 for transition in self.transitions if transition.adversarial)


@dataclass(frozen=True)
class InvariantAnnealingResult:
    path: tuple[str, ...]
    energy: float
    violation_found: bool
    qubo: QuboModel
    certificate: EnergyCertificate
    adversarial_steps: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": list(self.path),
            "energy": self.energy,
            "violation_found": self.violation_found,
            "adversarial_steps": self.adversarial_steps,
            "qubo": self.qubo.to_dict(),
            "certificate": self.certificate.to_dict(),
        }


def search_invariant_violation(
    graph: StateGraph,
    *,
    max_depth: int,
    weights: InvariantWeights = InvariantWeights(),
    adversarial_budget: int | None = None,
    seed: int = 0,
) -> InvariantAnnealingResult:
    graph.validate()
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    start = graph.initial_state or graph.states[0]
    candidates = _enumerate_paths(graph, start, max_depth)
    if not candidates:
        candidates = [CandidatePath(states=(start,), transitions=())]
    costs: dict[str, float] = {}
    path_by_variable: dict[str, CandidatePath] = {}
    terms_by_variable: dict[str, tuple[EnergyTerm, ...]] = {}
    for idx, candidate in enumerate(candidates):
        variable = f"path_{idx}"
        violation_found = graph.violates_invariant(candidate.states)
        validity_penalty = 0.0
        invariant_penalty = 0.0 if violation_found else 1.0
        path_cost = candidate.path_cost
        adversary_cost = float(candidate.adversarial_steps)
        if adversarial_budget is not None and candidate.adversarial_steps > adversarial_budget:
            validity_penalty += candidate.adversarial_steps - adversarial_budget
        energy_terms = (
            EnergyTerm("lambda_validity * P_validity", weights.validity, validity_penalty),
            EnergyTerm(
                "lambda_invariant * P_invariant",
                weights.invariant,
                invariant_penalty,
            ),
            EnergyTerm("lambda_path * C_path", weights.path, path_cost),
            EnergyTerm(
                "lambda_adversary * C_adversary",
                weights.adversary,
                adversary_cost,
            ),
        )
        costs[variable] = sum(term.contribution for term in energy_terms)
        path_by_variable[variable] = candidate
        terms_by_variable[variable] = energy_terms
    qubo = QuboModel.exactly_one_choice(costs, penalty=weights.exactly_one_path)
    solution = qubo.exhaustive_solve()
    selected_variable = min(
        variable for variable, enabled in solution.assignment.items() if enabled
    )
    selected_path = path_by_variable[selected_variable]
    energy_terms = terms_by_variable[selected_variable]
    violation_found = graph.violates_invariant(selected_path.states)
    satisfied_constraints = [
        CertificateConstraint("graph_valid", True, "state graph validation succeeded"),
        CertificateConstraint("path_valid", True, "selected path follows declared transitions"),
        CertificateConstraint(
            "exactly_one_path_selected",
            True,
            "QUBO solution selected one enumerated path variable",
        ),
    ]
    violated_constraints: list[CertificateConstraint] = []
    if not violation_found:
        violated_constraints.append(
            CertificateConstraint(
                "target_violation_found",
                False,
                "selected path does not reach a forbidden state or transition",
            )
        )
    else:
        satisfied_constraints.append(
            CertificateConstraint(
                "target_violation_found",
                True,
                "selected path reaches a declared forbidden condition",
            )
        )
    problem = {
        "graph": graph.to_dict(),
        "max_depth": max_depth,
        "weights": weights.__dict__,
        "adversarial_budget": adversarial_budget,
    }
    witness_assignment = {
        "selected_variable": selected_variable,
        "path": list(selected_path.states),
        "transitions": [transition.to_dict() for transition in selected_path.transitions],
        "adversarial_steps": selected_path.adversarial_steps,
        "violation_found": violation_found,
    }
    certificate = make_certificate(
        problem=problem,
        algorithm_name="invariant_annealing_search",
        energy_terms=energy_terms,
        selected_variables=solution.assignment,
        witness_assignment=witness_assignment,
        energy_breakdown={"selected_path_energy": sum(term.contribution for term in energy_terms)},
        proof_obligations=(
            "recompute_problem_hash",
            "recompute_selected_path_energy",
            "check_declared_path_transitions",
            "check_forbidden_condition_reached",
        ),
        satisfied_constraints=tuple(satisfied_constraints),
        violated_constraints=tuple(violated_constraints),
        reproducibility_seed=seed,
    )
    return InvariantAnnealingResult(
        path=selected_path.states,
        energy=sum(term.contribution for term in energy_terms),
        violation_found=violation_found,
        qubo=qubo,
        certificate=certificate,
        adversarial_steps=selected_path.adversarial_steps,
    )


def _enumerate_paths(graph: StateGraph, start: str, max_depth: int) -> list[CandidatePath]:
    results: list[CandidatePath] = []

    def walk(path: tuple[str, ...], transitions: tuple[Transition, ...], depth: int) -> None:
        results.append(CandidatePath(states=path, transitions=transitions))
        if depth == max_depth:
            return
        for transition in graph.outgoing(path[-1]):
            walk(
                path + (transition.target,),
                transitions + (transition,),
                depth + 1,
            )

    walk((start,), (), 0)
    return results
