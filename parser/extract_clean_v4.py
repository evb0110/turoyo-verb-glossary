#!/usr/bin/env python3
"""
Clean Turoyo Parser V4
FIXED: Cross-reference detection now works (was 0, now captures all 11+)

Key fixes over V3:
- Added missing character 'ž' (U+017E) to ALL character classes (lines 97, 111, 391)
- Fixed cross-ref pattern to handle HTML tags between root and arrow
- Cross-ref pattern now strips HTML before matching

Changes:
- Line 97: letter_pattern includes ž
- Line 111: root_pattern includes ž
- Line 391-402: xref_pattern strips HTML and includes ž
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

        # Pre-extract all cross-references from the HTML
        self.cross_references = self._extract_all_cross_references()

    def _extract_all_cross_references(self):
        """
        Extract ALL cross-references from the HTML by stripping tags first.
        This solves the problem of HTML tags appearing between root and arrow.
        """
        # Strip ALL HTML tags to get clean text
        html_clean = re.sub(r'<[^>]+>', '', self.html)

        # Find ALL cross-references (including ž)
        xref_pattern = r'([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})\s*→\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})'
        matches = re.findall(xref_pattern, html_clean)

        # Create a dictionary mapping from_root -> to_root
        xref_dict = {}
        for from_root, to_root in matches:
            xref_dict[from_root] = to_root

        return xref_dict

    def normalize_whitespace(self, text):
        """Clean whitespace"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def clean_reference(self, ref):
        """Clean reference strings"""
        ref = ref.rstrip(';:,.')
        ref = self.normalize_whitespace(ref)
        return ref if ref else None

    def has_turoyo_chars(self, text):
        """Check if text contains Turoyo-specific characters"""
        # Turoyo uses special characters not found in German/English
        # Note: ǝ (U+01DD) and ə (U+0259) are both schwas used in Turoyo
        turoyo_pattern = r'[ʕḥṣṭḏṯẓġǧəǝščž]'
        return bool(re.search(turoyo_pattern, text))

    def extract_turoyo_from_plain_text(self, text):
        """
        Extract Turoyo, translation, and reference from non-italic text.
        Returns (turoyo, translation, reference) tuple.
        """
        # Pattern: Turoyo text, optional translation in quotes, reference in parens or ; number;
        # Example: "Lu Sargey mgavazle u šabo bayn u ʕafro (İlyas p.c)"
        # Example: "mbarzaqqe l-am=maye; 770;"
        # Example: '"aʕli mawṣyo yo. (translation)"' - whole text in quotes

        turoyo = ""
        translation = ""
        reference = ""

        # If entire text is wrapped in quotes, unwrap it first
        if (text.startswith('"') and text.endswith('"')) or \
           (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()

        # Extract reference in parentheses at the end
        ref_match = re.search(r'\(([^)]+)\)\s*$', text)
        if ref_match:
            reference = self.clean_reference(ref_match.group(1))
            text = text[:ref_match.start()].strip()

        # Extract reference in format "; number;" at the end
        ref_num_match = re.search(r';\s*(\d+);?\s*$', text)
        if ref_num_match:
            reference = self.clean_reference(ref_num_match.group(1))
            text = text[:ref_num_match.start()].strip()

        # Check for quoted translation
        quote_match = re.search(r'[ʻ\'"\u201c\u201d]([^ʼ\'"\u201c\u201d]+)[ʼ\'"\u201c\u201d]', text)
        if quote_match:
            translation = self.normalize_whitespace(quote_match.group(1))
            # Turoyo is before the quote
            turoyo = self.normalize_whitespace(text[:quote_match.start()])
        else:
            # No quote - check if it's Turoyo
            # Primary indicator: if we extracted a reference, remaining text is likely Turoyo
            # Secondary indicators: special chars, = sign
            if reference or self.has_turoyo_chars(text) or '=' in text:
                turoyo = self.normalize_whitespace(text)
            else:
                # No Turoyo indicators and no reference - treat as translation
                translation = self.normalize_whitespace(text) if len(text) > 10 else ""

        return (turoyo, translation, reference)

    def split_by_letters(self):
        """Split into letter sections"""
        # Updated pattern to handle:
        # 1. &shy; (soft hyphen) before ʔ
        # 2. Whitespace (including newlines) between <h1> and <span>
        # 3. Added ž (U+017E) to character class
        letter_pattern = r'<h1[^>]*>\s*<span[^>]*>(?:&shy;)?([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə])</span></h1>'
        matches = list(re.finditer(letter_pattern, self.html))

        sections = []
        for i, match in enumerate(matches):
            letter = match.group(1)
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(self.html)
            sections.append((letter, self.html[start:end]))

        return sections

    def normalize_root(self, root_text):
        """Normalize root token by stripping trailing numbering markers."""
        return re.match(r'([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})', root_text).group(1)

    def extract_roots_from_section(self, section_html):
        """Extract verb entries"""
        root_pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6}[0-9]?)</span>'
        roots = []

        for match in re.finditer(root_pattern, section_html):
            raw_root = match.group(1)
            normalized_root = self.normalize_root(raw_root)
            start_pos = match.start()
            next_match = re.search(root_pattern, section_html[match.end():])
            end_pos = (match.end() + next_match.start()) if next_match else len(section_html)
            entry_html = section_html[start_pos:end_pos]
            roots.append((normalized_root, entry_html))

        return roots

    def parse_etymology(self, entry_html):
        """Parse etymology with support for nested parentheses and edge cases"""
        # FIXED: Use non-greedy match with lookahead to stop at the RIGHT closing paren
        # Old pattern: r'\(&lt;\s*([^)]{1,300})\)' - stopped at FIRST )
        # Fixed pattern: Uses lookahead to detect end of etymology (followed by uppercase or tag)
        # This correctly handles: (&lt; Arab. ʕdl (II) cf. Wehr 818: ... (wieder) ... ;) II: ...
        etym_pattern = r'\(&lt;\s*(.+?)\s*\)(?:\s*[A-Z<]|$)'
        match = re.search(etym_pattern, entry_html, re.DOTALL)

        if not match:
            return None

        etym_text = match.group(1).strip()
        # Remove trailing semicolon for processing
        etym_text = etym_text.rstrip(';').strip()

        # CRITICAL: Check for truncation - if ends with open paren + stem indicator, it's truncated
        if re.search(r'\([IVX]+$', etym_text) or re.search(r'\((?:Pa|Af|Ap|Et)\.$', etym_text):
            # This is truncated - skip to prevent bad data
            return None

        # Clean up HTML tags and normalize whitespace
        etym_text = re.sub(r'</span></i></font></font><font[^>]*><font[^>]*><i><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'</span></i></font></font><font[^>]*><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'</span></i></font><font[^>]*><i><span[^>]*>', ' ', etym_text)
        etym_text = re.sub(r'<[^>]+>', '', etym_text)  # Remove remaining HTML
        etym_text = self.normalize_whitespace(etym_text)

        # Try structured format: Source root (stem) cf. Reference: meaning
        # Updated to handle optional stem in parentheses
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

        # Try without "cf." - some use comma instead
        # Format: Source root, Reference: meaning
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

        # Try without colon (some refs don't have meaning after colon)
        # Format: Source root cf. Reference
        no_colon = re.match(
            r'([A-Za-z.]+)\s+([^\s]+)\s+(?:\([^)]+\)\s+)?cf\.\s+(.+)',
            etym_text,
            re.DOTALL
        )

        if no_colon:
            ref_part = no_colon.group(3).strip()
            # Check if there's a colon hiding in there
            if ':' in ref_part:
                ref, meaning = ref_part.split(':', 1)
                return {
                    'source': no_colon.group(1).strip(),
                    'source_root': no_colon.group(2).strip(),
                    'reference': self.normalize_whitespace(ref),
                    'meaning': self.normalize_whitespace(meaning),
                }
            else:
                # No colon - reference only
                return {
                    'source': no_colon.group(1).strip(),
                    'source_root': no_colon.group(2).strip(),
                    'reference': self.normalize_whitespace(ref_part),
                    'meaning': '',
                }

        # Simple format
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

    def parse_table_cell(self, cell_html):
        """
        Extract examples from table cell.
        KEY: Multiple examples per paragraph when stream alternates Turoyo→translation, while keeping
        references attached to the correct example. Leading reference-only tokens at the start of a
        paragraph are attached to the previous example.
        """
        soup = BeautifulSoup(cell_html, 'html.parser')

        examples = []

        for para in soup.find_all('p'):
            fragments = self.walk_and_extract(para, in_italic=False)

            # Merge consecutive fragments of same type
            merged = []
            for is_italic, text in fragments:
                if merged and merged[-1][0] == is_italic:
                    merged[-1] = (is_italic, merged[-1][1] + text)
                else:
                    merged.append((is_italic, text))

            # Build token stream
            tokens = []  # each: {'type': 'turoyo'|'translation'|'reference', 'text': str}
            for is_italic, raw in merged:
                text = self.normalize_whitespace(raw)
                if not text:
                    continue
                if is_italic:
                    # Italic: may begin with reference list (possibly preceded by punctuation like ’;)
                    lead = re.match(r'^[^0-9A-Za-z]*((?:\d+(?:/\d+){0,2}|[A-Za-z]{1,6}\.?\s*\d+(?:/\d+)*)\s*(?:;\s*(?:\d+(?:/\d+){0,2}|[A-Za-z]{1,6}\.?\s*\d+(?:/\d+)*)\s*)*)', text)
                    if lead and lead.group(1):
                        prefix = lead.group(1)
                        for tok in re.split(r'\s*;\s*', prefix):
                            tok = tok.strip()
                            if tok:
                                ref = self.clean_reference(tok)
                                if ref:
                                    tokens.append({'type': 'reference', 'text': ref})
                        text = text[lead.end():].strip()
                    # After stripping numeric refs, classify remaining italic text
                    if text:
                        if (not self.has_turoyo_chars(text)) and re.match(r'^[0-9A-Za-z\s./;:\-\[\]]+$', text):
                            _ref = self.clean_reference(text)
                            if _ref:
                                tokens.append({'type': 'reference', 'text': _ref})
                        else:
                            tokens.append({'type': 'turoyo', 'text': text})
                else:
                    turoyo, translation, reference = self.extract_turoyo_from_plain_text(text)
                    # Detect leading reference list like "’; 24/93; 22/3;" possibly with leading punctuation
                    lead = re.match(r'^[^0-9A-Za-z]*((?:\d+(?:/\d+){0,2}|[A-Za-z]{1,6}\.?\s*\d+(?:/\d+)*)\s*(?:;\s*(?:\d+(?:/\d+){0,2}|[A-Za-z]{1,6}\.?\s*\d+(?:/\d+)*)\s*)*)', text)
                    if lead and lead.group(1):
                        prefix = lead.group(1)
                        for tok in re.split(r'\s*;\s*', prefix):
                            tok = tok.strip()
                            if not tok:
                                continue
                            ref = self.clean_reference(tok)
                            if ref:
                                tokens.append({'type': 'reference', 'text': ref})
                        text = text[lead.end():].strip()
                        # Recompute extraction on the remainder
                        turoyo, translation, reference = self.extract_turoyo_from_plain_text(text)
                    if turoyo:
                        tokens.append({'type': 'turoyo', 'text': turoyo})
                    if translation:
                        tokens.append({'type': 'translation', 'text': translation})
                    if reference:
                        tokens.append({'type': 'reference', 'text': reference})

            # Attach leading references (before any turoyo/translation) to previous example
            i = 0
            while i < len(tokens) and tokens[i]['type'] == 'reference':
                if examples:
                    examples[-1]['references'].append(tokens[i]['text'])
                i += 1
            tokens = tokens[i:]
            if not tokens:
                continue

            # Clean stray leading punctuation on the first Turoyo token (leftover after refs like "; ")
            if tokens and tokens[0]['type'] == 'turoyo':
                cleaned = tokens[0]['text'].lstrip(" ;’'`,.:")
                if cleaned:
                    tokens[0]['text'] = cleaned
                else:
                    tokens.pop(0)
                    if not tokens:
                        continue

            # Stream remaining tokens to examples with correct flush conditions
            cur_turoyo = []
            cur_trans = []
            cur_refs = []

            def flush():
                nonlocal cur_turoyo, cur_trans, cur_refs
                if cur_turoyo or cur_trans:
                    t_text = ' '.join(cur_turoyo) if cur_turoyo else ''
                    # Strip stray leading punctuation left from reference separators
                    t_text = t_text.lstrip(" ;’'`,.:")
                    if not t_text and not cur_trans:
                        cur_turoyo, cur_trans, cur_refs = [], [], []
                        return
                    examples.append({
                        'turoyo': t_text,
                        'translations': cur_trans[:],
                        'references': cur_refs[:]
                    })
                cur_turoyo, cur_trans, cur_refs = [], [], []

            for tok in tokens:
                if tok['type'] == 'turoyo':
                    if cur_turoyo or cur_trans or cur_refs:
                        flush()
                    cur_turoyo.append(tok['text'])
                elif tok['type'] == 'translation':
                    cur_trans.append(tok['text'])
                elif tok['type'] == 'reference':
                    cur_refs.append(tok['text'])

            flush()

        return examples

    def extract_tables(self, entry_html, start_pos=0, end_pos=None):
        """Extract tables"""
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

                    header = self.normalize_header(header_match.group(1))
                    examples = self.parse_table_cell(cells[1])

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

        header = self.normalize_whitespace(header)
        return mapping.get(header, header)

    def parse_stems(self, entry_html):
        """Find stem headers"""
        stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'

        stems = []
        for match in re.finditer(stem_pattern, entry_html):
            stem_num = match.group(1)
            forms_text = match.group(2).strip()
            forms = [self.normalize_whitespace(f) for f in forms_text.split('/') if f.strip()]

            stems.append({
                'stem': stem_num,
                'forms': forms,
                'position': match.start()
            })

        return stems

    def parse_entry(self, root, entry_html):
        """Parse verb entry"""
        entry = {
            'root': root,
            'etymology': None,
            'cross_reference': None,
            'stems': [],
            'uncertain': False
        }

        # Cross-reference detection - use pre-extracted dictionary
        # This handles ALL cross-references regardless of HTML structure
        if root in self.cross_references:
            entry['cross_reference'] = self.cross_references[root]
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
            next_pos = stems[i+1]['position'] if i+1 < len(stems) else len(entry_html)
            conjugations = self.extract_tables(entry_html, stem['position'], next_pos)

            entry['stems'].append({
                'stem': stem['stem'],
                'forms': stem['forms'],
                'conjugations': conjugations
            })

            self.stats['stems_parsed'] += 1

        # Detransitive - TWO patterns in the HTML
        # Pattern 1: <font size="4" style="font-size: 16pt"><b><span>Detransitive (rare, only 4 occurrences)
        detrans_pattern1 = r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive'
        # Pattern 2: <p lang="en-GB" class="western"><span>Detransitive</span></p> (common, 521 occurrences)
        detrans_pattern2 = r'<p lang="en-GB" class="western"><span[^>]*>Detransitive</span></p>'

        detrans_match = re.search(detrans_pattern1, entry_html)
        if not detrans_match:
            detrans_match = re.search(detrans_pattern2, entry_html)

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
        print("🔄 Parsing with cross-reference fix...")

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

        # Add stub entries for cross-references that don't have their own entries
        # These are standalone cross-ref paragraphs that don't match the root pattern
        parsed_roots = set(v['root'] for v in self.verbs)
        for from_root, to_root in self.cross_references.items():
            if from_root not in parsed_roots:
                # Create stub entry
                stub_entry = {
                    'root': from_root,
                    'etymology': None,
                    'cross_reference': to_root,
                    'stems': [],
                    'uncertain': False
                }
                self.verbs.append(stub_entry)
                self.stats['verbs_parsed'] += 1
                self.stats['cross_references'] += 1
                self.stats['stub_cross_references'] = self.stats.get('stub_cross_references', 0) + 1

        print(f"\n✅ Parsed {self.stats['verbs_parsed']} verbs, {self.stats['stems_parsed']} stems")
        print(f"   🔗 Cross-references: {self.stats['cross_references']} ({self.stats.get('stub_cross_references', 0)} stubs)")
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
                    'parser_version': '6.0.0-v4-xref-fixed',
                    'notes': 'Fixed cross-reference detection: added ž character, strip HTML before matching'
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved: {output_file}")
        print(f"   📊 {total_examples} examples")

        # Sample
        if self.verbs:
            sample_file = output_file.parent / 'verbs_clean_v4_sample.json'
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(self.verbs[:3], f, ensure_ascii=False, indent=2)
            print(f"   📄 Sample: {sample_file}")

        if self.errors:
            errors_file = output_file.parent / 'parsing_errors_v4.txt'
            with open(errors_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.errors))
            print(f"   ❌ Errors: {errors_file}")


def main():
    parser = CleanTuroyoParser('source/Turoyo_all_2024.html')
    parser.parse_all()
    parser.save_json('data/verbs_clean_v4.json')

if __name__ == '__main__':
    main()
