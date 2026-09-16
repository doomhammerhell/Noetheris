#!/usr/bin/env bash

noetheris_select_python() {
  local requested_python="${PYTHON_BIN:-python3}"
  if [[ -z "${PYTHON_BIN+x}" && "$(uname -s)" == "Darwin" ]]; then
    if command -v arch >/dev/null 2>&1; then
      if arch -arm64 "${requested_python}" - <<'PY' >/dev/null 2>&1
import platform
raise SystemExit(0 if platform.machine() == "arm64" else 1)
PY
      then
        NOETHERIS_PYTHON_CMD=(arch -arm64 "${requested_python}")
        return
      fi
    fi
  fi
  NOETHERIS_PYTHON_CMD=("${requested_python}")
}

noetheris_select_python
