#!/usr/bin/env python3
"""Run Hugo and reimport the bibliography whenever the BibTeX file changes."""
import subprocess
import sys
from pathlib import Path
from import_publications import ROOT, generate

source = ROOT / 'publications.bib'

def signature():
    return source.read_bytes() if source.exists() else None

def run():
    generate()
    previous = signature()
    process = subprocess.Popen(['hugo', 'server', '--disableFastRender', *sys.argv[1:]], cwd=ROOT)
    try:
        while process.poll() is None:
            try:
                return process.wait(timeout=0.7)
            except subprocess.TimeoutExpired:
                current = signature()
                if current != previous:
                    previous = current
                    try:
                        print(f'BibTeX updated: {generate()} publications imported.', flush=True)
                    except Exception as exc:
                        print(f'BibTeX import failed; keeping the last valid preview: {exc}', file=sys.stderr, flush=True)
        return process.returncode
    except KeyboardInterrupt:
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

if __name__ == '__main__':
    try:
        sys.exit(run())
    except Exception as exc:
        print(f'Preview failed: {exc}', file=sys.stderr)
        sys.exit(1)
