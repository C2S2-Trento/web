#!/usr/bin/env python3
"""Convert publications.bib to Hugo data. No network calls; BibTeX is authoritative."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

from pybtex.database import BibliographyData, parse_file
from pylatexenc.latex2text import LatexNodes2Text

ROOT = Path(__file__).resolve().parents[1]


def plain(value):
    return ' '.join(LatexNodes2Text().latex_to_text(value).split())


def boolean(value, default, key, field):
    if value is None:
        return default
    if value.strip().lower() in ('true', 'yes', '1'):
        return True
    if value.strip().lower() in ('false', 'no', '0'):
        return False
    raise ValueError(f'{key}: {field} must be true or false')


def web_url(value, key):
    if not value:
        return ''
    value = value.replace('\\&', '&').strip()
    parsed = urlparse(value)
    if parsed.scheme not in ('https', 'http') or not parsed.netloc:
        raise ValueError(f'{key}: expected an http(s) URL, got {value!r}')
    return value


def convert(source):
    bibliography = parse_file(str(source), bib_format='bibtex')
    result, seen_dois = [], set()
    for key, entry in bibliography.entries.items():
        fields = entry.fields
        if not boolean(fields.get('selected'), True, key, 'selected'):
            continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]*', key):
            raise ValueError(f'{key}: citation keys must use letters, numbers, dots, colons, underscores or hyphens')
        if fields.get('crossref'):
            raise ValueError(f'{key}: export a self-contained entry (expand crossref fields first)')
        for field in ('title', 'year'):
            if not fields.get(field, '').strip():
                raise ValueError(f'{key}: missing {field}')
        if not re.fullmatch(r'\d{4}', fields['year']):
            raise ValueError(f'{key}: year must have four digits')
        people = entry.persons.get('author', [])
        if not people:
            raise ValueError(f'{key}: missing author')
        authors = []
        for person in people:
            name = ' '.join(person.first_names + person.middle_names + person.prelast_names + person.last_names)
            if person.lineage_names:
                name += ', ' + ' '.join(person.lineage_names)
            authors.append(plain(name))
        title = plain(fields['title'])
        venue = plain(fields.get('journal') or fields.get('booktitle') or fields.get('publisher') or fields.get('howpublished') or '')
        if not venue:
            raise ValueError(f'{key}: supply journal, booktitle, publisher, or howpublished')
        doi = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', fields.get('doi', '').strip(), flags=re.I)
        if doi:
            if not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
                raise ValueError(f'{key}: invalid DOI')
            if doi.lower() in seen_dois:
                raise ValueError(f'{key}: duplicate DOI {doi}')
            seen_dois.add(doi.lower())
        url = web_url(fields.get('url', ''), key)
        if not doi and not url:
            raise ValueError(f'{key}: supply a DOI or publisher URL')
        # Re-export one parsed entry: macros are expanded and valid LaTeX is retained.
        citation = BibliographyData(entries={key: entry}).to_string('bibtex')
        item = dict(key=key, title=title, authors=authors, year=int(fields['year']), venue=venue,
                    doi=doi, url='https://doi.org/' + quote(doi, safe='/():;.-_') if doi else url,
                    bibtex=citation, featured=boolean(fields.get('featured'), False, key, 'featured'),
                    type='Conference paper' if entry.type == 'inproceedings' else 'Book chapter' if entry.type in ('inbook','incollection') else 'Preprint' if entry.type in ('unpublished','misc') else 'Journal article' if entry.type == 'article' else 'Research item',
                    volume=plain(fields.get('volume', '')), number=plain(fields.get('number', '')),
                    pages=plain(fields.get('pages', '')).replace('--', '–'),
                    pdf=web_url(fields.get('pdf', ''), key), code=web_url(fields.get('code', ''), key),
                    correction=web_url(fields.get('correction', ''), key))
        result.append(item)
    return sorted(result, key=lambda p: (-p['year'], p['title'].casefold()))


def generate(source=ROOT / 'publications.bib', output=ROOT / 'data/publications.json'):
    items = convert(source)
    # Validate everything before replacing the previous successful import.
    payload = json.dumps(items, ensure_ascii=False, indent=2) + '\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists() or output.read_text(encoding='utf-8') != payload:
        temporary = output.with_suffix('.json.tmp')
        temporary.write_text(payload, encoding='utf-8')
        temporary.replace(output)
    return len(items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'publications.bib')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/publications.json')
    args = parser.parse_args()
    try:
        count = generate(args.source, args.output)
    except Exception as exc:
        print(f'BibTeX import failed: {exc}', file=sys.stderr)
        return 1
    print(f'Imported {count} publications from {args.source.name}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
