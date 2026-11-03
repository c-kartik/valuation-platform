#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$TASK_ROOT"
export PYTHONPATH=src
.venv/bin/python scripts/cloud/research.py --check
.venv/bin/python scripts/cloud/workspace.py smoke
.venv/bin/python -m unittest discover -s tests/valuation -v
.venv/bin/python -m unittest discover -s tests/preload -v
.venv/bin/python -m unittest discover -s tests/review -p 'test_*resolution.py' -v
.venv/bin/python -m unittest discover -s tests/review -p 'test_cfo_history.py' -v
.venv/bin/python -m unittest discover -s tests/cloud -v
.venv/bin/python scripts/resolve_apple_cashflows.py --check
.venv/bin/python scripts/resolve_meta_alphabet_cashflows.py --check
.venv/bin/python scripts/verify_registered_preloads.py --check
npm --prefix frontend test
npm --prefix frontend run build
