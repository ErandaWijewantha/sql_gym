#!/usr/bin/env bash
# Thin wrapper around validate_all_solutions.py so it can be run the
# same way as the other shell scripts.
set -euo pipefail
cd "$(dirname "$0")/.."
source .env 2>/dev/null || true
python scripts/validate_all_solutions.py
