#!/usr/bin/env python3
"""
Turoyo HTML → JSON Parser
Fault-tolerant parser that extracts verb data with comprehensive error tracking
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import json
from typing import Dict, List, Optional, Tuple
import sys

class TuroyoParser:
    """Fault-tolerant parser for Turoyo verb glossary"""

    # Normalization maps
    HEADER_NORMALIZE = {
        # Imperatives
        'Imperativ': 'Imperative',
        '    Imperativ': 'Imperative',

        # Infinitives
        'Infinitiv': 'Infinitive',
        '   Infinitive': 'Infinitive',

        # Preterits
        'Preterite': 'Preterit',
        '     Preterite': 'Preterit',
        '     Preterit': 'Preterit',
        'k-Preterit': 'ko-Preterit',
        'Preterit 1': 'Preterit_1',
        'Preterit 2': 'Preterit_2',

        # Infectum variations
        ' Infectum': 'Infectum',
        ' Infectum-wa': 'Infectum-wa',
        'Infectum - wa': 'Infectum-wa',
        'Infectum – wa': 'Infectum-wa',  # em-dash
        'Infectum and Infectum-wa': 'Infectum_and_Infectum-wa',
        'Infectum (???)': 'Infectum_uncertain',
        'Infectum – Transitive': 'Infectum_Transitive',

        # Participles
        'Part act.': 'Part_Act',
        'Part. act.': 'Part_Act',
        'Part Act.': 'Part_Act',
        'Part. Act.': 'Part_Act',
        'Part pass.': 'Part_Pass',
        'Part. pass.': 'Part_Pass',
        'Part. Pass.': 'Part_Pass',
        'Part.Pass': 'Part_Pass',
        'Pass. Part.': 'Part_Pass',
        'Passive Part.': 'Part_Pass',
        'Past Part.': 'Part_Pass',
        'Past Participle': 'Part_Pass',
        'Part': 'Participle',
        'Participle': 'Participle',

        # Nomina
        'Nomen Actionis': 'Nomen_Actionis',
        'Nomen Patiens': 'Nomen_Patiens',
        'Nomen Patientis?': 'Nomen_Patientis_uncertain',
        'Nomen agentis': 'Nomen_Agentis',

        # Detransitive
        'Detransitive infectum': 'Detransitive_Infectum',
    }

    def __init__(self, html_path: str):
        self.html_path = Path(html_path)
        print(f"📖 Loading {self.html_path.name}...")

        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.soup = BeautifulSoup(self.html, 'html.parser')

        # Error tracking
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)
        self.stats = defaultdict(int)

        # Results
        self.verbs = []

    def normalize_header(self, header: str) -> str:
        """Normalize table headers to canonical form"""
        header = header.strip()
        return self.HEADER_NORMALIZE.get(header, header)

    def extract_text(self, element) -> str:
        """Safely extract text from element"""
        if element is None:
            return ""

        if isinstance(element, str):
            return element.strip()

        return element.get_text().strip()

    def parse_etymology(self, etym_text: str) -> Optional[Dict]:
        """Parse etymology string like '(&lt; MEA ʔmr cf. SL 57: to say;)'"""
        if not etym_text:
            return None

        try:
            # Pattern: (< SOURCE root cf. REF: meaning)
            pattern = r'\(<?\s*&lt;\s*([^>]+?)\s+([^\s]+)\s+cf\.\s+([^:]+):\s*([^)]+)\)'
            match = re.search(pattern, etym_text)

            if match:
                return {
                    'source': match.group(1).strip(),
                    'root': match.group(2).strip(),
                    'reference': match.group(3).strip(),
                    'meaning': match.group(4).strip()
                }

            # Simpler pattern without cf.
            simple_pattern = r'\(<?\s*&lt;\s*([^>]+?)\s+([^\)]+)\)'
            match = re.search(simple_pattern, etym_text)

            if match:
                return {
                    'source': match.group(1).strip(),
                    'notes': match.group(2).strip()
                }

        except Exception as e:
            self.warnings['etymology'].append(f"Failed to parse: {etym_text[:100]}")

        return None

    def parse_stem_header(self, text: str) -> Optional[Tuple[str, str]]:
        """Parse stem header like 'I: abəʕ/obəʕ' or 'II: mʔadəb/miʔadəb'"""
        # Match patterns like "I:", "II:", "III:"
        stem_match = re.search(r'^([IVX]+):\s*(.*)$', text.strip())

        if stem_match:
            stem_num = stem_match.group(1)
            forms_text = stem_match.group(2).strip()

            # Extract forms (usually italic bold)
            # Forms are separated by /
            forms = [f.strip() for f in forms_text.split('/') if f.strip()]

            return (stem_num, forms)

        return None

    def parse_table(self, table_elem) -> Optional[Dict]:
        """Parse a conjugation table"""
        try:
            rows = table_elem.find_all('tr')

            if not rows:
                return None

            result = {}

            for row in rows:
                cells = row.find_all('td')

                if len(cells) != 2:
                    continue

                # First cell: header (conjugation type)
                header = self.extract_text(cells[0])
                header = self.normalize_header(header)

                # Second cell: content (examples, forms, etc.)
                content = self.extract_text(cells[1])

                result[header] = content

            return result if result else None

        except Exception as e:
            self.errors['table_parsing'].append(str(e))
            return None

    def parse_verb_entry(self, root_p, following_elements) -> Dict:
        """Parse a complete verb entry starting from root paragraph"""
        entry = {
            'root': '',
            'etymology': None,
            'meanings': [],
            'stems': [],
            'cross_reference': None,
            'notes': [],
            'uncertain': False
        }

        try:
            # Extract root
            root_text = self.extract_text(root_p)

            # Check for cross-reference (root → other_root)
            if '→' in root_text:
                parts = root_text.split('→')
                entry['root'] = parts[0].strip()
                entry['cross_reference'] = parts[1].strip() if len(parts) > 1 else None
                return entry

            # Extract just the root (first word)
            root_match = re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)', root_text)
            if root_match:
                entry['root'] = root_match.group(1)

            # Check for uncertain marker
            if '???' in root_text:
                entry['uncertain'] = True

            # Parse following elements
            current_stem = None

            for elem in following_elements:
                elem_text = self.extract_text(elem)

                # Check if next root (stop processing)
                if elem.name == 'h1':
                    break

                # Etymology (usually right after root)
                if '&lt;' in str(elem) and not entry['etymology']:
                    entry['etymology'] = self.parse_etymology(str(elem))

                # Binyan header (I:, II:, III:)
                if elem.name == 'p' and re.search(r'font-size:\s*14pt', str(elem)):
                    stem_data = self.parse_stem_header(elem_text)
                    if stem_data:
                        current_stem = {
                            'stem': stem_data[0],
                            'forms': stem_data[1] if isinstance(stem_data[1], list) else [],
                            'meanings': [],
                            'conjugations': {}
                        }
                        entry['stems'].append(current_stem)

                # Detransitive marker
                if 'Detransitive' in elem_text and 'font-size: 16pt' in str(elem):
                    current_stem = {
                        'stem': 'Detransitive',
                        'forms': [],
                        'meanings': [],
                        'conjugations': {}
                    }
                    entry['stems'].append(current_stem)

                # Meanings (small font paragraphs after stem)
                if elem.name == 'p' and current_stem and 'font-size: 10pt' in str(elem):
                    meaning_text = elem_text
                    # Extract numbered meanings: 1) ...; 2) ...
                    meanings = re.split(r'\d+\)', meaning_text)
                    for m in meanings:
                        m = m.strip(' ;')
                        if m:
                            current_stem['meanings'].append(m)

                # Tables (conjugations)
                if elem.name == 'table' and current_stem:
                    table_data = self.parse_table(elem)
                    if table_data:
                        current_stem['conjugations'].update(table_data)

        except Exception as e:
            self.errors['verb_entry'].append(f"Root {entry.get('root', '?')}: {e}")

        return entry

    def parse_all(self) -> List[Dict]:
        """Main parsing method"""
        print("🔄 Parsing verb entries...")

        # Find all paragraphs with potential roots
        # Roots are in <p class="western"> with specific font pattern
        all_paragraphs = self.soup.find_all('p', class_='western')

        i = 0
        while i < len(all_paragraphs):
            p = all_paragraphs[i]

            # Check if this looks like a root entry
            # (has root-like text at the start)
            text = self.extract_text(p)

            # Skip empty or very short paragraphs
            if len(text) < 2:
                i += 1
                continue

            # Check if starts with a root-like pattern
            if re.match(r'^[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6}(&lt;|→| )', text):
                # This looks like a root entry
                # Gather following elements until next root
                following = []
                j = i + 1

                while j < len(all_paragraphs):
                    next_p = all_paragraphs[j]
                    next_text = self.extract_text(next_p)

                    # Stop if we hit another root entry
                    if re.match(r'^[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6}(&lt;|→| )', next_text):
                        break

                    following.append(next_p)
                    j += 1

                # Parse this entry
                entry = self.parse_verb_entry(p, following)

                if entry['root']:
                    self.verbs.append(entry)
                    self.stats['verbs_parsed'] += 1

                i = j  # Skip to next root
            else:
                i += 1

            # Progress indicator
            if self.stats['verbs_parsed'] % 100 == 0:
                print(f"  Parsed {self.stats['verbs_parsed']} verbs...", end='\r')

        print(f"\n✅ Parsed {self.stats['verbs_parsed']} verb entries")
        return self.verbs

    def save_json(self, output_path: str):
        """Save parsed data to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'verbs': self.verbs,
                'metadata': {
                    'total_verbs': len(self.verbs),
                    'source_file': self.html_path.name,
                    'parser_version': '1.0.0'
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved to: {output_file}")

    def save_error_report(self, output_path: str):
        """Save error and warning report"""
        report = {
            'stats': dict(self.stats),
            'errors': dict(self.errors),
            'warnings': dict(self.warnings)
        }

        output_file = Path(output_path)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # Print summary
        print("\n📋 Parsing Report:")
        print(f"  Verbs parsed: {self.stats.get('verbs_parsed', 0)}")

        if self.errors:
            print(f"\n  ⚠️  Errors by category:")
            for category, errors in self.errors.items():
                print(f"    {category}: {len(errors)}")

        if self.warnings:
            print(f"\n  ⚡ Warnings by category:")
            for category, warnings in self.warnings.items():
                print(f"    {category}: {len(warnings)}")

        print(f"\n  Full report: {output_file}")


def main():
    html_file = Path(__file__).parent.parent / 'source' / 'Turoyo_all_2024.html'

    if not html_file.exists():
        print(f"❌ Error: {html_file} not found")
        sys.exit(1)

    parser = TuroyoParser(html_file)
    verbs = parser.parse_all()

    # Save outputs
    output_dir = Path(__file__).parent.parent / 'data'
    parser.save_json(output_dir / 'verbs.json')
    parser.save_error_report(output_dir / 'parsing_errors.json')

    print(f"\n🎉 Done! Extracted {len(verbs)} verb entries")


if __name__ == '__main__':
    main()
