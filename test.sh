#!/bin/bash
set -euo pipefail

case "${1:-}" in
  base)
    # Run a small, existing subset expected to pass at base commit
    pytest -q dask/tests/test_imports.py
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
