from __future__ import annotations

from pathlib import Path


def release_benchmark_manifest() -> dict[str, str]:
    root = Path(__file__).resolve().parents[3]
    return {
        "json": str(root / "benchmarks" / "results" / "noetheris_v0_1_baseline.json"),
        "csv": str(root / "benchmarks" / "results" / "noetheris_v0_1_baseline.csv"),
        "runner": str(root / "benchmarks" / "run_benchmarks.py"),
    }
