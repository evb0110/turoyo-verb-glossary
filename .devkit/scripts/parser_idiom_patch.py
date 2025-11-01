"""
Idiom Extraction Patch for parse_docx_production.py

This file contains the methods to add to the parser for idiom extraction.
"""

def is_in_table(self, para):
    """Check if paragraph is inside a table"""
    return para._element.getparent().tag.endswith('tbl')

def is_idiom_paragraph(self, text, verb_forms):
    """
    Detect if a paragraph is an idiomatic expression.

    Args:
        text: Paragraph text
        verb_forms: List of verb forms for this root (e.g., ['obe', 'hule', 'mahwele'])

    Returns:
        bool: True if this looks like an idiomatic expression
    """
    if not text or len(text) < 10:
        return False

    # Pattern 1: Contains verb form + Turoyo word(s) + quotation mark (translation)
    # Example: "obe/hule ʕafu 'begnadigen': ..."
    has_verb_form = any(form in text for form in verb_forms if form)
    has_quotation = bool(re.search(r'[ʻʼ""]', text))

    if has_verb_form and has_quotation:
        return True

    # Pattern 2: Starts with Turoyo characters and has quotation (less strict)
    # Example: "iḏa kān d-zəbṭi ... 'wenn sie...'"
    turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə'
    starts_with_turoyo = bool(re.match(rf'^[{turoyo_chars}]', text, re.UNICODE))

    if starts_with_turoyo and has_quotation and len(text) > 30:
        return True

    # Pattern 3: Contains multiple Turoyo words with translations
    # Count Turoyo character sequences
    turoyo_sequences = re.findall(rf'[{turoyo_chars}]+', text, re.UNICODE)
    if len(turoyo_sequences) >= 3 and has_quotation:
        return True

    return False

def parse_idiom_paragraph(self, text):
    """
    Parse an idiomatic expression paragraph into structured data.

    Expected patterns:
    1. "PHRASE 'MEANING': EXAMPLE 'TRANSLATION'"
    2. "PHRASE 'MEANING'"
    3. Just an example with translation

    Returns:
        dict or None: Idiom data with phrase, meaning, and examples
    """
    text = text.strip()

    # Try to extract:
    # - Phrase (Turoyo idiomatic expression)
    # - Meaning (first quoted text)
    # - Example and translation (rest of text)

    # Pattern: "phrase 'meaning': example 'translation'"
    # or: "phrase 'meaning' example 'translation'"

    # Find all quoted segments (using various quotation marks)
    quotes = re.findall(r'[ʻʼ""]([^ʻʼ""]+)[ʻʼ""]', text)

    if not quotes:
        # No clear structure - return as raw example
        return {
            'phrase': '',
            'meaning': '',
            'examples': [{
                'turoyo': text[:200],  # Truncate long text
                'translation': '',
                'reference': None
            }]
        }

    # First quote is usually the meaning/gloss
    meaning = quotes[0] if quotes else ''

    # Extract phrase (text before first quote)
    first_quote_pos = text.find(f"'{meaning}'") if meaning else 0
    if first_quote_pos < 0:
        first_quote_pos = text.find(f"ʻ{meaning}ʼ")
    if first_quote_pos < 0:
        first_quote_pos = text.find(f'"{meaning}"')

    phrase = text[:first_quote_pos].strip() if first_quote_pos > 0 else ''

    # Clean up phrase (remove trailing colon, 'to' prefix, etc.)
    phrase = re.sub(r':+$', '', phrase).strip()

    # Extract example (text after first quote)
    example_start = first_quote_pos + len(meaning) + 2 if first_quote_pos >= 0 else 0
    example_text = text[example_start:].strip()

    # Clean up example (remove leading colon)
    example_text = re.sub(r'^:\s*', '', example_text)

    # Split example into Turoyo and translation
    turoyo_part = ''
    translation_part = ''

    if len(quotes) > 1:
        # Second quote is usually the translation
        translation_part = quotes[1]

        # Turoyo is between first and second quote
        second_quote_pos = example_text.find(f"'{translation_part}'")
        if second_quote_pos < 0:
            second_quote_pos = example_text.find(f"ʻ{translation_part}ʼ")
        if second_quote_pos < 0:
            second_quote_pos = example_text.find(f'"{translation_part}"')

        if second_quote_pos > 0:
            turoyo_part = example_text[:second_quote_pos].strip()
        else:
            turoyo_part = example_text
    else:
        # No translation quote - entire example is Turoyo
        turoyo_part = example_text

    # Extract reference (page/line numbers)
    reference = None
    ref_match = re.search(r'\b(\d+/\d+|\d+:\d+)\b', text)
    if ref_match:
        reference = ref_match.group(1)

    return {
        'phrase': phrase,
        'meaning': meaning,
        'examples': [{
            'turoyo': turoyo_part[:300] if turoyo_part else '',  # Truncate if very long
            'translation': translation_part[:300] if translation_part else '',
            'reference': reference
        }] if turoyo_part or translation_part else []
    }

