#!/usr/bin/env python3
"""
MASTER TUROYO VERB PARSER
=========================
This is the ONE and ONLY parser script for the Turoyo Verb Glossary.
It does EVERYTHING automatically in one run:
- Parse HTML source
- Extract verbs, stems, conjugations, etymology
- Add homonym numbering for duplicate roots
- Generate tokens with proper spacing (fixes text concatenation)
- Extract lemma headers and stem labels
- Split into individual verb JSON files
- Generate search index
- Generate statistics

Usage: python3 parser/parse_verbs.py

Author: Claude Code
Last Updated: 2025-10-11
"""

import re
import json
import subprocess
import html
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup, Tag, NavigableString


class TuroyoVerbParser:
    """Complete parser for Turoyo verb glossary"""

    def __init__(self, html_path):
        self.html_path = Path(html_path)
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.verbs = []
        self.stats = defaultdict(int)
        self.errors = []

    # ============================================================================
    # SECTION 1: HTML SEGMENTATION
    # ============================================================================

    def split_by_letters(self):
        """Split HTML into letter sections"""
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
        """Extract verb entries from a letter section"""
        # Pattern handles: roots, numbers, variant spellings (e.g., "fhr, fxr")
        # Note: <font> tag is optional (e.g., ʕmr 1 has <p><span>, ʕmr 2 has <p><font><span>)
        root_pattern = r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)?<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(?:\s*\d+)?[^<]*</span>'

        # STEP 1: Collect all valid root matches (filtering out glosses)
        valid_matches = []
        for match in re.finditer(root_pattern, section_html):
            root_chars = match.group(1)

            # FILTER: Skip German glosses (e.g., "speichern;")
            # Glosses end with semicolon and have no etymology/stem markup
            span_content = match.group(0)
            span_text_match = re.search(r'<span[^>]*>([^<]+)</span>', span_content)
            if span_text_match:
                full_span_text = span_text_match.group(1).strip()
                # If the span contains ONLY German text ending with semicolon, skip it
                if ';' in full_span_text and not any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
                    continue

            # Check for root continuation (e.g., ṣyb + r = ṣybr)
            lookahead_cont = section_html[match.end():match.end()+100]
            cont_match = re.search(r'</font><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]+)</span>', lookahead_cont)
            if cont_match:
                root_chars = root_chars + cont_match.group(1)

            # Check for number in span
            full_match = match.group(0)
            number_match = re.search(r'([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})\s*(\d+)', full_match)

            if number_match:
                root = f"{root_chars} {number_match.group(2)}"
            else:
                # Look ahead for number in various formats
                lookahead = section_html[match.end():match.end()+300]

                # Pattern 1: Number in italic span
                italic_num = re.search(r'<i><span[^>]*>\s*(\d+)\s+\(', lookahead)
                if italic_num:
                    root = f"{root_chars} {italic_num.group(1)}"
                else:
                    # Pattern 2: Number in separate span
                    sep_num = re.search(r'<span[^>]*>\s*(\d+)\s*</span>', lookahead, re.DOTALL)
                    if sep_num:
                        root = f"{root_chars} {sep_num.group(1)}"
                    else:
                        # Pattern 3: Superscript homonym marker
                        sup_num = re.search(r'<sup[^>]*>.*?(\d+).*?</sup>', lookahead, re.DOTALL)
                        if sup_num:
                            root = f"{root_chars} {sup_num.group(1)}"
                        else:
                            root = root_chars

            valid_matches.append((root, match))

        # STEP 2: Extract entry HTML using filtered match boundaries
        roots = []
        for i, (root, match) in enumerate(valid_matches):
            start_pos = match.start()
            # Use next VALID match as boundary, not raw pattern search
            end_pos = valid_matches[i+1][1].start() if i+1 < len(valid_matches) else len(section_html)
            entry_html = section_html[start_pos:end_pos]
            roots.append((root, entry_html))

        return roots

    # ============================================================================
    # SECTION 2: TOKEN GENERATION (for display with proper spacing)
    # ============================================================================

    def walk_and_extract(self, element, in_italic=False):
        """
        Walk DOM tree and extract text with italic markers.
        Returns list of (is_italic, text) tuples.

        CRITICAL: Adds spacing after block-level elements to fix text concatenation bug.
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

        # Add spacing after block-level elements
        if element.name in block_elements and result:
            last_italic = result[-1][0] if result else in_italic
            result.append((last_italic, ' '))

        return result

    def html_to_tokens(self, html):
        """Convert HTML to token array with italic markers"""
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        pairs = self.walk_and_extract(soup)
        tokens = []
        for is_italic, text in pairs:
            # Keep tokens if they have content OR if they're a single space (block separator)
            if text and (text.strip() or text == ' '):
                tokens.append({'italic': bool(is_italic), 'text': text})
        return tokens

    # ============================================================================
    # SECTION 3: ETYMOLOGY PARSING
    # ============================================================================

    def normalize_whitespace(self, text):
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def parse_etymology(self, entry_html):
        """Parse etymology with support for multiple sources"""
        etym_pattern = r'\(&lt;\s*(.+?)\s*\)(?:\s*[A-Z<]|$)'
        match = re.search(etym_pattern, entry_html, re.DOTALL)

        if not match:
            return None

        etym_text = match.group(1).strip().rstrip(';').strip()

        # Clean HTML tags
        etym_text = re.sub(r'</span></i></font></font><font[^>]*><font[^>]*><i><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'</span></i></font></font><font[^>]*><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'</span></i></font><font[^>]*><i><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'<[^>]+>', '', etym_text)
        # Decode HTML entities (&lt; → <, &amp; → &, etc.)
        etym_text = html.unescape(etym_text)
        etym_text = self.normalize_whitespace(etym_text)

        # Check for complex etymologies with relationships
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

        # Parse each etymon
        etymons = []
        for part in etymon_parts:
            etymon = self._parse_single_etymon(part)
            if etymon:
                etymons.append(etymon)

        if not etymons:
            return None

        result = {'etymons': etymons}
        if relationship:
            result['relationship'] = relationship

        return result

    def _parse_single_etymon(self, etym_text):
        """Parse a single etymon"""
        # Pattern 1: Full structure with cf.
        structured = re.match(
            r'([A-Za-z.]+)\s+([^\s]+)\s+(?:\([^)]+\)\s+)?cf\.\s+([^:]+):\s*(.+)',
            etym_text, re.DOTALL
        )
        if structured:
            return {
                'source': structured.group(1).strip(),
                'source_root': structured.group(2).strip(),
                'reference': structured.group(3).strip(),
                'meaning': self.normalize_whitespace(structured.group(4)),
            }

        # Pattern 2: Without cf.
        no_cf = re.match(
            r'([A-Za-z.]+)\s+([^\s,]+),\s+([^:]+):\s*(.+)',
            etym_text, re.DOTALL
        )
        if no_cf:
            return {
                'source': no_cf.group(1).strip(),
                'source_root': no_cf.group(2).strip(),
                'reference': no_cf.group(3).strip(),
                'meaning': self.normalize_whitespace(no_cf.group(4)),
            }

        # Pattern 3: Simple format
        simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
        if simple:
            return {
                'source': simple.group(1).strip(),
                'notes': self.normalize_whitespace(simple.group(2)),
            }

        return {'raw': etym_text}

    # ============================================================================
    # SECTION 4: STEM AND CONJUGATION EXTRACTION
    # ============================================================================

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

        # Alternative pattern: stem and forms in same span
        combined_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*([^<]+)</span></b></font>'
        for match in re.finditer(combined_pattern, entry_html):
            if any(s['position'] == match.start() for s in stems):
                continue

            stem_num = match.group(1)
            forms_text = match.group(2).strip()
            if '/' in forms_text or any(c in forms_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
                forms = [f.strip() for f in forms_text.split('/') if f.strip()]
                if forms:
                    stems.append({
                        'stem': stem_num,
                        'forms': forms,
                        'position': match.start()
                    })

        # Fallback pattern
        fallback_pattern = r'<p[^>]*>.*?<span[^>]*>([IVX]+):</span>.*?</p>'
        for match in re.finditer(fallback_pattern, entry_html):
            if any(s['position'] == match.start() for s in stems):
                continue

            stem_num = match.group(1)
            lookahead = entry_html[match.end():match.end()+500]

            forms_match = re.search(r'<i><b><span[^>]*>([^<]+)</span>', lookahead)
            if not forms_match:
                forms_match = re.search(r'<i><span[^>]*>([^<]+)</span>', lookahead)

            if not forms_match:
                lookahead_skip = re.sub(r'<p[^>]*><span[^>]*>Detransitive.*?</p>', '', lookahead, flags=re.DOTALL)
                forms_match = re.search(r'<span[^>]*>([^<]*\/[^<]+)</span>', lookahead_skip)

            if forms_match:
                forms_text = forms_match.group(1).strip().replace('?', '')
                forms = [f.strip() for f in forms_text.split('/') if f.strip() and f != '?']
                if forms:
                    stems.append({
                        'stem': stem_num,
                        'forms': forms,
                        'position': match.start()
                    })

        stems.sort(key=lambda x: x['position'])
        return stems

    def find_detransitive_position(self, entry_html):
        """Find Detransitive section position"""
        detrans_pattern1 = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        match1 = re.search(detrans_pattern1, entry_html)
        if match1:
            return match1.start()

        detrans_pattern2 = r'<p[^>]*><span[^>]*>Detransitive</span></p>'
        match2 = re.search(detrans_pattern2, entry_html)
        if match2:
            return match2.start()

        return None

    def parse_table_cell_examples(self, cell_html):
        """Extract examples from table cell"""
        soup = BeautifulSoup(cell_html, 'html.parser')
        examples = []
        paragraphs = soup.find_all('p')

        for para in paragraphs:
            parts = []
            for element in para.descendants:
                if isinstance(element, Tag):
                    if element.name == 'i':
                        text = element.get_text()
                        if text:
                            parts.append(('turoyo', text))
                    elif element.name == 'span' and not element.find_parent('i'):
                        text = element.get_text().strip()
                        if text and len(text) > 1 and not text.isdigit():
                            parts.append(('translation', text))

            if parts:
                current_example = {
                    'turoyo': [],
                    'translations': [],
                    'references': []
                }

                for typ, text in parts:
                    if typ == 'turoyo':
                        stripped = text.strip()
                        if re.match(r'^[\d;/\s\[\]A-Z]+$', stripped):
                            current_example['references'].append(stripped)
                        else:
                            current_example['turoyo'].append(text)
                    elif typ == 'translation':
                        quotes = re.findall(r'[ʻ\'\"]([^ʼ\'\"]{3,})[ʼ\'\"]', text)
                        if quotes:
                            current_example['translations'].extend(quotes)
                        elif len(text) > 10:
                            current_example['translations'].append(text)

                turoyo_text = ''.join(current_example['turoyo'])
                turoyo_text = re.sub(r'\s+', ' ', turoyo_text).strip()

                example = {
                    'turoyo': turoyo_text,
                    'translations': [t.strip() for t in current_example['translations'] if t.strip()],
                    'references': [r.strip() for r in current_example['references'] if r.strip()]
                }

                if example['turoyo'] or example['translations']:
                    examples.append(example)

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
        """Normalize conjugation headers"""
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

    # ============================================================================
    # SECTION 5: LABEL AND HEADER EXTRACTION (for display tokens)
    # ============================================================================

    def extract_lemma_header_raw(self, fragment_html):
        """Extract the lemma header HTML (between root and first stem)"""
        stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span>'
        stem = re.search(stem_pattern, fragment_html)
        if stem:
            header_html = fragment_html[:stem.start()]
        else:
            table_m = re.search(r'<table', fragment_html)
            header_html = fragment_html[:table_m.start()] if table_m else fragment_html
        return header_html.strip()

    def extract_stem_labels(self, fragment_html):
        """Extract stem label HTML for each stem"""
        stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span>'
        labels = {}
        headers = list(re.finditer(stem_pattern, fragment_html))

        for i, m in enumerate(headers):
            roman = m.group(1)
            start = m.start()
            end_region = headers[i+1].start() if i + 1 < len(headers) else len(fragment_html)
            region = fragment_html[start:end_region]

            table = re.search(r'<table', region)
            end = table.start() if table else len(region)
            label_html = region[:end].strip()
            labels[roman] = label_html

        return labels

    def extract_gloss_html_from_label(self, label_html):
        """Remove forms from label, return only gloss HTML"""
        try:
            soup = BeautifulSoup(label_html, 'html.parser')
            ib = soup.find('i')
            if ib and ib.find('b') and ib.find('span'):
                ib.decompose()
            return str(soup)
        except Exception:
            return ''

    # ============================================================================
    # SECTION 6: MAIN PARSING LOGIC
    # ============================================================================

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

        # Lemma header (with tokens)
        header_html = self.extract_lemma_header_raw(entry_html)
        entry['lemma_header_raw'] = header_html
        entry['lemma_header_tokens'] = self.html_to_tokens(header_html)

        # Find Detransitive position
        detrans_pos = self.find_detransitive_position(entry_html)

        # Stems
        stems = self.parse_stems(entry_html)
        stem_labels = self.extract_stem_labels(entry_html)

        for i, stem in enumerate(stems):
            # Find next boundary
            boundaries = []
            if i+1 < len(stems):
                boundaries.append(stems[i+1]['position'])
            if detrans_pos and detrans_pos > stem['position']:
                if i+1 >= len(stems) or detrans_pos < stems[i+1]['position']:
                    boundaries.append(detrans_pos)
            boundaries.append(len(entry_html))
            next_pos = min(boundaries)

            # Extract tables
            conjugations = self.extract_tables(entry_html, stem['position'], next_pos)

            stem_data = {
                'stem': stem['stem'],
                'forms': stem['forms'],
                'conjugations': conjugations
            }

            # Add label (with tokens)
            roman = stem['stem']
            if roman in stem_labels:
                label_html = stem_labels[roman]
                stem_data['label_raw'] = label_html
                gloss_html = self.extract_gloss_html_from_label(label_html)
                stem_data['label_gloss_tokens'] = self.html_to_tokens(gloss_html)

            entry['stems'].append(stem_data)
            self.stats['stems_parsed'] += 1

        # Detransitive
        if detrans_pos:
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

    # ============================================================================
    # SECTION 7: HOMONYM NUMBERING
    # ============================================================================

    def add_homonym_numbers(self):
        """Add sequential numbers to homonyms with different etymologies"""
        root_groups = defaultdict(list)
        for idx, verb in enumerate(self.verbs):
            root_groups[verb['root']].append((idx, verb))

        numbered_count = 0
        for root, entries in root_groups.items():
            if len(entries) <= 1:
                continue

            # Extract etymology signatures
            etymologies = []
            for idx, verb in entries:
                etym = verb.get('etymology')
                if etym:
                    if 'etymons' in etym and etym['etymons']:
                        first_etymon = etym['etymons'][0]
                        sig = (
                            first_etymon.get('source', ''),
                            first_etymon.get('source_root', ''),
                            first_etymon.get('notes', ''),
                            first_etymon.get('raw', ''),
                            first_etymon.get('reference', '')
                        )
                    else:
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

    # ============================================================================
    # SECTION 8: MAIN EXECUTION
    # ============================================================================

    def parse_all(self):
        """Main parsing pipeline"""
        print("🔄 Parsing Turoyo verb data...")

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

        # Auto-number homonyms
        print("🔍 Checking for homonyms with different etymologies...")
        self.add_homonym_numbers()

        return self.verbs

    def save_json(self, output_path):
        """Save complete verb data"""
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
                    'homonyms_numbered': self.stats.get('homonyms_numbered', 0),
                    'parser_version': '4.0.0-master'
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved: {output_file}")
        print(f"   📊 {total_examples} examples across {self.stats['stems_parsed']} stems")

        if self.errors:
            error_file = output_file.parent / 'parsing_errors.txt'
            with open(error_file, 'w') as f:
                f.write('\n'.join(self.errors))
            print(f"   ⚠️  {len(self.errors)} errors: {error_file}")

    def split_into_files(self):
        """Split verbs into individual JSON files"""
        print("\n🔄 Splitting into individual files...")

        # Define both output directories
        output_dirs = [
            Path('public/appdata/api/verbs'),      # For static client access
            Path('server/assets/appdata/api/verbs') # For Nitro storage API
        ]

        # Create directories and clear existing files
        for output_dir in output_dirs:
            output_dir.mkdir(parents=True, exist_ok=True)
            for f in output_dir.glob('*.json'):
                f.unlink()

        # Write to both locations
        for verb in self.verbs:
            root = verb['root']
            filename = f"{root}.json"

            for output_dir in output_dirs:
                filepath = output_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(verb, f, ensure_ascii=False, indent=2)

        print(f"✅ Created {len(self.verbs)} individual verb files in:")
        for output_dir in output_dirs:
            print(f"   • {output_dir}")

    def generate_search_index(self):
        """Generate search index"""
        print("\n🔄 Generating search index...")
        try:
            result = subprocess.run(
                ['python3', 'parser/generate_search_index.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("✅ Search index generated")
            else:
                print(f"⚠️  Search index generation failed: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Search index generation failed: {e}")

    def generate_stats(self):
        """Generate statistics"""
        print("\n🔄 Generating statistics...")

        # Count by stem type
        stem_counts = defaultdict(int)
        for verb in self.verbs:
            for stem in verb.get('stems', []):
                stem_counts[stem.get('stem', 'Unknown')] += 1

        # Etymology sources
        etym_sources = defaultdict(int)
        for verb in self.verbs:
            etym = verb.get('etymology')
            if etym and 'etymons' in etym:
                for etymon in etym['etymons']:
                    source = etymon.get('source', 'Unknown')
                    etym_sources[source] += 1

        # Count total examples
        total_examples = sum(
            sum(len(conj_data) for conj_data in stem['conjugations'].values())
            for verb in self.verbs
            for stem in verb['stems']
        )

        stats = {
            'total_verbs': len(self.verbs),
            'total_stems': self.stats['stems_parsed'],
            'total_examples': total_examples,
            'stem_counts': dict(stem_counts),
            'etymology_sources': dict(etym_sources),
            'cross_references': self.stats.get('cross_references', 0),
            'uncertain_entries': self.stats.get('uncertain_entries', 0),
            'homonyms': self.stats.get('homonyms_numbered', 0)
        }

        stats_file = Path('public/appdata/api/stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"✅ Statistics saved to {stats_file}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Run the complete parsing pipeline"""
    print("=" * 80)
    print("TUROYO VERB GLOSSARY - MASTER PARSER")
    print("=" * 80)

    parser = TuroyoVerbParser('source/Turoyo_all_2024.html')

    # Step 1: Parse HTML
    parser.parse_all()

    # Step 2: Save complete data
    parser.save_json('data/verbs_final.json')

    # Step 3: Split into individual files
    parser.split_into_files()

    # Step 4: Generate search index
    parser.generate_search_index()

    # Step 5: Generate statistics
    parser.generate_stats()

    print("\n" + "=" * 80)
    print("✅ PARSING COMPLETE!")
    print("=" * 80)
    print(f"📚 Total verbs: {len(parser.verbs)}")
    print(f"📖 Total stems: {parser.stats['stems_parsed']}")
    print(f"🔗 Cross-references: {parser.stats.get('cross_references', 0)}")
    print(f"❓ Uncertain entries: {parser.stats.get('uncertain_entries', 0)}")
    print(f"🔢 Homonyms numbered: {parser.stats.get('homonyms_numbered', 0)}")
    print("=" * 80)


if __name__ == '__main__':
    main()
