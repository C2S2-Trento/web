"""Check generated pages for broken local links/assets, at any deployment prefix."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
import sys

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.canonical = [], set(), None
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.links.append(attrs[attr])

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'public')
pages = {p: Page(p.read_text()) for p in root.rglob('*.html')}
assert root / 'index.html' in pages, 'Missing homepage'
base = pages[root / 'index.html'].canonical
assert base, 'Missing canonical URL'
base_parts = urlparse(base)
errors = []
checked = 0
for path, page in pages.items():
    relative = path.relative_to(root).as_posix()
    page_url = urljoin(base, relative.removesuffix('index.html'))
    for link in page.links:
        target = urlparse(urljoin(page_url, link))
        if target.scheme not in ('http', 'https') or target.netloc != base_parts.netloc:
            continue
        if not target.path.startswith(base_parts.path):
            errors.append(f'{path}: outside deployment prefix: {link}')
            continue
        local = root / unquote(target.path[len(base_parts.path):])
        if local.is_dir():
            local = local / 'index.html'
        if not local.exists():
            errors.append(f'{path}: missing {link}')
        elif target.fragment and local in pages and unquote(target.fragment) not in pages[local].ids:
            errors.append(f'{path}: missing anchor {link}')
        checked += 1
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'Checked {len(pages)} HTML pages and {checked} local links/assets: OK')
