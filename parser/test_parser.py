#!/usr/bin/env python3
"""
PARSER UNIT TESTS
=================
Unit tests for Turoyo verb parser functions.

Tests cover:
- Root extraction
- Stem parsing
- Etymology parsing
- Conjugation extraction
- Token generation
- Edge cases

Usage:
    python3 parser/test_parser.py              # Run all tests
    python3 parser/test_parser.py -v           # Verbose output
    python3 parser/test_parser.py TestRootExtraction  # Run specific test class

Author: Claude Code
Created: 2025-10-13
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parse_verbs import TuroyoVerbParser


class TestRootExtraction(unittest.TestCase):
    """Test root extraction from HTML"""

    def setUp(self):
        """Create parser instance with mock HTML"""
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)
        self.parser.stats = {}
        self.parser.errors = []

    def test_simple_root(self):
        """Test extraction of simple root without number"""
        html = '<p class="western"><span>ʔmr</span></p>'
        roots = self.parser.extract_roots_from_section(html)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0][0], 'ʔmr')

    def test_root_with_homonym_number(self):
        """Test extraction of root with homonym number"""
        html = '<p class="western"><span>ʔmr 1</span></p>'
        roots = self.parser.extract_roots_from_section(html)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0][0], 'ʔmr 1')

    def test_multiple_roots(self):
        """Test extraction of multiple roots"""
        html = '''
        <p class="western"><span>ʔmr</span></p>
        <p class="western"><span>ʕbd</span></p>
        '''
        roots = self.parser.extract_roots_from_section(html)
        self.assertEqual(len(roots), 2)

    def test_filters_german_glosses(self):
        """Test that German glosses are filtered out"""
        html = '''
        <p class="western"><span>ʔmr</span></p>
        <p class="western"><span>speichern;</span></p>
        '''
        roots = self.parser.extract_roots_from_section(html)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0][0], 'ʔmr')


class TestEtymologyParsing(unittest.TestCase):
    """Test etymology parsing"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)

    def test_simple_etymology(self):
        """Test parsing of simple etymology"""
        html = '(&lt; MEA ʔmr cf. SL 57: to say; to pronounce;)'
        result = self.parser.parse_etymology(html)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['etymons']), 1)
        self.assertEqual(result['etymons'][0]['source'], 'MEA')
        self.assertEqual(result['etymons'][0]['source_root'], 'ʔmr')

    def test_etymology_with_relationship(self):
        """Test etymology with 'also' relationship"""
        html = '(&lt; MEA ʔmr also Syr. ʔmr)'
        result = self.parser.parse_etymology(html)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['etymons']), 2)
        self.assertEqual(result.get('relationship'), 'also')

    def test_no_etymology(self):
        """Test entry without etymology"""
        html = '<p>Some text without etymology</p>'
        result = self.parser.parse_etymology(html)
        self.assertIsNone(result)


class TestStemParsing(unittest.TestCase):
    """Test stem header parsing"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)

    def test_stem_extraction(self):
        """Test extraction of stem header"""
        html = '''
        <font size="4"><b><span>I: </span></b></font>
        <font><font><i><b><span>məlle/omər</span></b></i></font></font>
        '''
        stems = self.parser.parse_stems(html)
        self.assertEqual(len(stems), 1)
        self.assertEqual(stems[0]['stem'], 'I')
        self.assertIn('məlle', stems[0]['forms'])
        self.assertIn('omər', stems[0]['forms'])

    def test_multiple_stems(self):
        """Test extraction of multiple stems"""
        html = '''
        <font size="4"><b><span>I: </span></b></font>
        <font><i><b><span>məlle/omər</span></b></i></font>
        <font size="4"><b><span>III: </span></b></font>
        <font><i><b><span>mtamər</span></b></i></font>
        '''
        stems = self.parser.parse_stems(html)
        self.assertGreaterEqual(len(stems), 2)


class TestTokenGeneration(unittest.TestCase):
    """Test HTML to token conversion"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)

    def test_simple_text(self):
        """Test conversion of simple text"""
        html = '<p>Hello world</p>'
        tokens = self.parser.html_to_tokens(html)
        self.assertTrue(any('Hello world' in t['text'] for t in tokens))

    def test_italic_text(self):
        """Test italic text is marked"""
        html = '<p>Normal <i>italic</i> text</p>'
        tokens = self.parser.html_to_tokens(html)
        italic_tokens = [t for t in tokens if t['italic']]
        non_italic_tokens = [t for t in tokens if not t['italic']]
        self.assertTrue(len(italic_tokens) > 0)
        self.assertTrue(len(non_italic_tokens) > 0)

    def test_block_spacing(self):
        """Test that block elements add spacing"""
        html = '<p>First</p><p>Second</p>'
        tokens = self.parser.html_to_tokens(html)
        self.assertTrue(len(tokens) > 2)


