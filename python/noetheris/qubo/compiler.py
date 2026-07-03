from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any, Mapping

from noetheris.certificates import stable_problem_hash
from noetheris.ir import StructuralSystem
from noetheris.qubo.model import QuadraticTerm, QuboModel, QuboSolution


@dataclass(frozen=True)
class EnergyComponent:
    name: str
    contribution: float


@dataclass(frozen=True)
class EnergyBreakdown:
    total: float
    components: tuple[EnergyComponent, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "components": [
                {"name": item.name, "contribution": item.contribution}
                for item in self.components
            ],
        }


@dataclass(frozen=True)
class CompiledProblem:
    problem_type: str
    problem_hash: str
    compiled_model_hash: str
    model: QuboModel
    variable_metadata: Mapping[str, str]
    constraints: tuple[str, ...] = ()
    objective_components: tuple[str, ...] = ()
    reverse_map: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_type": self.problem_type,
            "problem_hash": self.problem_hash,
            "compiled_model_hash": self.compiled_model_hash,
            "model": self.model.to_dict(),
            "variable_metadata": dict(sorted(self.variable_metadata.items())),
            "constraints": list(self.constraints),
            "objective_components": list(self.objective_components),
            "reverse_map": _jsonable(self.reverse_map),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CompiledProblem":
        model_value = value["model"]
        model = QuboModel(
            variables=[str(item) for item in model_value["variables"]],
            linear={str(k): float(v) for k, v in model_value.get("linear", {}).items()},
            quadratic=tuple(
                QuadraticTerm(
                    left=str(item["left"]),
                    right=str(item["right"]),
                    coefficient=float(item["coefficient"]),
                )
                for item in model_value.get("quadratic", ())
            ),
            constant=float(model_value.get("constant", 0.0)),
        )
        return cls(
            problem_type=str(value["problem_type"]),
            problem_hash=str(value["problem_hash"]),
            compiled_model_hash=str(value["compiled_model_hash"]),
            model=model,
            variable_metadata={
                str(k): str(v) for k, v in value.get("variable_metadata", {}).items()
            },
            constraints=tuple(str(item) for item in value.get("constraints", ())),
            objective_components=tuple(
                str(item) for item in value.get("objective_components", ())
            ),
            reverse_map=value.get("reverse_map", {}),
        )


def compile_invariant_search_to_qubo(
    system: StructuralSystem, *, max_depth: int | None = None
) -> CompiledProblem:
    system.validate()
    depth = max_depth or int(system.metadata.get("max_depth", "3"))
    initial = _initial_state(system)
    forbidden = {
        node
        for invariant in system.invariants
        if invariant.kind == "forbidden_state"
        for node in invariant.nodes
    }
    paths = _enumerate_structural_paths(system, initial, depth)
    variable_costs: dict[str, float] = {}
    reverse_map: dict[str, Any] = {}
    metadata: dict[str, str] = {}
    target_weight = sum(item.weight for item in system.invariants) or 100.0
    for idx, path in enumerate(paths):
        variable = f"path_{idx}"
        edge_ids = path["edges"]
        states = path["states"]
        cost = sum(_edge_by_id(system, edge).cost for edge in edge_ids)
        adversarial = sum(1 for edge in edge_ids if _edge_by_id(system, edge).adversarial)
        violation = any(state in forbidden for state in states)
        energy = cost + 3.0 * adversarial + (0.0 if violation else target_weight)
        variable_costs[variable] = energy
        reverse_map[variable] = path
        metadata[variable] = f"bounded path {' -> '.join(states)}"
    model = QuboModel.exactly_one_choice(variable_costs, penalty=100.0)
    return _compiled(system, "invariant", model, metadata, reverse_map)


