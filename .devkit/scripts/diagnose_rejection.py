#!/usr/bin/env python3
"""Diagnose WHY paragraphs are being rejected"""

import sys
sys.path.insert(0, 'parser')

from parse_docx_production import FixedDocxParser
from docx import Document
import re

parser = FixedDocxParser()
doc = Document('source/glossary-docx/2026-10-21/3. h,ḥ,k.docx')

root_pattern = re.compile(r'^(hyw\s+1)\s*[<(]', re.UNICODE)
stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

in_hyw1 = False
has_stem = False
verb_forms = ['obe', 'hule', 'mahwele', 'mahwe']

# Test cases that SHOULD be accepted
test_cases = [
    "obe/hule ʕafu 'begnadigen': w-hule-ste ʕafu",
    "obe/hule aman, amniye 'Sicherheit geben': húli-lox",
    "hule/obe baxt 'Ehrenwort geben': an=noš-ani",
]

print("="*80)
print("TESTING QUOTE DETECTION")
print("="*80)

for test in test_cases:
    print(f"\nTest: {test[:60]}...")

    # Check for quotes
    import re
    quote_pattern = r'[ʻʼ\'''"""\"]'
    quotes_found = re.findall(quote_pattern, test)
    print(f"  Quotes found: {quotes_found} (count: {len(quotes_found)})")

    # Check has_verb_form
    has_verb = any(form in test for form in verb_forms if form)
    print(f"  Has verb form: {has_verb}")

    # Check is_idiom_paragraph
    result = parser.is_idiom_paragraph(test, verb_forms)
    print(f"  is_idiom_paragraph: {result}")

    if not result:
        print(f"  ❌ REJECTED!")

print("\n" + "="*80)
print("TESTING ACTUAL DOCX PARAGRAPHS")
print("="*80)

for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue

    if root_pattern.match(text):
        in_hyw1 = True
        has_stem = False
        continue

    if in_hyw1 and re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]+(?:\s+\d+)?)\s*[<(]', text, re.UNICODE):
        break

    if in_hyw1:
        if stem_pattern.match(text) or text.startswith('Detransitive'):
            has_stem = True
        elif has_stem and not parser.is_in_table(para):
            # This is an idiom candidate
            if 'ʕafu' in text or 'aman' in text or 'baxt' in text:
                print(f"\n📝 Testing: {text[:80]}...")

                # Show actual quote characters
                quotes_in_text = []
                for char in text:
                    if char in ["'", "'", "'", "ʻ", "ʼ", '"', '"', '"']:
                        quotes_in_text.append(f"{char}(U+{ord(char):04X})")
                print(f"  Quotes in text: {quotes_in_text}")

                # Test detection
                result = parser.is_idiom_paragraph(text, verb_forms)
                print(f"  is_idiom_paragraph: {result}")

                if not result:
                    print(f"  ❌ REJECTED - WHY?")

                    # Debug each condition
                    has_verb = any(form in text for form in verb_forms if form)
                    quote_pattern = r'[ʻʼ\'''"""\"]'
                    has_quote = bool(re.search(quote_pattern, text))

                    print(f"     has_verb_form: {has_verb}")
                    print(f"     has_quotation: {has_quote}")
                    print(f"     Condition 1 (verb+quote): {has_verb and has_quote}")
