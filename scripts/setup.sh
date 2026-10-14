#!/usr/bin/env bash
# Install project-local tools. Does not change your system installations.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .tools
case "$(uname -s)" in
  Darwin) platform=darwin; hugo_arch=universal ;;
  Linux) platform=linux; hugo_arch="$(uname -m)" ;;
  *) echo 'Use the manual Windows instructions in README.md.' >&2; exit 1 ;;
esac
case "$(uname -m)" in
  arm64|aarch64) go_arch=arm64; [[ "$platform" != linux ]] || hugo_arch=arm64 ;;
  x86_64) go_arch=amd64; [[ "$platform" != linux ]] || hugo_arch=amd64 ;;
  *) echo 'Unsupported CPU architecture.' >&2; exit 1 ;;
esac
task_tmp="$(mktemp -d)"
trap 'rm -rf "$task_tmp"' EXIT
hugo_file="hugo_extended_0.135.0_${platform}-${hugo_arch}.tar.gz"
go_file="go1.23.2.${platform}-${go_arch}.tar.gz"
curl --fail --location --retry 3 "https://github.com/gohugoio/hugo/releases/download/v0.135.0/$hugo_file" -o "$task_tmp/$hugo_file"
curl --fail --location --retry 3 'https://github.com/gohugoio/hugo/releases/download/v0.135.0/hugo_0.135.0_checksums.txt' -o "$task_tmp/checksums.txt"
curl --fail --location --retry 3 "https://go.dev/dl/$go_file" -o "$task_tmp/$go_file"
curl --fail --location --retry 3 "https://go.dev/dl/$go_file.sha256" -o "$task_tmp/go.sha256"
verify() {
  if command -v sha256sum >/dev/null; then actual="$(sha256sum "$1" | cut -d ' ' -f1)";
  else actual="$(shasum -a 256 "$1" | cut -d ' ' -f1)"; fi
  [[ "$actual" == "$2" ]] || { echo "Checksum mismatch: $1" >&2; exit 1; }
}
verify "$task_tmp/$hugo_file" "$(awk -v file="$hugo_file" '$2 == file {print $1}' "$task_tmp/checksums.txt")"
verify "$task_tmp/$go_file" "$(tr -d '\r\n' < "$task_tmp/go.sha256")"
tar -xzf "$task_tmp/$hugo_file" -C .tools hugo
# Extract to a fresh versioned folder to avoid mixing Go releases.
mkdir -p .tools/go-1.23.2
tar -xzf "$task_tmp/$go_file" -C .tools/go-1.23.2
if [[ -L .tools/go ]]; then unlink .tools/go; fi
if [[ ! -e .tools/go ]]; then ln -s go-1.23.2/go .tools/go; fi
.tools/hugo version
./scripts/setup-publications.sh
printf '\nReady. Run ./scripts/preview.sh and open the local URL it prints.\n'
