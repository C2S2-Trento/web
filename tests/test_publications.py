"""Behavioral checks for importing real-world BibTeX exports."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from import_publications import RESEARCH_AREAS, convert, generate

BASE = r'''@string{venue = "Journal of " # "Social Science"}
@article{example,
 title = {{AI} and \textit{society}: A {nested {title}}},
 author = {de Courson, Beno\^{i}t and Garc\'{i}a, Ana and {Research and Development Group}},
 year = {2025}, journal = venue,
 doi = {https://doi.org/10.1234/example},
 research_areas = {human-social-behavior},
 featured = {true}
}
'''

class BibliographyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'papers.bib'
        self.output = Path(self.temp.name) / 'publications.json'
    def put(self, text):
        self.source.write_text(text, encoding='utf-8')
        return convert(self.source)
    def test_exported_latex_names_macros_and_download_roundtrip(self):
        item = self.put(BASE)[0]
        self.assertEqual(item['title'], 'AI and society: A nested title')
        self.assertEqual(item['authors'], ['Benoît de Courson', 'Ana García', 'Research and Development Group'])
        self.assertEqual(item['venue'], 'Journal of Social Science')
        self.assertEqual(item['doi'], '10.1234/example')
        self.assertTrue(item['featured'])
        self.assertEqual(self.put(item['bibtex'])[0]['title'], item['title'])
    def test_selection_year_order_and_removal(self):
        more = BASE.replace('example,', 'newer,').replace('2025', '2026').replace('10.1234/example', '10.1234/newer')
        hidden = BASE.replace('example,', 'hidden,').replace('featured = {true}', 'selected = {false}')
        self.assertEqual([p['key'] for p in self.put(BASE + more + hidden)], ['newer', 'example'])
        generate(self.source, self.output)
        self.source.write_text(BASE)
        generate(self.source, self.output)
        self.assertEqual(len(json.loads(self.output.read_text())), 1)
    def test_invalid_import_keeps_previous_output(self):
        self.put(BASE)
        generate(self.source, self.output)
        original = self.output.read_bytes()
        self.source.write_text(BASE.replace('year = {2025},', ''))
        with self.assertRaisesRegex(ValueError, 'missing year'):
            generate(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), original)
    def test_duplicate_doi_and_key_fail(self):
        with self.assertRaisesRegex(ValueError, 'duplicate DOI'):
            self.put(BASE + BASE.replace('example,', 'duplicate,'))
        with self.assertRaises(Exception):
            self.put(BASE + BASE)
    def test_malformed_and_unsafe_urls_fail(self):
        with self.assertRaises(Exception):
            self.put(BASE[:-3])
        with self.assertRaisesRegex(ValueError, 'http'):
            self.put(BASE.replace('featured = {true}', 'pdf = {javascript:alert(1)}'))
    def test_deterministic_import(self):
        self.put(BASE)
        generate(self.source, self.output)
        before = self.output.stat().st_mtime_ns
        generate(self.source, self.output)
        self.assertEqual(self.output.stat().st_mtime_ns, before)
    def test_research_areas_roundtrip(self):
        item = self.put(BASE.replace('research_areas = {human-social-behavior}',
                                    'research_areas = { human-social-behavior, demography-inequality-welfare }'))[0]
        self.assertEqual(item['research_areas'], ['human-social-behavior', 'demography-inequality-welfare'])
        self.assertEqual(self.put(item['bibtex'])[0]['research_areas'], item['research_areas'])
    def test_invalid_research_areas_fail_without_replacing_data(self):
        self.put(BASE)
        generate(self.source, self.output)
        original = self.output.read_bytes()
        for value in ['', 'unknown', 'human-social-behavior,',
                      'human-social-behavior, human-social-behavior',
                      'human-social-behavior, collective-behavior-action, demography-inequality-welfare']:
            with self.subTest(value=value):
                self.source.write_text(BASE.replace('research_areas = {human-social-behavior}',
                                                   'research_areas = {' + value + '}'))
                with self.assertRaisesRegex(ValueError, 'research.area'):
                    generate(self.source, self.output)
                self.assertEqual(self.output.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, 'research_areas'):
            self.put(BASE.replace(' research_areas = {human-social-behavior},\n', ''))
    def test_site_bibliography_has_distinct_links_and_complete_citations(self):
        source = Path(__file__).resolve().parents[1] / 'publications.bib'
        papers = convert(source)
        self.assertTrue(papers)
        self.assertEqual(len({p['url'] for p in papers}), len(papers))
        self.assertTrue(all(p['authors'] and p['venue'] for p in papers))
        self.assertTrue(all(1 <= len(p['research_areas']) <= 2 for p in papers))
        self.assertEqual({area for p in papers for area in p['research_areas']}, set(RESEARCH_AREAS))
        root = source.parent
        self.assertTrue(all((root / 'content/research' / area / 'index.md').exists() for area in RESEARCH_AREAS))

if __name__ == '__main__':
    unittest.main()
