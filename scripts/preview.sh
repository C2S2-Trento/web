#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools:$PWD/.tools/go/bin:$PATH"
if ! command -v hugo >/dev/null || ! command -v go >/dev/null; then
  echo 'Run ./scripts/setup.sh once to install the local preview tools.' >&2
  exit 1
fi
if [[ "$(hugo version)" != *'v0.135.0-'* ]]; then
  echo 'This template requires Hugo Extended 0.135.0. Run ./scripts/setup.sh.' >&2
  exit 1
fi
exec hugo server --disableFastRender "$@"
