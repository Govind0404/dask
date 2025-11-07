#!/bin/bash
set -euo pipefail

case "${1:-}" in
  base)
    # Run a small, existing subset expected to pass at base commit
    if [ -f dask/tests/test_imports.py ]; then
      pytest -q dask/tests/test_imports.py
    elif [ -d dask/tests ]; then
      # Fallback: run any "imports"-related tests to avoid zero-test runs
      pytest -q -k imports dask/tests
    else
      # Last-resort smoke test so base mode never runs zero checks
      python - <<'PY'
import importlib
for mod in ("dask",):
    importlib.import_module(mod)
print("SMOKE_OK")
PY
    fi
    ;;
  new)
    # Run newly added tests that define the win condition (should fail at base)
    pytest -q tests/new/test_scaling_hints.py
    ;;
  *)
    echo "Usage: ./test.sh {base|new}"
    exit 1
    ;;
esac
