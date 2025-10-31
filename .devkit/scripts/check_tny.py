#!/usr/bin/env python3
import re
from pathlib import Path
from docx import Document

doc = Document('.devkit/new-source-docx/6. š,t,ṭ,ṯ.docx')
in_verb = False
count = 0

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if not text:
        continue

    if re.match(r'^ṯny(\s|\()', text):
        in_verb = True
        print(f'{i}: ROOT: {text[:100]}')

    if in_verb:
        count += 1
        if count > 20:
            break

        has_bold = any(r.bold for r in para.runs)
        has_italic = any(r.italic for r in para.runs)
        sizes = [r.font.size.pt for r in para.runs if r.font.size]

        stem_match = re.match(r'^([IVX]+):', text)
        detrans = 'Detransitive' in text

        print(f'{i}: {text[:80]} | bold={has_bold} italic={has_italic} 14pt={14.0 in sizes} stem={stem_match.group(1) if stem_match else None} detrans={detrans}')

        next_root = re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(\s+\d+|\s+\()', text)
        if next_root and count > 5 and next_root.group(1) != 'ṯny':
            print(f'{i}: NEXT VERB: {next_root.group(1)}')
            break
