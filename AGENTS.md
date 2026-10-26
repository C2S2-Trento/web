# Repository Guidelines

## Project Structure & Module Organization

This is a Hugo site for C2S2. Edit pages in `content/` (research areas, events, people, and publications), site settings in `config/_default/`, and Hugo templates in `layouts/`. Styles and processed images live in `assets/`; files served unchanged live in `static/`. Keep bibliography records in `publications.bib`; `scripts/import_publications.py` generates `data/publications.json`. Python checks are in `tests/`. Treat `examples/original-starter/` as reference material, not current site content.

The Opportunities page always displays guidance that students can contact researchers about thesis projects and internships. Keep this guidance visible whether or not opportunity listings are present; render listings as an optional section below it.

## Build, Test, and Development Commands

- `./scripts/setup.sh`: install the pinned Hugo Extended, Go, and Python tools into `.tools/` once per machine.
- `./scripts/preview.sh`: import publications and serve a live local preview; pass `--buildDrafts` to inspect draft pages.
- `./scripts/build.sh`: import publications and build the minified site into `public/`.
- `.tools/bibtex-venv/bin/python -m unittest discover -s tests -v`: run bibliography importer tests.
- `python3 scripts/check_site.py public`: check generated internal links, assets, and fragment targets after a build.

Run the build, tests, and link checker before opening a pull request. The GitHub Actions workflow runs the same checks on pull requests.

## Coding Style & Naming Conventions

Follow `.editorconfig`: UTF-8, LF line endings, two-space indentation, final newline, and no trailing whitespace (Markdown is exempt from trimming). Match nearby Hugo template, YAML front matter, SCSS, and Python style. Use lowercase hyphenated folder slugs such as `content/event/cultural-change/`; keep content pages as `index.md` and section pages as `_index.md`. Name Python tests `test_*.py` with `test_*` methods.

## Testing & Content Review

Use Python `unittest` for importer behavior; no numeric coverage target is configured. For content changes, inspect the local preview and run the generated-site link checker. Validate event dates and time-zone offsets. Check publication authors, year, DOI, and citation key against the source before editing `publications.bib`. Do not edit generated `data/publications.json` or commit `.tools/`, `public/`, or Hugo caches.

## Commits & Pull Requests

Recent commits use short descriptive subjects such as `Research areas updated` and `added publications`; no prefix scheme is established. Use a concise subject that identifies the change. In pull requests, describe affected pages or data, report the build and check results, and include screenshots for visual changes. Link a related issue when one exists.
