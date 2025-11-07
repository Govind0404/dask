#!/bin/bash
set -euo pipefail

case "${1:-}" in
  base)
    # Run a small, existing subset expected to pass at base commit
    if [ -f dask/tests/test_imports.py ]; then
      pytest -q dask/tests/test_imports.py
    else
      echo "[base] dask/tests/test_imports.py not found; skipping base test run"
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
