from __future__ import annotations

import argparse
import json
from pathlib import Path

from noetheris.certificates import validate_certificate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Noetheris certificate")
    parser.add_argument("certificate", help="certificate JSON file")
    args = parser.parse_args(argv)
    with Path(args.certificate).open("r", encoding="utf-8") as handle:
        certificate = json.load(handle)
    result = validate_certificate(certificate)
    print(json.dumps({"status": result.status, "reasons": list(result.reasons)}, indent=2, sort_keys=True))
    return 0 if result.status == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
