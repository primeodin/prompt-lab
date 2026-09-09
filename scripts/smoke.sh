#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]" -q
.venv/bin/pytest -q
.venv/bin/python -m prompt_lab --mock
echo smoke ok
