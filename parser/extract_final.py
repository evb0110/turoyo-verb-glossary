#!/usr/bin/env python3
"""
Final Complete Turoyo Parser
Uses BeautifulSoup for clean extraction of italic/regular text
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup, Tag

class FinalTuroyoParser:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.verbs = []
        self.stats = defaultdict(int)
        self.errors = []

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
        """Extract verb entries"""
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
        """Parse etymology"""
        etym_pattern = r'\(&lt;\s*([^)]{1,300})\)'
        match = re.search(etym_pattern, entry_html)

        if not match:
            return None

        etym_text = match.group(1).strip()

        # Structured: SOURCE root cf. REF: meaning
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
            }

        # Simple: SOURCE info
        simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
        if simple:
            return {
                'source': simple.group(1).strip(),
                'notes': simple.group(2).strip(),
            }

        return {'raw': etym_text}

    def parse_table_cell_examples(self, cell_html):
        """Extract examples from table cell using BeautifulSoup"""
        soup = BeautifulSoup(cell_html, 'html.parser')

        examples = []

        # Find all <p> tags in the cell
        paragraphs = soup.find_all('p')

        for para in paragraphs:
            # Collect italic and regular spans
            parts = []

            for element in para.descendants:
                if isinstance(element, Tag):
                    if element.name == 'i':
                        # This is Turoyo text
                        text = element.get_text().strip()
                        if text:
                            parts.append(('turoyo', text))

                    elif element.name == 'span' and not element.find_parent('i'):
                        # Regular text (translation)
                        text = element.get_text().strip()
                        # Filter out empty or single chars
                        if text and len(text) > 1 and not text.isdigit():
                            parts.append(('translation', text))

            # Group parts into examples
            if parts:
                current_example = {
                    'turoyo': [],
                    'translations': [],
                    'references': []
                }

                for typ, text in parts:
                    if typ == 'turoyo':
                        # Check if this is a reference (numbers and slashes)
                        if re.match(r'^[\d;/\s\[\]A-Z]+$', text):
                            current_example['references'].append(text)
                        else:
                            current_example['turoyo'].append(text)
                    elif typ == 'translation':
                        # Extract quoted translations
                        quotes = re.findall(r'[ʻ\'\"]([^ʼ\'\"]{3,})[ʼ\'\"]', text)
                        if quotes:
                            current_example['translations'].extend(quotes)
                        elif len(text) > 10:  # Long enough to be meaningful
                            current_example['translations'].append(text)

                # Clean up
                example = {
                    'turoyo': ' '.join(current_example['turoyo']).strip(),
                    'translations': [t.strip() for t in current_example['translations'] if t.strip()],
                    'references': [r.strip() for r in current_example['references'] if r.strip()]
                }

                if example['turoyo'] or example['translations']:
                    examples.append(example)

        return examples if examples else []

    def extract_tables(self, entry_html, start_pos=0, end_pos=None):
        """Extract all tables in range"""
        if end_pos is None:
            end_pos = len(entry_html)

        fragment = entry_html[start_pos:end_pos]

        table_pattern = r'<table[^>]*>(.*?)</table>'
        tables_data = {}

        for table_match in re.finditer(table_pattern, fragment, re.DOTALL):
            table_html = table_match.group(0)

            # Parse table rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)

            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)

                if len(cells) >= 2:
                    # First cell: header
                    header_match = re.search(r'<span[^>]*>([^<]+)</span>', cells[0])
                    if not header_match:
                        continue

                    header = self.normalize_header(header_match.group(1).strip())

                    # Second cell: examples
                    examples = self.parse_table_cell_examples(cells[1])

                    if examples:
                        tables_data[header] = examples

        return tables_data

    def normalize_header(self, header):
        """Normalize headers"""
        mapping = {
            'Imperativ': 'Imperative',
            'Infinitiv': 'Infinitive',
            'Preterite': 'Preterit',
            ' Infectum': 'Infectum',
            'Infectum - wa': 'Infectum-wa',
            'Infectum – wa': 'Infectum-wa',
            'Part act.': 'Participle_Active',
            'Part. act.': 'Participle_Active',
            'Part. Act.': 'Participle_Active',
            'Part pass.': 'Participle_Passive',
            'Part. pass.': 'Participle_Passive',
            'Part. Pass.': 'Participle_Passive',
            'Part.Pass': 'Participle_Passive',
        }

        return mapping.get(header.strip(), header.strip())

    def parse_stems(self, entry_html):
        """Find all stem headers"""
        stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'

        stems = []
        for match in re.finditer(stem_pattern, entry_html):
            stem_num = match.group(1)
            forms_text = match.group(2).strip()
            forms = [f.strip() for f in forms_text.split('/') if f.strip()]

            stems.append({
                'stem': stem_num,
                'forms': forms,
                'position': match.start()
            })

        return stems

    def parse_entry(self, root, entry_html):
        """Parse complete entry"""
        entry = {
            'root': root,
            'etymology': None,
            'cross_reference': None,
            'stems': [],
            'uncertain': False
        }

        # Cross-reference?
        xref_pattern = root + r'\s*→\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)'
        xref = re.search(xref_pattern, entry_html)
        if xref:
            entry['cross_reference'] = xref.group(1)
            self.stats['cross_references'] += 1
            return entry

        # Uncertain?
        if '???' in entry_html:
            entry['uncertain'] = True
            self.stats['uncertain_entries'] += 1

        # Etymology
        entry['etymology'] = self.parse_etymology(entry_html)

        # Stems
        stems = self.parse_stems(entry_html)

        for i, stem in enumerate(stems):
            # Find next stem position
            next_pos = stems[i+1]['position'] if i+1 < len(stems) else len(entry_html)

            # Extract tables for this stem
            conjugations = self.extract_tables(entry_html, stem['position'], next_pos)

            entry['stems'].append({
                'stem': stem['stem'],
                'forms': stem['forms'],
                'conjugations': conjugations
            })

            self.stats['stems_parsed'] += 1

        # Detransitive
        detrans_pattern = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        detrans_match = re.search(detrans_pattern, entry_html)

        if detrans_match:
            conjugations = self.extract_tables(entry_html, detrans_match.end())

            entry['stems'].append({
                'stem': 'Detransitive',
                'forms': [],
                'conjugations': conjugations
            })

            self.stats['detransitive_entries'] += 1

        return entry

    def parse_all(self):
        """Main parsing"""
        print("🔄 Parsing complete verb data...")

        sections = self.split_by_letters()

        for idx, (letter, section_html) in enumerate(sections, 1):
            print(f"  [{idx}/{len(sections)}] {letter}...", end='\r')

            roots = self.extract_roots_from_section(section_html)

            for root, entry_html in roots:
                try:
                    entry = self.parse_entry(root, entry_html)
                    self.verbs.append(entry)
                    self.stats['verbs_parsed'] += 1
                except Exception as e:
                    self.errors.append(f"{root}: {e}")
                    self.stats['errors'] += 1

        print(f"\n✅ Parsed {self.stats['verbs_parsed']} verbs, {self.stats['stems_parsed']} stems")
        return self.verbs

    def save_json(self, output_path):
        """Save data"""
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        # Count examples
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
                    'cross_references': self.stats.get('cross_references', 0),
                    'uncertain_entries': self.stats.get('uncertain_entries', 0),
                    'parser_version': '3.0.0-final'
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved: {output_file}")
        print(f"   📊 {total_examples} examples across {self.stats['stems_parsed']} stems")

        # Sample
        if self.verbs:
            sample_file = output_file.parent / 'verbs_final_sample.json'
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(self.verbs[:3], f, ensure_ascii=False, indent=2)
            print(f"   📄 Sample: {sample_file}")

        if self.errors:
            error_file = output_file.parent / 'parsing_errors.txt'
            with open(error_file, 'w') as f:
                f.write('\n'.join(self.errors))
            print(f"   ⚠️  {len(self.errors)} errors: {error_file}")


def main():
    parser = FinalTuroyoParser('source/Turoyo_all_2024.html')
    parser.parse_all()
    parser.save_json('data/verbs_final.json')

if __name__ == '__main__':
    main()