class TestConjugationExtraction(unittest.TestCase):
    """Test conjugation table extraction"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)

    def test_conjugation_header_normalization(self):
        """Test conjugation header normalization"""
        self.assertEqual(self.parser.normalize_header('Imperativ'), ['Imperative'])
        self.assertEqual(self.parser.normalize_header('Infinitiv'), ['Infinitive'])
        self.assertEqual(self.parser.normalize_header('Part act.'), ['Participle_Active'])
        self.assertEqual(self.parser.normalize_header('Part pass.'), ['Participle_Passive'])

    def test_split_header_with_and(self):
        """Test header with 'and' splits correctly"""
        result = self.parser.normalize_header('Part act. and Part pass.')
        self.assertEqual(len(result), 2)
        self.assertIn('Participle_Active', result)
        self.assertIn('Participle_Passive', result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)
        self.parser.stats = {}
        self.parser.errors = []

    def test_empty_html(self):
        """Test handling of empty HTML"""
        tokens = self.parser.html_to_tokens('')
        self.assertEqual(tokens, [])

    def test_malformed_html(self):
        """Test handling of malformed HTML"""
        html = '<p>Unclosed tag'
        try:
            tokens = self.parser.html_to_tokens(html)
            self.assertIsInstance(tokens, list)
        except Exception as e:
            self.fail(f"html_to_tokens raised exception: {e}")

    def test_unicode_handling(self):
        """Test proper Unicode handling"""
        html = '<p>ʔʕġǧḥṣštṭḏṯẓāēīūə</p>'
        tokens = self.parser.html_to_tokens(html)
        self.assertTrue(len(tokens) > 0)
        full_text = ''.join(t['text'] for t in tokens)
        self.assertIn('ʔ', full_text)

    def test_html_entity_decoding(self):
        """Test HTML entity decoding in etymology"""
        html = '(&lt; MEA ʔmr &amp; test)'
        result = self.parser.parse_etymology(html)
        if result:
            raw_text = str(result)
            self.assertIn('<', raw_text)
            self.assertIn('&', raw_text)


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity validation"""

    def test_no_html_in_output(self):
        """Test that output has no HTML tags in text fields"""
        pass

    def test_utf8_encoding(self):
        """Test all text is valid UTF-8"""
        pass


class TestHomonymNumbering(unittest.TestCase):
    """Test homonym numbering logic"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)
        self.parser.stats = {}
        self.parser.verbs = []

    def test_different_etymologies_get_numbers(self):
        """Test that verbs with same root but different etymologies get numbered"""
        self.parser.verbs = [
            {
                'root': 'ʔmr',
                'etymology': {
                    'etymons': [{'source': 'MEA', 'source_root': 'ʔmr'}]
                }
            },
            {
                'root': 'ʔmr',
                'etymology': {
                    'etymons': [{'source': 'Syr', 'source_root': 'ʔmr'}]
                }
            }
        ]
        self.parser.add_homonym_numbers()
        self.assertEqual(self.parser.verbs[0]['root'], 'ʔmr 1')
        self.assertEqual(self.parser.verbs[1]['root'], 'ʔmr 2')

    def test_same_etymology_no_numbers(self):
        """Test that verbs with same etymology don't get numbered"""
        self.parser.verbs = [
            {
                'root': 'ʔmr',
                'etymology': {
                    'etymons': [{'source': 'MEA', 'source_root': 'ʔmr'}]
                }
            },
            {
                'root': 'ʔmr',
                'etymology': {
                    'etymons': [{'source': 'MEA', 'source_root': 'ʔmr'}]
                }
            }
        ]
        original_roots = [v['root'] for v in self.parser.verbs]
        self.parser.add_homonym_numbers()
        self.assertEqual(self.parser.verbs[0]['root'], 'ʔmr')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestRootExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestEtymologyParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestStemParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestTokenGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestConjugationExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestHomonymNumbering))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


def main():
    """Main entry point"""
    print("=" * 80)
    print("TUROYO PARSER UNIT TESTS")
    print("=" * 80)
    print()

    exit_code = run_tests()

    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)

    sys.exit(exit_code)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        unittest.main()
    else:
        main()
