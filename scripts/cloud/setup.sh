#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$TASK_ROOT"
TASK_PYTHON="${VALUATION_PYTHON:-python3.12}"
"$TASK_PYTHON" -c 'import sys; assert sys.version_info[:2] == (3,12), "Use Python3.12; set VALUATION_PYTHON to its executable"'
node -e 'const [a,b]=process.versions.node.split(".").map(Number);if(a<22||(a===22&&b<12))throw Error("Node22.12+ required")'
"$TASK_PYTHON" -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements-api-dev.lock
.venv/bin/python -m pip check
npm --prefix frontend ci --no-audit --no-fund
.venv/bin/python scripts/cloud/research.py
npm --prefix frontend run build
PYTHONPATH=src .venv/bin/python scripts/cloud/workspace.py smoke
printf '%s\n' 'Setup complete. Verify: bash scripts/cloud/verify.sh; start: .venv/bin/python scripts/cloud/workspace.py serve'
