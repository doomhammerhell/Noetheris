from __future__ import annotations

from noetheris.qubo import QuboModel


def export_to_dimod_bqm(model: QuboModel) -> tuple[object | None, str]:
    """Export a QUBO model to a dimod BinaryQuadraticModel when Ocean is installed."""
    try:
        import dimod  # type: ignore
    except Exception as exc:
        return None, f"dwave ocean unavailable: {exc.__class__.__name__}"
    canonical = model.canonicalized()
    linear = dict(canonical.linear)
    quadratic = {
        (term.left, term.right): term.coefficient for term in canonical.quadratic
    }
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, canonical.constant, dimod.BINARY)
    return bqm, "dimod binary quadratic model exported"
