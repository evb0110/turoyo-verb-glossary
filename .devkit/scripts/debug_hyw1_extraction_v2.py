#!/usr/bin/env python3
"""Debug why we're getting 15/33 idioms for hyw 1"""

import sys
sys.path.insert(0, 'parser')

from parse_docx_production import FixedDocxParser
from docx import Document
import re

parser = FixedDocxParser()

doc = Document('.devkit/new-source-docx/3. h,ḥ,k.docx')

root_pattern = re.compile(r'^(hyw\s+1)\s*[<(]', re.UNICODE)
stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

in_hyw1 = False
has_stem = False
pending_paras = []
all_verb_forms = ['obe', 'hule', 'mahwele', 'mahwe']

print("Looking for hyw 1...")

for para in doc.paragraphs:
    text = para.text.strip()

    if not text:
        continue

    # Check if we found hyw 1 root
    if root_pattern.match(text):
        print(f"\n✓ Found root: {text[:80]}")
        in_hyw1 = True
        has_stem = False
        pending_paras = []
        continue

    # Check if we hit next root (end of hyw 1)
    if in_hyw1 and re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]+(?:\s+\d+)?)\s*[<(]', text, re.UNICODE):
        print(f"\n✓ Found next root, ending hyw 1 collection")
        print(f"\n📊 Collected {len(pending_paras)} paragraphs AFTER stems")

        # Test extraction
        idioms = parser.extract_idioms(pending_paras, all_verb_forms)
        print(f"\n✅ EXTRACTED {len(idioms) if idioms else 0} IDIOMS")

        # Show which paragraphs were accepted/rejected
        print(f"\n🔍 DETAILED ANALYSIS:")
        for i, p in enumerate(pending_paras, 1):
            p_text = p.text.strip()
            is_table = parser.is_in_table(p)
            is_idiom = parser.is_idiom_paragraph(p_text, all_verb_forms)

            status = "📊 [TABLE]" if is_table else ("✅ IDIOM" if is_idiom else "❌ SKIPPED")
            print(f"\n  {i:2}. {status}")
            print(f"      {p_text[:90]}...")

        break

    # If we're in hyw 1 and have seen a stem, collect paragraphs
    if in_hyw1:
        # Check if this is a stem
        if stem_pattern.match(text) or text.startswith('Detransitive'):
            has_stem = True
            print(f"  ✓ Found stem: {text}")

        # If we have a stem, collect non-stem paragraphs
        elif has_stem and not parser.is_in_table(para):
            pending_paras.append(para)