def compile_pqc_migration_to_qubo(system: StructuralSystem) -> CompiledProblem:
    system.validate()
    variables: list[str] = []
    linear: dict[str, float] = {}
    quadratic: list[QuadraticTerm] = []
    metadata: dict[str, str] = {}
    reverse_map: dict[str, Any] = {}
    candidate_asset: dict[str, str] = {}
    for node in system.nodes:
        if node.kind != "asset":
            continue
        risk = node.risk.weight if node.risk else 0.0
        hndl = 1.25 if node.risk and node.risk.harvest_now_decrypt_later else 1.0
        for candidate in node.migration_candidates:
            variable = candidate.candidate_id
            variables.append(variable)
            candidate_asset[variable] = node.node_id
            risk_delta = -10.0 * risk * hndl * candidate.risk_reduction
            cost = candidate.migration_cost + 1.5 * candidate.downtime
            compliance = -80.0 if node.crypto and node.crypto.compliance_required and candidate.compliance_satisfies else 0.0
            linear[variable] = risk_delta + cost + compliance
            metadata[variable] = f"migrate {node.node_id} to {candidate.target_algorithm}"
            reverse_map[variable] = {"asset": node.node_id, "candidate": candidate.to_dict()}
    by_asset: dict[str, list[str]] = {}
    for variable, asset in candidate_asset.items():
        by_asset.setdefault(asset, []).append(variable)
    for candidates in by_asset.values():
        for idx, left in enumerate(candidates):
            for right in candidates[idx + 1:]:
                quadratic.append(QuadraticTerm(left, right, 500.0))
    for edge in system.edges:
        if edge.kind != "dependency":
            continue
        source_candidates = by_asset.get(edge.source, ())
        target_candidates = by_asset.get(edge.target, ())
        for source in source_candidates:
            linear[source] = linear.get(source, 0.0) + 90.0
            for target in target_candidates:
                quadratic.append(QuadraticTerm(source, target, -90.0))
    constant = sum(
        10.0
        * (node.risk.weight if node.risk else 0.0)
        * (1.25 if node.risk and node.risk.harvest_now_decrypt_later else 1.0)
        for node in system.nodes
        if node.kind == "asset"
    )
    model = QuboModel(variables=variables, linear=linear, quadratic=quadratic, constant=constant)
    return _compiled(system, "migration", model, metadata, reverse_map)


def compile_threshold_policy_to_qubo(system: StructuralSystem) -> CompiledProblem:
    system.validate()
    approvers = [node.node_id for node in system.nodes if node.kind == "actor"]
    variables = sorted(approvers + ["whitelist", "time_window"])
    linear = {variable: 1.0 for variable in variables}
    quadratic: list[QuadraticTerm] = []
    threshold = int(system.metadata.get("threshold", "2"))
    penalty = 80.0
    # Penalize selecting fewer than the required approvals through a bounded pair form.
    for approver in approvers:
        linear[approver] -= penalty / max(1, threshold)
    for idx, left in enumerate(approvers):
        for right in approvers[idx + 1:]:
            quadratic.append(QuadraticTerm(left, right, -penalty / max(1, threshold)))
    linear["whitelist"] -= 70.0
    linear["time_window"] -= 50.0
    model = QuboModel(variables=variables, linear=linear, quadratic=quadratic, constant=penalty + 120.0)
    metadata = {variable: f"policy witness variable {variable}" for variable in variables}
    reverse_map = {variable: {"kind": "policy_variable"} for variable in variables}
    return _compiled(system, "threshold", model, metadata, reverse_map)


def solve_exact(compiled: CompiledProblem, *, max_variables: int = 24) -> QuboSolution:
    if len(compiled.model.variables) > max_variables:
        raise ValueError("exact solver variable bound exceeded")
    return compiled.model.exhaustive_solve()


def solve_simulated_annealing(
    compiled: CompiledProblem, *, seed: int = 1337, sweeps: int = 128
) -> QuboSolution:
    compiled.model.validate()
    rng = random.Random(seed)
    assignment = {variable: bool(rng.getrandbits(1)) for variable in compiled.model.variables}
    current = compiled.model.evaluate(assignment)
    best = QuboSolution(dict(assignment), current)
    for sweep in range(max(1, sweeps)):
        temperature = 1.0 / (1.0 + sweep / max(1, sweeps))
        for variable in compiled.model.variables:
            previous = assignment[variable]
            assignment[variable] = not previous
            candidate = compiled.model.evaluate(assignment)
            delta = candidate - current
            accept = delta <= 0.0 or rng.random() < math.exp(-delta / max(temperature, 1e-12))
            if accept:
                current = candidate
                if current < best.energy:
                    best = QuboSolution(dict(assignment), current)
            else:
                assignment[variable] = previous
    return best


def evaluate_energy(compiled: CompiledProblem, assignment: Mapping[str, bool]) -> float:
    missing = [variable for variable in compiled.model.variables if variable not in assignment]
    if missing:
        raise ValueError(f"assignment missing variables: {', '.join(missing)}")
    return compiled.model.evaluate(assignment)


def energy_breakdown(compiled: CompiledProblem, assignment: Mapping[str, bool]) -> EnergyBreakdown:
    components = [EnergyComponent("constant", compiled.model.constant)]
    for variable, coefficient in sorted(compiled.model.linear.items()):
        if assignment.get(variable, False):
            components.append(EnergyComponent(f"linear:{variable}", coefficient))
    for term in compiled.model.quadratic:
        if assignment.get(term.left, False) and assignment.get(term.right, False):
            components.append(
                EnergyComponent(f"quadratic:{term.left}:{term.right}", term.coefficient)
            )
    total = sum(item.contribution for item in components)
    return EnergyBreakdown(total, tuple(components))


