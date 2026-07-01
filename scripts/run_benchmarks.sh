#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/python"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"${PYTHON_BIN}" benchmarks/run_benchmarks.py
