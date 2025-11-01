#!/usr/bin/env python3
"""Debug why hyw 1 idioms aren't being extracted"""

import sys
sys.path.insert(0, 'parser')

from parse_docx_production import FixedDocxParser
from docx import Document

# Create parser instance
parser = FixedDocxParser()

# Open the DOCX file with hyw 1
doc = Document('.devkit/new-source-docx/3. h,ḥ,k.docx')

# Find hyw 1 manually
import re
turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə'
root_pattern = re.compile(rf'^(hyw\s+1)\s*[<(]', re.UNICODE)
stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

in_hyw1 = False
pending_paras = []

for para in doc.paragraphs:
    text = para.text.strip()

    if not text:
        continue

    if root_pattern.match(text):
        print(f"✓ Found root: {text[:80]}")
        in_hyw1 = True
        pending_paras = []
        continue

    if in_hyw1:
        # Check if it's a stem header
        if stem_pattern.match(text):
            print(f"\n✓ Hit first stem: {text}")
            print(f"\n📊 Collected {len(pending_paras)} paragraphs before first stem")

            # Now test idiom extraction
            verb_forms = ['obe', 'hule']  # Manually specified for hyw 1
            print(f"\n🔍 Testing idiom extraction with verb_forms: {verb_forms}")

            for i, p in enumerate(pending_paras, 1):
                p_text = p.text.strip()
                is_idiom = parser.is_idiom_paragraph(p_text, verb_forms)
                is_table = parser.is_in_table(p)

                status = "❌"
                if is_table:
                    status = "📊 [IN TABLE]"
                elif is_idiom:
                    status = "✅ IDIOM"

                print(f"\n  Para {i}: {status}")
                print(f"    {p_text[:100]}...")

            # Actually extract idioms
            idioms = parser.extract_idioms(pending_paras, verb_forms)
            if idioms:
                print(f"\n✅ EXTRACTED {len(idioms)} IDIOMS:")
                for i, idiom in enumerate(idioms, 1):
                    print(f"\n  {i}. Phrase: {idiom['phrase'][:50] if idiom['phrase'] else '(empty)'}")
                    print(f"     Meaning: {idiom['meaning'][:50] if idiom['meaning'] else '(empty)'}")
            else:
                print(f"\n❌ NO IDIOMS EXTRACTED")

            break

        # Not a stem - collect this paragraph
        if not parser.is_in_table(para):
            pending_paras.append(para)