def explain_solution(compiled: CompiledProblem, solution: QuboSolution) -> dict[str, Any]:
    selected = {
        variable: compiled.reverse_map.get(variable, {})
        for variable, enabled in solution.assignment.items()
        if enabled
    }
    return {
        "problem_type": compiled.problem_type,
        "energy": solution.energy,
        "selected": _jsonable(selected),
        "energy_breakdown": energy_breakdown(compiled, solution.assignment).to_dict(),
    }


def replay_external_solution(
    compiled: CompiledProblem,
    assignment: Mapping[str, bool | int],
    *,
    reported_energy: float | None = None,
    problem_hash: str | None = None,
    compiled_model_hash: str | None = None,
    solver_metadata: Mapping[str, Any] | None = None,
    embedding_metadata: Mapping[str, Any] | None = None,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    reasons: list[str] = []
    if problem_hash is not None and problem_hash != compiled.problem_hash:
        reasons.append("problem hash mismatch")
    if compiled_model_hash is not None and compiled_model_hash != compiled.compiled_model_hash:
        reasons.append("compiled model hash mismatch")
    try:
        normalized_assignment = {
            name: bool(value) for name, value in assignment.items()
        }
        energy = compiled.model.evaluate(normalized_assignment)
    except ValueError as exc:
        return {
            "status": "rejected",
            "reasons": [str(exc)],
            "solver_metadata": _jsonable(dict(solver_metadata or {})),
            "embedding_metadata": _jsonable(dict(embedding_metadata or {})),
        }
    if reported_energy is not None and abs(float(reported_energy) - energy) > tolerance:
        reasons.append("reported energy mismatch")
    status = "verified" if not reasons else "rejected"
    return {
        "status": status,
        "reasons": reasons,
        "problem_hash": compiled.problem_hash,
        "compiled_model_hash": compiled.compiled_model_hash,
        "assignment": {
            variable: normalized_assignment[variable]
            for variable in compiled.model.variables
        },
        "energy": energy,
        "reported_energy": reported_energy,
        "energy_recomputed": status == "verified",
        "solver_boundary": "external solver output is an untrusted witness until replay verifies it",
        "solver_metadata": _jsonable(dict(solver_metadata or {})),
        "embedding_metadata": _jsonable(
            dict(
                embedding_metadata
                or {
                    "embedding_status": "not_requested",
                    "embedding": None,
                }
            )
        ),
    }

def compile_system(system: StructuralSystem, problem: str) -> CompiledProblem:
    if problem == "invariant":
        return compile_invariant_search_to_qubo(system)
    if problem == "migration":
        return compile_pqc_migration_to_qubo(system)
    if problem == "threshold":
        return compile_threshold_policy_to_qubo(system)
    raise ValueError(f"unsupported compile problem {problem}")


def _compiled(
    system: StructuralSystem,
    problem_type: str,
    model: QuboModel,
    metadata: Mapping[str, str],
    reverse_map: Mapping[str, Any],
) -> CompiledProblem:
    model.validate()
    problem_hash = system.canonical_hash()
    compiled_payload = {
        "problem_hash": problem_hash,
        "problem_type": problem_type,
        "model": model.to_dict(),
        "variable_metadata": dict(sorted(metadata.items())),
    }
    return CompiledProblem(
        problem_type=problem_type,
        problem_hash=problem_hash,
        compiled_model_hash=stable_problem_hash(compiled_payload),
        model=model,
        variable_metadata=metadata,
        constraints=tuple(constraint.constraint_id for constraint in system.constraints),
        objective_components=tuple(objective.objective_id for objective in system.objectives),
        reverse_map=reverse_map,
    )


def _initial_state(system: StructuralSystem) -> str:
    for constraint in system.constraints:
        if constraint.constraint_id.startswith("initial") and constraint.nodes:
            return constraint.nodes[0]
    states = [node.node_id for node in system.nodes if node.kind == "state"]
    if not states:
        raise ValueError("invariant system has no state nodes")
    return states[0]


def _edge_by_id(system: StructuralSystem, edge_id: str):
    for edge in system.edges:
        if edge.edge_id == edge_id:
            return edge
    raise ValueError(f"unknown edge {edge_id}")


def _enumerate_structural_paths(
    system: StructuralSystem, initial: str, max_depth: int
) -> list[dict[str, Any]]:
    outgoing: dict[str, list[Any]] = {}
    for edge in system.edges:
        if edge.kind == "transition":
            outgoing.setdefault(edge.source, []).append(edge)
    paths: list[dict[str, Any]] = []

    def walk(states: tuple[str, ...], edges: tuple[str, ...], depth: int) -> None:
        paths.append({"states": list(states), "edges": list(edges)})
        if depth == max_depth:
            return
        for edge in outgoing.get(states[-1], ()):
            walk(states + (edge.target,), edges + (edge.edge_id,), depth + 1)

    walk((initial,), (), 0)
    return paths


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value
