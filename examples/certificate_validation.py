from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from noetheris.annealing import search_invariant_violation
from noetheris.certificates import certificate_fingerprint, validate_certificate
from noetheris.graph import StateGraph


def main() -> None:
    graph = StateGraph.from_json_file(ROOT / "examples" / "consensus_protocol.json")
    result = search_invariant_violation(graph, max_depth=3, seed=2026)
    validation = validate_certificate(result.certificate)
    rejected = result.certificate.to_dict()
    rejected["total_energy"] += 1.0
    rejected_validation = validate_certificate(rejected)
    print(
        json.dumps(
            {
                "valid_certificate_status": validation.status,
                "valid_certificate_fingerprint": certificate_fingerprint(result.certificate),
                "valid_certificate_reasons": validation.reasons,
                "tampered_certificate_status": rejected_validation.status,
                "tampered_certificate_reasons": rejected_validation.reasons,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
