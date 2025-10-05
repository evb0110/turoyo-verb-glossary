#!/usr/bin/env python3
"""
Simplified Turoyo Parser - Regex-based approach
Works directly with HTML text to avoid BeautifulSoup parsing issues
"""

import re
import json
from pathlib import Path
from collections import defaultdict

class SimpleTuroyoParser:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.verbs = []
        self.stats = defaultdict(int)
        self.errors = []

    def split_by_letter_sections(self):
        """Split HTML by letter headers (h1 tags)"""
        # Find all <h1> tags with single letters
        letter_pattern = r'<h1[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə])</span></h1>'

        sections = []
        matches = list(re.finditer(letter_pattern, self.html))

        for i, match in enumerate(matches):
            letter = match.group(1)
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(self.html)

            section_html = self.html[start:end]
            sections.append((letter, section_html))

        print(f"📚 Found {len(sections)} letter sections")
        return sections

    def extract_roots_from_section(self, section_html):
        """Extract individual verb entries from a letter section"""
        # Pattern for root entry: root followed by etymology or cross-ref
        # Root is at start of <p class="western">
        root_pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6})</span>'

        roots = []
        for match in re.finditer(root_pattern, section_html):
            root = match.group(1)
            start_pos = match.start()

            # Find next root to determine boundary
            next_match = re.search(root_pattern, section_html[match.end():])
            end_pos = (match.end() + next_match.start()) if next_match else len(section_html)

            entry_html = section_html[start_pos:end_pos]
            roots.append((root, entry_html))

        return roots

    def parse_entry(self, root, entry_html):
        """Parse a single verb entry"""
        entry = {
            'root': root,
            'etymology': None,
            'stems': [],
            'cross_reference': None
        }

        # Check for cross-reference (root → other_root)
        xref_pattern = r'' + root + r'\s*→\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)'
        xref_match = re.search(xref_pattern, entry_html)
        if xref_match:
            entry['cross_reference'] = xref_match.group(1)
            return entry

        # Extract etymology
        etym_pattern = r'\(&lt;\s*([^)]+)\)'
        etym_match = re.search(etym_pattern, entry_html)
        if etym_match:
            entry['etymology'] = etym_match.group(1).strip()

        # Find stem markers (I:, II:, III:)
        stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'

        for stem_match in re.finditer(stem_pattern, entry_html):
            stem_num = stem_match.group(1)
            forms = stem_match.group(2).strip()

            stem = {
                'stem': stem_num,
                'forms': [f.strip() for f in forms.split('/')],
                'conjugations': {}
            }

            # Extract tables after this stem
            # Find tables between this stem and next stem/detransitive
            stem_start = stem_match.end()

            # Find next stem or end
            next_stem = re.search(stem_pattern, entry_html[stem_start:])
            next_detrans = re.search(r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive',
                                      entry_html[stem_start:])

            stem_end = len(entry_html)
            if next_stem and next_detrans:
                stem_end = stem_start + min(next_stem.start(), next_detrans.start())
            elif next_stem:
                stem_end = stem_start + next_stem.start()
            elif next_detrans:
                stem_end = stem_start + next_detrans.start()

            stem_html = entry_html[stem_start:stem_end]

            # Extract tables from this stem
            tables = self.extract_tables(stem_html)
            stem['conjugations'] = tables

            entry['stems'].append(stem)

        # Handle Detransitive
        detrans_pattern = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        if re.search(detrans_pattern, entry_html):
            detrans_match = re.search(detrans_pattern, entry_html)
            detrans_start = detrans_match.end()

            # Find tables in detransitive section
            detrans_html = entry_html[detrans_start:]
            tables = self.extract_tables(detrans_html)

            entry['stems'].append({
                'stem': 'Detransitive',
                'forms': [],
                'conjugations': tables
            })

        return entry

    def extract_tables(self, html_fragment):
        """Extract conjugation tables from HTML fragment"""
        tables = {}

        # Find all tables
        table_pattern = r'<table[^>]*>.*?</table>'

        for table_match in re.finditer(table_pattern, html_fragment, re.DOTALL):
            table_html = table_match.group(0)

            # Extract rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)

            for row in rows:
                # Extract cells
                cell_pattern = r'<td[^>]*>.*?<p[^>]*>\s*(?:<font[^>]*>)?(?:<span[^>]*>)?([^<]+)'
                cells = re.findall(cell_pattern, row, re.DOTALL)

                if len(cells) >= 2:
                    header = cells[0].strip()
                    # Normalize header
                    header = self.normalize_header(header)

                    # Content is everything in second cell
                    content_match = re.search(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                    if content_match:
                        content_html = content_match.group(1)
                        # Strip HTML but keep text
                        content_text = re.sub(r'<[^>]+>', ' ', content_html)
                        content_text = re.sub(r'\s+', ' ', content_text).strip()

                        tables[header] = content_text

        return tables

    def normalize_header(self, header):
        """Normalize table headers"""
        mapping = {
            'Imperativ': 'Imperative',
            'Infinitiv': 'Infinitive',
            'Preterite': 'Preterit',
            'Infectum - wa': 'Infectum-wa',
            'Infectum – wa': 'Infectum-wa',
            ' Infectum': 'Infectum',
            'Part act.': 'Part_Act',
            'Part. act.': 'Part_Act',
            'Part. Pass.': 'Part_Pass',
        }

        header = header.strip()
        return mapping.get(header, header)

    def parse_all(self):
        """Main parsing method"""
        print("🔄 Parsing HTML...")

        sections = self.split_by_letter_sections()

        for letter, section_html in sections:
            print(f"  Processing letter: {letter}...", end='\r')
            roots = self.extract_roots_from_section(section_html)

            for root, entry_html in roots:
                try:
                    entry = self.parse_entry(root, entry_html)
                    self.verbs.append(entry)
                    self.stats['verbs_parsed'] += 1
                except Exception as e:
                    self.errors.append(f"Error parsing {root}: {e}")

        print(f"\n✅ Parsed {self.stats['verbs_parsed']} verb entries")
        return self.verbs

    def save_json(self, output_path):
        """Save to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'verbs': self.verbs,
                'metadata': {
                    'total_verbs': len(self.verbs),
                    'total_stems': sum(len(v['stems']) for v in self.verbs),
                    'source_file': self.html_path.name
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved {len(self.verbs)} verbs to: {output_file}")

        # Also save a sample for inspection
        if self.verbs:
            sample_file = output_file.parent / 'verbs_sample.json'
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(self.verbs[:10], f, ensure_ascii=False, indent=2)
            print(f"📄 Sample (first 10): {sample_file}")

def main():
    html_file = Path('source/Turoyo_all_2024.html')

    parser = SimpleTuroyoParser(html_file)
    verbs = parser.parse_all()

    output_dir = Path('data')
    parser.save_json(output_dir / 'verbs.json')

    if parser.errors:
        print(f"\n⚠️  {len(parser.errors)} errors occurred")
        error_file = output_dir / 'parsing_errors.txt'
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(parser.errors))
        print(f"   Errors saved to: {error_file}")

if __name__ == '__main__':
    main()
