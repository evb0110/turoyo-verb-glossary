#!/usr/bin/env python3
"""
Clean Turoyo Parser - Fixed version
Properly handles word reconstruction and whitespace normalization
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup, NavigableString

class CleanTuroyoParser:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.verbs = []
        self.stats = defaultdict(int)
        self.errors = []
        self.warnings = []

    def normalize_whitespace(self, text):
        """Clean up whitespace: tabs, newlines, multiple spaces"""
        if not text:
            return ""
        # Replace all whitespace sequences with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def clean_reference(self, ref):
        """Clean up reference strings"""
        # Remove trailing punctuation
        ref = ref.rstrip(';:,.')
        # Normalize whitespace
        ref = self.normalize_whitespace(ref)
        return ref if ref else None

    def split_by_letters(self):
        """Split HTML into letter sections"""
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
        """Extract individual verb entries"""
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
                'meaning': self.normalize_whitespace(structured.group(4)),
            }

        # Simple: SOURCE info
        simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
        if simple:
            return {
                'source': simple.group(1).strip(),
                'notes': self.normalize_whitespace(simple.group(2)),
            }

        return {'raw': etym_text}

    def extract_text_segments(self, cell_html):
        """
        Extract text from table cell, separating italic (Turoyo) from regular (translation).
        KEY FIX: Process paragraph as a whole to preserve word boundaries.
        """
        soup = BeautifulSoup(cell_html, 'html.parser')
        segments = []

        # Process each paragraph
        for para in soup.find_all('p'):
            para_segments = []

            # Walk through all children in order
            for element in para.children:
                if isinstance(element, NavigableString):
                    # Direct text node (rare but possible)
                    text = self.normalize_whitespace(str(element))
                    if text:
                        para_segments.append(('regular', text))
                    continue

                # It's a tag - check if it or its descendants have italic
                # Strategy: get all text from this element, then determine if italic
                element_text = element.get_text()
                element_text = self.normalize_whitespace(element_text)

                if not element_text:
                    continue

                # Check if this element contains an <i> tag
                has_italic = element.find('i') is not None

                if has_italic:
                    # This is Turoyo text
                    # Get text from all <i> tags within this element
                    italic_texts = []
                    for i_tag in element.find_all('i'):
                        i_text = i_tag.get_text()
                        i_text = self.normalize_whitespace(i_text)
                        if i_text:
                            italic_texts.append(i_text)

                    if italic_texts:
                        # Join all italic fragments with space
                        combined = ' '.join(italic_texts)
                        para_segments.append(('turoyo', combined))
                else:
                    # Regular text (translation)
                    # Check if it's inside a <span> without <i> parent
                    if element.name == 'font' or element.name == 'span':
                        # Only add if not a child of italic
                        if not element.find_parent('i'):
                            para_segments.append(('regular', element_text))

            segments.extend(para_segments)

        return segments

    def segments_to_examples(self, segments):
        """
        Convert text segments to structured examples.
        Groups consecutive Turoyo and regular text appropriately.
        """
        examples = []
        current = {
            'turoyo': [],
            'translations': [],
            'references': []
        }

        for seg_type, text in segments:
            if seg_type == 'turoyo':
                # Check if this looks like a reference
                # References: numbers, slashes, uppercase abbreviations
                if re.match(r'^[\d;/\s\[\]]+$', text) or re.match(r'^[A-Z]{2,}[\s\d.;]+$', text):
                    # This is a reference
                    ref = self.clean_reference(text)
                    if ref:
                        current['references'].append(ref)
                else:
                    # Actual Turoyo text
                    current['turoyo'].append(text)

            elif seg_type == 'regular':
                # Translation text
                # Extract quoted translations
                quotes = re.findall(r'[ʻ\'"\"]([^ʼ\'"\"]{3,})[ʼ\'"\"]', text)

                if quotes:
                    current['translations'].extend([self.normalize_whitespace(q) for q in quotes])
                elif len(text) > 10:  # Meaningful translation
                    current['translations'].append(text)

        # Build final example
        example = {
            'turoyo': ' '.join(current['turoyo']),
            'translations': [t for t in current['translations'] if t],
            'references': [r for r in current['references'] if r]
        }

        # Only add if has content
        if example['turoyo'] or example['translations']:
            return [example]

        return []

    def parse_table_cell(self, cell_html):
        """Parse table cell to extract examples"""
        segments = self.extract_text_segments(cell_html)
        examples = self.segments_to_examples(segments)

        # Quality check
        for ex in examples:
            # Flag suspicious patterns
            turoyo = ex.get('turoyo', '')

            # Check for unreasonable fragmentation
            if re.search(r'\b[ʔʕḥṭəbdēaioug]\s+[ʔʕḥṭəbdēaioug]\b', turoyo):
                self.warnings.append(f"Suspicious spacing: {turoyo[:50]}")

            # Check for leftover HTML entities
            if '&' in turoyo or '<' in turoyo:
                self.warnings.append(f"HTML entities in text: {turoyo[:50]}")

        return examples

    def extract_tables(self, entry_html, start_pos=0, end_pos=None):
        """Extract all tables in range"""
        if end_pos is None:
            end_pos = len(entry_html)

        fragment = entry_html[start_pos:end_pos]
        table_pattern = r'<table[^>]*>(.*?)</table>'
        tables_data = {}

        for table_match in re.finditer(table_pattern, fragment, re.DOTALL):
            table_html = table_match.group(0)

            # Parse rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)

            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)

                if len(cells) >= 2:
                    # First cell: header
                    header_match = re.search(r'<span[^>]*>([^<]+)</span>', cells[0])
                    if not header_match:
                        continue

                    header = self.normalize_header(header_match.group(1))

                    # Second cell: examples
                    examples = self.parse_table_cell(cells[1])

                    if examples:
                        tables_data[header] = examples

        return tables_data

    def normalize_header(self, header):
        """Normalize conjugation headers"""
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

        header = self.normalize_whitespace(header)
        return mapping.get(header, header)

    def parse_binyanim(self, entry_html):
        """Find all binyan headers"""
        binyan_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'

        binyanim = []
        for match in re.finditer(binyan_pattern, entry_html):
            binyan_num = match.group(1)
            forms_text = match.group(2).strip()
            forms = [self.normalize_whitespace(f) for f in forms_text.split('/') if f.strip()]

            binyanim.append({
                'binyan': binyan_num,
                'forms': forms,
                'position': match.start()
            })

        return binyanim

    def parse_entry(self, root, entry_html):
        """Parse complete verb entry"""
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

        # Binyanim
        binyanim = self.parse_binyanim(entry_html)

        for i, binyan in enumerate(binyanim):
            next_pos = binyanim[i+1]['position'] if i+1 < len(binyanim) else len(entry_html)
            conjugations = self.extract_tables(entry_html, binyan['position'], next_pos)

            entry['stems'].append({
                'binyan': binyan['binyan'],
                'forms': binyan['forms'],
                'conjugations': conjugations
            })

            self.stats['stems_parsed'] += 1

        # Detransitive
        detrans_pattern = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        detrans_match = re.search(detrans_pattern, entry_html)

        if detrans_match:
            conjugations = self.extract_tables(entry_html, detrans_match.end())

            entry['stems'].append({
                'binyan': 'Detransitive',
                'forms': [],
                'conjugations': conjugations
            })

            self.stats['detransitive_entries'] += 1

        return entry

    def parse_all(self):
        """Main parsing"""
        print("🔄 Parsing with clean extraction...")

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

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings (see data/parsing_warnings.txt)")

        return self.verbs

    def save_json(self, output_path):
        """Save clean data"""
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

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
                    'parser_version': '4.0.0-clean',
                    'notes': 'Cleaned whitespace, reconstructed words, normalized references'
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved: {output_file}")
        print(f"   📊 {total_examples} examples across {self.stats['stems_parsed']} stems")

        # Sample
        if self.verbs:
            sample_file = output_file.parent / 'verbs_clean_sample.json'
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(self.verbs[:3], f, ensure_ascii=False, indent=2)
            print(f"   📄 Sample: {sample_file}")

        # Warnings
        if self.warnings:
            warnings_file = output_file.parent / 'parsing_warnings.txt'
            with open(warnings_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.warnings[:100]))  # First 100
            print(f"   ⚠️  Warnings: {warnings_file}")

        # Errors
        if self.errors:
            errors_file = output_file.parent / 'parsing_errors.txt'
            with open(errors_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.errors))
            print(f"   ❌ Errors: {errors_file}")


def main():
    parser = CleanTuroyoParser('source/Turoyo_all_2024.html')
    parser.parse_all()
    parser.save_json('data/verbs_clean.json')

if __name__ == '__main__':
    main()
