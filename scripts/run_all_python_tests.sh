#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/python"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"${PYTHON_BIN}" -m compileall python examples benchmarks
"${PYTHON_BIN}" -m pytest
