#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools:$PWD/.tools/go/bin:$PATH"
if [[ ! -x .tools/bibtex-venv/bin/python ]]; then
  echo 'Run ./scripts/setup-publications.sh once to install the BibTeX tools.' >&2
  exit 1
fi
.tools/bibtex-venv/bin/python scripts/import_publications.py
hugo --minify "$@"
