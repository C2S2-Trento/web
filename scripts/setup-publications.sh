#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .tools/bibtex-venv
.tools/bibtex-venv/bin/python -m pip install -r requirements-publications.txt
