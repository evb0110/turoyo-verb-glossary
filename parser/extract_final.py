#!/usr/bin/env python3
"""
Final Complete Turoyo Parser
Uses BeautifulSoup for clean extraction of italic/regular text
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup, Tag, NavigableString

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
        letter_pattern = r'<h1[^>]*>\s*<span[^>]*>(?:&shy;)?([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə])</span></h1>'
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
        # Updated pattern to handle roots with numbers and include 'ž'
        root_pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(?:\s*\d+)?</span>'
        roots = []

        for match in re.finditer(root_pattern, section_html):
            root_chars = match.group(1)

            # Check for root continuation in next span (e.g., ṣyb + r = ṣybr)
            # Pattern: </font><font><span>r</span> (no </span></font> between)
            lookahead_cont = section_html[match.end():match.end()+100]
            cont_match = re.search(r'</font><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]+)</span>', lookahead_cont)
            if cont_match:
                root_chars = root_chars + cont_match.group(1)

            # Check if there's a number inside the span
            full_match = match.group(0)
            number_match = re.search(r'([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})\s*(\d+)', full_match)

            if number_match:
                root = f"{root_chars} {number_match.group(2)}"
            else:
                # Look ahead for number in separate span or italic tag
                lookahead = section_html[match.end():match.end()+300]

                # Pattern 1: Number in italic span (e.g., <i><span>2 (etymology...)</span></i>)
                italic_num = re.search(r'<i><span[^>]*>\s*(\d+)\s+\(', lookahead)
                if italic_num:
                    root = f"{root_chars} {italic_num.group(1)}"
                else:
                    # Pattern 2: Number in separate regular span
                    # Fixed: Don't require </span> at start of lookahead (lookahead starts AFTER first </span>)
                    sep_num = re.search(r'<span[^>]*>\s*(\d+)\s*</span>', lookahead, re.DOTALL)
                    if sep_num:
                        root = f"{root_chars} {sep_num.group(1)}"
                    else:
                        # Pattern 3: Superscript homonym marker
                        # Fixed: Number can be inside nested tags within <sup> (e.g., <sup><span>1</span></sup>)
                        sup_num = re.search(r'<sup[^>]*>.*?(\d+).*?</sup>', lookahead, re.DOTALL)
                        if sup_num:
                            root = f"{root_chars} {sup_num.group(1)}"
                        else:
                            root = root_chars

            start_pos = match.start()

            next_match = re.search(root_pattern, section_html[match.end():])
            end_pos = (match.end() + next_match.start()) if next_match else len(section_html)

            entry_html = section_html[start_pos:end_pos]
            roots.append((root, entry_html))

        return roots

    def normalize_whitespace(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def clean_reference(self, ref: str):
        if ref is None:
            return None
        ref = ref.rstrip(';:,.')
        ref = self.normalize_whitespace(ref)
        return ref if ref else None

    def has_turoyo_chars(self, text: str) -> bool:
        return bool(re.search(r'[ʔʕḥṣṭḏṯẓġǧəǝščž]', text or ''))

    def parse_etymology(self, entry_html):
        """Parse etymology with support for nested parentheses, edge cases, and multiple sources"""
        etym_pattern = r'\(&lt;\s*(.+?)\s*\)(?:\s*[A-Z<]|$)'
        match = re.search(etym_pattern, entry_html, re.DOTALL)

        if not match:
            return None

        etym_text = match.group(1).strip()
        etym_text = etym_text.rstrip(';').strip()

        etym_text = re.sub(r'</span></i></font></font><font[^>]*><font[^>]*><i><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'</span></i></font></font><font[^>]*><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'</span></i></font><font[^>]*><i><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'<[^>]+>', '', etym_text)
        etym_text = self.normalize_whitespace(etym_text)

        # Check for complex etymologies with "also", "or", "and" relationships
        relationship = None
        etymon_parts = [etym_text]

        if ' also ' in etym_text:
            relationship = 'also'
            etymon_parts = [part.strip() for part in etym_text.split(' also ')]
        elif ' or ' in etym_text:
            relationship = 'or'
            etymon_parts = [part.strip() for part in etym_text.split(' or ')]
        elif '; and ' in etym_text or ', and ' in etym_text:
            relationship = 'and'
            etymon_parts = [part.strip() for part in re.split(r'[;,]\s*and\s+', etym_text)]

        # Parse each etymon part
        etymons = []
        for part in etymon_parts:
            etymon = self._parse_single_etymon(part)
            if etymon:
                etymons.append(etymon)

        # Return structured etymology with etymons array
        if not etymons:
            return None

        result = {'etymons': etymons}
        if relationship:
            result['relationship'] = relationship

        return result

    def _parse_single_etymon(self, etym_text):
        """Parse a single etymon (helper for parse_etymology)"""
        structured = re.match(
            r'([A-Za-z.]+)\s+([^\s]+)\s+(?:\([^)]+\)\s+)?cf\.\s+([^:]+):\s*(.+)',
            etym_text,
            re.DOTALL
        )
        if structured:
            return {
                'source': structured.group(1).strip(),
                'source_root': structured.group(2).strip(),
                'reference': structured.group(3).strip(),
                'meaning': self.normalize_whitespace(structured.group(4)),
            }

        no_cf = re.match(
            r'([A-Za-z.]+)\s+([^\s,]+),\s+([^:]+):\s*(.+)',
            etym_text,
            re.DOTALL
        )
        if no_cf:
            return {
                'source': no_cf.group(1).strip(),
                'source_root': no_cf.group(2).strip(),
                'reference': no_cf.group(3).strip(),
                'meaning': self.normalize_whitespace(no_cf.group(4)),
            }

        no_colon = re.match(
            r'([A-Za-z.]+)\s+([^\s]+)\s+(?:\([^)]+\)\s+)?cf\.\s+(.+)',
            etym_text,
            re.DOTALL
        )
        if no_colon:
            ref_part = no_colon.group(3).strip()
            if ':' in ref_part:
                ref, meaning = ref_part.split(':', 1)
                return {
                    'source': no_colon.group(1).strip(),
                    'source_root': no_colon.group(2).strip(),
                    'reference': self.normalize_whitespace(ref),
                    'meaning': self.normalize_whitespace(meaning),
                }
            else:
                return {
                    'source': no_colon.group(1).strip(),
                    'source_root': no_colon.group(2).strip(),
                    'reference': self.normalize_whitespace(ref_part),
                    'meaning': '',
                }

        simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
        if simple:
            return {
                'source': simple.group(1).strip(),
                'notes': self.normalize_whitespace(simple.group(2)),
            }

        return {'raw': etym_text}

    def walk_and_extract(self, element, in_italic=False):
        """
        Walk DOM tree and extract text while tracking italic context.
        Returns list of (is_italic, text) tuples.

        Adds spacing after block-level elements to preserve word boundaries.
        """
        result = []

        # Block-level elements that should add spacing after
        block_elements = {'p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'td'}

        if isinstance(element, NavigableString):
            text = str(element)
            if text.strip():
                result.append((in_italic, text))
            return result

        # Check if this element is or contains <i>
        current_italic = in_italic or (element.name == 'i')

        # Recurse to children
        for child in element.children:
            result.extend(self.walk_and_extract(child, current_italic))

        # Add spacing after block-level elements (unless it's the root being processed)
        if element.name in block_elements and result:
            # Add a space token after this block element, preserving the italic context of the last token
            last_italic = result[-1][0] if result else in_italic
            result.append((last_italic, ' '))

        return result

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
                        # This is Turoyo text - DON'T strip yet to preserve word boundaries
                        text = element.get_text()
                        if text:  # Include even whitespace-only elements for spacing
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
                        stripped = text.strip()
                        if re.match(r'^[\d;/\s\[\]A-Z]+$', stripped):
                            current_example['references'].append(stripped)
                        else:
                            current_example['turoyo'].append(text)
                    elif typ == 'translation':
                        # Extract quoted translations
                        quotes = re.findall(r'[ʻ\'\"]([^ʼ\'\"]{3,})[ʼ\'\"]', text)
                        if quotes:
                            current_example['translations'].extend(quotes)
                        elif len(text) > 10:  # Long enough to be meaningful
                            current_example['translations'].append(text)

                # Clean up - join without adding spaces, then normalize whitespace
                turoyo_text = ''.join(current_example['turoyo'])
                # Normalize: collapse multiple whitespace chars into single space
                turoyo_text = re.sub(r'\s+', ' ', turoyo_text).strip()

                example = {
                    'turoyo': turoyo_text,
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
                    header_match = re.search(r'<span[^>]*>([^<]+)</span>', cells[0])
                    if not header_match:
                        continue

                    headers = self.normalize_header(header_match.group(1).strip())

                    examples = self.parse_table_cell_examples(cells[1])

                    if examples:
                        for h in headers:
                            if h in tables_data:
                                tables_data[h].extend(examples)
                            else:
                                tables_data[h] = examples[:]

        return tables_data

    def normalize_header(self, header):
        """Normalize headers and return list (supports multi-headers like 'Infectum and Infectum-wa')"""
        h = self.normalize_whitespace(header)
        mapping = {
            'Imperativ': 'Imperative',
            'Infinitiv': 'Infinitive',
            'Preterite': 'Preterit',
            'Preterit 1': 'Preterit 1',
            'Preterit 2': 'Preterit 2',
            'k-Preterit': 'k-Preterit',
            'ko-Preterit': 'ko-Preterit',
            ' Infectum': 'Infectum',
            'Infectum - wa': 'Infectum-wa',
            'Infectum – wa': 'Infectum-wa',
            'Infectum – Transitive': 'Infectum-Transitive',
            'Detransitive infectum': 'Detransitive Infectum',
            'Part act.': 'Participle_Active',
            'Part. act.': 'Participle_Active',
            'Part. Act.': 'Participle_Active',
            'Part act': 'Participle_Active',
            'Part pass.': 'Participle_Passive',
            'Part. pass.': 'Participle_Passive',
            'Part. Pass.': 'Participle_Passive',
            'Part.Pass': 'Participle_Passive',
            'Pass. Part.': 'Participle_Passive',
            'Passive Part.': 'Participle_Passive',
            'Part': 'Participle',
            'Participle': 'Participle',
            'Nomen Patiens': 'Nomen Patiens',
            'Nomen Patientis?': 'Nomen Patiens',
            'Nomen Actionis': 'Nomen Actionis',
            'Nomen agentis': 'Nomen agentis',
        }
        h = mapping.get(h, h)
        if ' and ' in h:
            parts = [mapping.get(p.strip(), p.strip()) for p in h.split(' and ') if p.strip()]
            return parts
        return [h]

    def parse_stems(self, entry_html):
        """Find all stem headers"""
        # Primary pattern: standard bold, large font
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

        # Alternative primary pattern: stem and forms in SAME bold span
        # e.g., <span>II:\nmṣaybarle/mṣaybar </span>
        combined_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*([^<]+)</span></b></font>'
        for match in re.finditer(combined_pattern, entry_html):
            # Check if already captured
            if any(s['position'] == match.start() for s in stems):
                continue

            stem_num = match.group(1)
            forms_text = match.group(2).strip()
            # Only process if it looks like forms (contains slash or Turoyo chars)
            if '/' in forms_text or any(c in forms_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
                forms = [f.strip() for f in forms_text.split('/') if f.strip()]
                if forms:
                    stems.append({
                        'stem': stem_num,
                        'forms': forms,
                        'position': match.start()
                    })

        # Fallback pattern: simple format without bold/large font
        # Handles cases like: <p><span>II:</span></p> followed by forms
        fallback_pattern = r'<p[^>]*>.*?<span[^>]*>([IVX]+):</span>.*?</p>'

        for match in re.finditer(fallback_pattern, entry_html):
            stem_num = match.group(1)

            # Check if this position is already captured by primary pattern
            if any(s['position'] == match.start() for s in stems):
                continue

            # Look ahead for forms in next tags
            lookahead = entry_html[match.end():match.end()+500]

            # Try to find italic forms
            forms_match = re.search(r'<i><b><span[^>]*>([^<]+)</span>', lookahead)
            if not forms_match:
                # Try alternative format
                forms_match = re.search(r'<i><span[^>]*>([^<]+)</span>', lookahead)

            if not forms_match:
                # Try plain span with slash (very non-standard format)
                # Skip past Detransitive marker if present
                lookahead_skip = re.sub(r'<p[^>]*><span[^>]*>Detransitive.*?</p>', '', lookahead, flags=re.DOTALL)
                forms_match = re.search(r'<span[^>]*>([^<]*\/[^<]+)</span>', lookahead_skip)

            if forms_match:
                forms_text = forms_match.group(1).strip()
                # Filter out "?" markers
                forms_text = forms_text.replace('?', '').replace('/', '/').strip()
                forms = [f.strip() for f in forms_text.split('/') if f.strip() and f != '?']

                if forms:  # Only add if we found actual forms
                    stems.append({
                        'stem': stem_num,
                        'forms': forms,
                        'position': match.start()
                    })

        # Sort by position to maintain order
        stems.sort(key=lambda x: x['position'])

        return stems

    def find_detransitive_position(self, entry_html):
        """Find Detransitive section position (handles both formats)"""
        # Format 1: Bold, large font (rare)
        detrans_pattern1 = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        match1 = re.search(detrans_pattern1, entry_html)
        if match1:
            return match1.start()

        # Format 2: Simple format (common)
        detrans_pattern2 = r'<p[^>]*><span[^>]*>Detransitive</span></p>'
        match2 = re.search(detrans_pattern2, entry_html)
        if match2:
            return match2.start()

        return None

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

        # Find Detransitive position (if any) to use as boundary
        detrans_pos = self.find_detransitive_position(entry_html)

        # Stems
        stems = self.parse_stems(entry_html)

        for i, stem in enumerate(stems):
            # Find next boundary: next stem, or Detransitive, or end of entry
            boundaries = []

            # Add next stem position
            if i+1 < len(stems):
                boundaries.append(stems[i+1]['position'])

            # Add Detransitive position if it's after current stem and before next stem
            if detrans_pos and detrans_pos > stem['position']:
                if i+1 >= len(stems) or detrans_pos < stems[i+1]['position']:
                    boundaries.append(detrans_pos)

            # Add end of entry
            boundaries.append(len(entry_html))

            # Use the earliest boundary
            next_pos = min(boundaries)

            # Extract tables for this stem
            conjugations = self.extract_tables(entry_html, stem['position'], next_pos)

            entry['stems'].append({
                'stem': stem['stem'],
                'forms': stem['forms'],
                'conjugations': conjugations
            })

            self.stats['stems_parsed'] += 1

        # Detransitive (extract tables after its position)
        if detrans_pos:
            # Find next stem after Detransitive (if any)
            next_stem_pos = None
            for stem in stems:
                if stem['position'] > detrans_pos:
                    if next_stem_pos is None or stem['position'] < next_stem_pos:
                        next_stem_pos = stem['position']

            end_pos = next_stem_pos if next_stem_pos else len(entry_html)
            conjugations = self.extract_tables(entry_html, detrans_pos, end_pos)

            entry['stems'].append({
                'stem': 'Detransitive',
                'forms': [],
                'conjugations': conjugations
            })

            self.stats['detransitive_entries'] += 1

        return entry

    def add_homonym_numbers(self):
        """Add sequential numbers to homonyms with different etymologies"""
        # Group by root
        root_groups = defaultdict(list)
        for idx, verb in enumerate(self.verbs):
            root_groups[verb['root']].append((idx, verb))

        # Process duplicates
        numbered_count = 0
        for root, entries in root_groups.items():
            if len(entries) <= 1:
                continue

            # Extract comparable etymology signatures
            etymologies = []
            for idx, verb in entries:
                etym = verb.get('etymology')
                if etym:
                    # Handle new structure with etymons array
                    if 'etymons' in etym and etym['etymons']:
                        # Extract signature from first etymon in array
                        first_etymon = etym['etymons'][0]
                        sig = (
                            first_etymon.get('source', ''),
                            first_etymon.get('source_root', ''),
                            first_etymon.get('notes', ''),
                            first_etymon.get('raw', ''),
                            first_etymon.get('reference', '')
                        )
                    else:
                        # Fallback for legacy flat structure (shouldn't happen with new parser)
                        sig = (
                            etym.get('source', ''),
                            etym.get('source_root', ''),
                            etym.get('notes', ''),
                            etym.get('raw', ''),
                            etym.get('reference', '')
                        )
                else:
                    sig = None
                etymologies.append((idx, sig))

            # Check if etymologies differ
            unique_etyms = set(sig for _, sig in etymologies)

            # Only number if there are DIFFERENT etymologies
            # This ensures we're not hallucinating - we only number genuine homonyms
            if len(unique_etyms) > 1:
                print(f"   ℹ️  Found homonyms for '{root}' with {len(unique_etyms)} different etymologies")
                for entry_num, (idx, sig) in enumerate(etymologies, 1):
                    old_root = self.verbs[idx]['root']
                    self.verbs[idx]['root'] = f"{root} {entry_num}"
                    print(f"      {old_root} → {self.verbs[idx]['root']} (etymology: {sig[0] if sig else 'None'})")
                numbered_count += len(entries)

        if numbered_count > 0:
            self.stats['homonyms_numbered'] = numbered_count
            print(f"   ✅ Auto-numbered {numbered_count} homonym entries")

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

        # Auto-number homonyms with different etymologies
        print("🔍 Checking for homonyms with different etymologies...")
        self.add_homonym_numbers()

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
