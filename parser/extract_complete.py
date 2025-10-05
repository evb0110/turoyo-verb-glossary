#!/usr/bin/env python3
"""
Complete Turoyo Parser - Extracts EVERYTHING
Parses all examples, translations, references, meanings
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

class CompleteTuroyoParser:
    """Extract all data from Turoyo HTML"""

    def __init__(self, html_path):
        self.html_path = Path(html_path)
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.verbs = []
        self.stats = defaultdict(int)
        self.errors = []
        self.warnings = []

    def split_by_letters(self):
        """Split into letter sections"""
        letter_pattern = r'<h1[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə])</span></h1>'
        matches = list(re.finditer(letter_pattern, self.html))

        sections = []
        for i, match in enumerate(matches):
            letter = match.group(1)
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(self.html)
            sections.append((letter, self.html[start:end]))

        return sections

    def extract_roots_from_section(self, section_html):
        """Extract verb entries from section"""
        root_pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6})</span>'
        roots = []

        for match in re.finditer(root_pattern, section_html):
            root = match.group(1)
            start_pos = match.start()

            next_match = re.search(root_pattern, section_html[match.end():])
            end_pos = (match.end() + next_match.start()) if next_match else len(section_html)

            entry_html = section_html[start_pos:end_pos]
            roots.append((root, entry_html))

        return roots

    def parse_etymology(self, entry_html):
        """Parse etymology with all details"""
        etym_pattern = r'\(&lt;\s*([^)]{1,200})\)'
        match = re.search(etym_pattern, entry_html)

        if not match:
            return None

        etym_text = match.group(1).strip()

        # Try to parse structured etymology: SOURCE root cf. REF: meaning
        structured = re.match(
            r'([A-Za-z.]+)\s+([^\s]+)\s+cf\.\s+([^:]+):\s*(.+)',
            etym_text
        )

        if structured:
            return {
                'source': structured.group(1).strip(),
                'source_root': structured.group(2).strip(),
                'reference': structured.group(3).strip(),
                'meaning': structured.group(4).strip(),
                'raw': etym_text
            }

        # Simpler pattern: SOURCE info
        simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
        if simple:
            return {
                'source': simple.group(1).strip(),
                'notes': simple.group(2).strip(),
                'raw': etym_text
            }

        return {'raw': etym_text}

    def parse_meanings(self, text):
        """Extract meanings from text after stem header"""
        # Pattern: "1) meaning; 2) other meaning; 3) third meaning"
        meanings = []

        # Split by numbered patterns
        parts = re.split(r'(?:^|\s)(\d+)\)\s*', text)

        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                meaning = parts[i+1].strip(' ;')
                if meaning and len(meaning) < 500:  # Sanity check
                    meanings.append(meaning)

        return meanings

    def parse_table_cell_content(self, cell_html) -> List[Dict]:
        """Parse examples from table cell with full structure"""
        examples = []

        # Remove outer <td> and <p> tags but keep inner structure
        cell_text = cell_html

        # Split by <p> tags (sub-sections within cell)
        paragraphs = re.split(r'<p[^>]*>', cell_html)

        for para in paragraphs:
            if not para.strip():
                continue

            # Check if paragraph starts with a number (numbered sub-section)
            numbered_match = re.match(r'^\s*<font[^>]*>\s*<i>\s*<span[^>]*>\s*(\d+)\)', para)
            subsection_num = numbered_match.group(1) if numbered_match else None

            # Extract all italic spans (Turoyo examples)
            italic_pattern = r'<i>\s*<span[^>]*>([^<]+)</span>\s*</i>'
            turoyo_parts = re.findall(italic_pattern, para)
            turoyo_text = ' '.join(turoyo_parts).strip()

            # Extract all non-italic spans (translations)
            # Translations are usually in regular font, often in quotes
            regular_pattern = r'<font[^>]*>(?!</i>)<span[^>]*>([^<]+)</span></font>'
            translation_parts = re.findall(regular_pattern, para)
            translation_text = ' '.join(translation_parts).strip()

            # Extract quotes (ʻ...ʼ or '...' or "...")
            quote_patterns = [
                r'ʻ([^ʼ]+)ʼ',
                r'\'([^\']+)\'',
                r'"([^"]+)"'
            ]

            translations = []
            for pattern in quote_patterns:
                matches = re.findall(pattern, para)
                translations.extend(matches)

            # Extract references (e.g., "731; 24/51", "MM 27", "JL 9.9.4")
            ref_pattern = r'(\d+(?:/\d+)?(?:;\s*\d+/\d+)*|[A-Z]{2,}\s+\d+(?:\.\d+)*(?:;\s*\d+/\d+)*|\[?[A-Z]{2}\]?)'
            references = re.findall(ref_pattern, para)
            # Clean up references
            references = [r.strip('; ') for r in references if r and len(r) < 30]

            if turoyo_text or translations:
                example = {
                    'subsection': subsection_num,
                    'turoyo': turoyo_text if turoyo_text else None,
                    'translations': translations if translations else [],
                    'references': references if references else [],
                    'raw_html': para[:500]  # Keep first 500 chars for debugging
                }

                examples.append(example)

        return examples

    def extract_table_data(self, table_html):
        """Extract complete table data with examples"""
        table_data = {}

        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table_html, re.DOTALL)

        for row in rows:
            # Extract both cells
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)

            if len(cells) >= 2:
                # First cell: header
                header_match = re.search(r'<span[^>]*>([^<]+)</span>', cells[0])
                if not header_match:
                    continue

                header = self.normalize_header(header_match.group(1).strip())

                # Second cell: content with examples
                examples = self.parse_table_cell_content(cells[1])

                table_data[header] = examples

        return table_data

    def normalize_header(self, header):
        """Normalize table headers"""
        mapping = {
            'Imperativ': 'Imperative',
            '    Imperativ': 'Imperative',
            'Infinitiv': 'Infinitive',
            '   Infinitive': 'Infinitive',
            'Preterite': 'Preterit',
            '     Preterite': 'Preterit',
            '     Preterit': 'Preterit',
            'k-Preterit': 'ko-Preterit',
            ' Infectum': 'Infectum',
            ' Infectum-wa': 'Infectum-wa',
            'Infectum - wa': 'Infectum-wa',
            'Infectum – wa': 'Infectum-wa',
            'Infectum (???)': 'Infectum_uncertain',
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
        }

        header = header.strip()
        return mapping.get(header, header)

    def parse_stem_header(self, entry_html):
        """Extract stem info with forms and meanings"""
        stems = []

        # Pattern for stem headers
        stem_pattern = r'<p[^>]*><font[^>]*><font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span></b></i></font></font>(?:</p>\s*<p[^>]*><span[^>]*>)?(.*?)?(?=</p>)'

        matches = list(re.finditer(stem_pattern, entry_html, re.DOTALL))

        for match in matches:
            stem_num = match.group(1)
            forms_text = match.group(2).strip()
            meanings_text = match.group(3) if match.group(3) else ""

            forms = [f.strip() for f in forms_text.split('/') if f.strip()]

            # Extract meanings if present
            meanings = self.parse_meanings(meanings_text) if meanings_text else []

            stems.append({
                'stem': stem_num,
                'forms': forms,
                'meanings': meanings,
                'position': match.start()
            })

        return stems

    def parse_entry(self, root, entry_html):
        """Parse complete verb entry"""
        entry = {
            'root': root,
            'etymology': None,
            'cross_reference': None,
            'notes': [],
            'stems': [],
            'uncertain': False
        }

        # Check for cross-reference
        xref_pattern = root + r'\s*→\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)'
        xref = re.search(xref_pattern, entry_html)
        if xref:
            entry['cross_reference'] = xref.group(1)
            self.stats['cross_references'] += 1
            return entry

        # Check for ??? (uncertain)
        if '???' in entry_html:
            entry['uncertain'] = True
            self.stats['uncertain_entries'] += 1

        # Parse etymology
        entry['etymology'] = self.parse_etymology(entry_html)

        # Find all stemim
        stems = self.parse_stem_header(entry_html)

        # Extract tables for each stem
        tables = list(re.finditer(r'<table[^>]*>(.*?)</table>', entry_html, re.DOTALL))

        for stem in stems:
            # Find tables between this stem and next one
            start_pos = stem['position']

            # Find next stem position or end
            next_positions = [b['position'] for b in stems if b['position'] > start_pos]
            end_pos = min(next_positions) if next_positions else len(entry_html)

            # Find tables in this range
            stem_tables = {}
            for table_match in tables:
                if start_pos < table_match.start() < end_pos:
                    table_data = self.extract_table_data(table_match.group(0))
                    stem_tables.update(table_data)

            stem = {
                'stem': stem['stem'],
                'forms': stem['forms'],
                'meanings': stem['meanings'],
                'conjugations': stem_tables
            }

            entry['stems'].append(stem)
            self.stats['stems_parsed'] += 1

        # Handle Detransitive
        detrans_pattern = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        if re.search(detrans_pattern, entry_html):
            detrans_match = re.search(detrans_pattern, entry_html)
            detrans_start = detrans_match.end()

            detrans_tables = {}
            for table_match in tables:
                if table_match.start() > detrans_start:
                    table_data = self.extract_table_data(table_match.group(0))
                    detrans_tables.update(table_data)

            entry['stems'].append({
                'stem': 'Detransitive',
                'forms': [],
                'meanings': [],
                'conjugations': detrans_tables
            })

            self.stats['detransitive_entries'] += 1

        return entry

    def parse_all(self):
        """Main parsing"""
        print("🔄 Parsing all verb data...")

        sections = self.split_by_letters()
        total_sections = len(sections)

        for idx, (letter, section_html) in enumerate(sections, 1):
            print(f"  [{idx}/{total_sections}] {letter}...", end='\r')

            roots = self.extract_roots_from_section(section_html)

            for root, entry_html in roots:
                try:
                    entry = self.parse_entry(root, entry_html)
                    self.verbs.append(entry)
                    self.stats['verbs_parsed'] += 1
                except Exception as e:
                    self.errors.append(f"Error parsing {root}: {e}")
                    self.stats['errors'] += 1

        print(f"\n✅ Parsed {self.stats['verbs_parsed']} verbs, {self.stats['stems_parsed']} stems")
        return self.verbs

    def save_json(self, output_path):
        """Save complete data"""
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        # Calculate stats
        total_examples = sum(
            sum(len(conj_data) for conj_data in stem['conjugations'].values())
            for verb in self.verbs
            for stem in verb['stems']
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'verbs': self.verbs,
                'metadata': {
                    'total_verbs': len(self.verbs),
                    'total_stems': self.stats['stems_parsed'],
                    'total_examples': total_examples,
                    'cross_references': self.stats['cross_references'],
                    'uncertain_entries': self.stats['uncertain_entries'],
                    'detransitive_entries': self.stats['detransitive_entries'],
                    'source_file': self.html_path.name,
                    'parser_version': '2.0.0'
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Complete data: {output_file}")
        print(f"   {total_examples} total examples extracted")

        # Save sample
        if self.verbs:
            sample_file = output_file.parent / 'verbs_complete_sample.json'
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(self.verbs[:5], f, ensure_ascii=False, indent=2)
            print(f"📄 Sample: {sample_file}")

    def print_stats(self):
        """Print parsing statistics"""
        print("\n" + "="*60)
        print("PARSING STATISTICS")
        print("="*60)
        for key, value in sorted(self.stats.items()):
            print(f"  {key}: {value}")

        if self.errors:
            print(f"\n⚠️  Errors: {len(self.errors)}")
            error_file = Path('data/parsing_errors.txt')
            with open(error_file, 'w') as f:
                f.write('\n'.join(self.errors))
            print(f"   Saved to: {error_file}")


def main():
    html_file = Path('source/Turoyo_all_2024.html')

    parser = CompleteTuroyoParser(html_file)
    verbs = parser.parse_all()

    output_dir = Path('data')
    parser.save_json(output_dir / 'verbs_complete.json')
    parser.print_stats()

if __name__ == '__main__':
    main()