def extract_idioms(self, paragraphs, verb_forms):
    """
    Extract idiomatic expressions from paragraphs between root and first stem.

    Args:
        paragraphs: List of paragraph objects
        verb_forms: List of verb forms for this root

    Returns:
        list or None: List of idiom dicts, or None if no idioms found
    """
    idioms = []

    for para in paragraphs:
        # Skip if in table (tables are handled separately)
        if self.is_in_table(para):
            continue

        text = para.text.strip()

        # Skip empty or very short
        if not text or len(text) < 10:
            continue

        # Skip if it's clearly just a note or header
        if text in ['Detransitive', 'Idiomatic phrases', 'Idioms:', 'Examples:']:
            continue

        # Skip numbered meaning lists (these are part of the general definition)
        if re.match(r'^\d+\)\s+.+;.+;', text):
            # Pattern like "1) meaning1; 2) meaning2; 3) meaning3"
            continue

        # Check if this looks like an idiom
        if self.is_idiom_paragraph(text, verb_forms):
            idiom = self.parse_idiom_paragraph(text)
            if idiom and (idiom['phrase'] or idiom['meaning']):
                idioms.append(idiom)

    return idioms if idioms else None


# MODIFICATIONS TO __init__ method:
# Add to line 44 (in __init__):
#     self.pending_idiom_paras = []  # Track paragraphs between root and first stem


# MODIFICATIONS TO parse_docx method (around line 820-850):

# CHANGE 1: After line 820 (after creating current_verb dict), add:
#     current_verb = {
#         'root': root,
#         'etymology': etymology,
#         'cross_reference': None,
#         'stems': [],
#         'idioms': None,  # NEW: Will be populated before first stem
#         'uncertain': '???' in para.text
#     }
#     current_stem = None
#     self.pending_idiom_paras = []  # NEW: Reset for new verb

# CHANGE 2: After line 833 (in "elif self.is_stem_header(para):" block), add extraction logic:
#     elif self.is_stem_header(para):
#         # NEW: Extract idioms BEFORE adding first stem
#         if current_verb is not None and not current_verb['stems']:
#             # This is the first stem - extract idioms from preceding paragraphs
#             if self.pending_idiom_paras:
#                 verb_forms = []  # Will be populated after stem extraction
#                 idioms = self.extract_idioms(self.pending_idiom_paras, verb_forms)
#                 if idioms:
#                     current_verb['idioms'] = idioms
#                     self.stats['idioms_extracted'] += len(idioms)
#                 self.pending_idiom_paras = []  # Clear after extraction
#
#         stem_num, forms = self.extract_stem_info(para.text)
#         if stem_num and current_verb is not None:
#             current_stem = {
#                 'stem': stem_num,
#                 'forms': forms,
#                 'conjugations': {}
#             }
#             current_verb['stems'].append(current_stem)
#             self.stats['stems_parsed'] += 1

# CHANGE 3: Add new else clause to track non-stem, non-root paragraphs (after line 852):
#     elif 'Detransitive' in para.text and current_verb:
#         # ... existing detransitive logic ...
#
#     # NEW: Track paragraphs for idiom extraction
#     elif current_verb is not None and not current_verb['stems']:
#         # We're between root and first stem - collect this paragraph
#         self.pending_idiom_paras.append(para)
