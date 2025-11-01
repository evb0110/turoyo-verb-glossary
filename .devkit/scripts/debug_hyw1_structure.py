#!/usr/bin/env python3
"""Understand the actual DOCX structure for hyw 1"""

from docx import Document
import re

doc = Document('.devkit/new-source-docx/3. h,ḥ,k.docx')

root_pattern = re.compile(r'^(hyw\s+1)\s*[<(]', re.UNICODE)
stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

in_hyw1 = False
para_count = 0

for para in doc.paragraphs:
    text = para.text.strip()

    if not text:
        continue

    if root_pattern.match(text):
        print(f"═══════════════════════════════════════════════════════════")
        print(f"ROOT: {text}")
        print(f"═══════════════════════════════════════════════════════════")
        in_hyw1 = True
        para_count = 0
        continue

    if in_hyw1:
        para_count += 1

        # Check if new root
        if re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]+(?:\s+\d+)?)\s*[<(]', text, re.UNICODE):
            print(f"\n[END - Next root found]")
            break

        is_stem = stem_pattern.match(text) or text.startswith('Detransitive')
        is_table = para._element.getparent().tag.endswith('tbl')

        marker = ""
        if is_stem:
            marker = "🔷 STEM"
        elif is_table:
            marker = "📊 TABLE"
        else:
            marker = "📝 PARA"

        print(f"\n{para_count:3}. {marker}: {text[:100]}")

        if para_count >= 45:  # Limit output
            print(f"\n[... output truncated after 45 paragraphs ...]")
            break
