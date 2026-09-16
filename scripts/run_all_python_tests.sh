#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="${PYTHONPATH}:$(pwd)/python"
else
  export PYTHONPATH="$(pwd)/python"
fi
source "$(dirname "${BASH_SOURCE[0]}")/python_env.sh"
"${NOETHERIS_PYTHON_CMD[@]}" -m compileall python examples benchmarks
"${NOETHERIS_PYTHON_CMD[@]}" -m pytest
