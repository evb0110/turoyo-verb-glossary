#!/usr/bin/env python3
"""Extract raw text from DOCX and JSON for hyw 1 to see data loss"""

import json
import re
from docx import Document

# Extract from DOCX
doc = Document('.devkit/new-source-docx/3. h,ḥ,k.docx')

root_pattern = re.compile(r'^(hyw\s+1)\s*[<(]', re.UNICODE)
stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

in_hyw1 = False
has_stem = False
docx_idiom_paras = []

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
        elif has_stem and not para._element.getparent().tag.endswith('tbl'):
            # Skip the "Idiomatic phrases" header
            if text not in ['Idiomatic phrases', 'Idioms:', 'Examples:']:
                # Skip general meaning lists
                if not re.match(r'^\d+\)\s+.+;.+;', text):
                    docx_idiom_paras.append(text)

# Extract from JSON
with open('.devkit/analysis/docx_v2_verbs/hyw 1.json') as f:
    verb = json.load(f)

json_idiom_texts = []
if verb.get('idioms'):
    for idiom in verb['idioms']:
        # Reconstruct the text
        parts = []
        if idiom['phrase']:
            parts.append(idiom['phrase'])
        if idiom['meaning']:
            parts.append(f"'{idiom['meaning']}'")
        if idiom['examples']:
            for ex in idiom['examples']:
                if ex.get('turoyo'):
                    parts.append(ex['turoyo'])
                if ex.get('translation'):
                    parts.append(f"'{ex['translation']}'")
        json_idiom_texts.append(' '.join(parts))

# Compare
print("="*80)
print("DOCX SOURCE - IDIOM PARAGRAPHS")
print("="*80)
print(f"\nTotal paragraphs: {len(docx_idiom_paras)}\n")
for i, text in enumerate(docx_idiom_paras, 1):
    print(f"{i:2}. {text[:120]}")
    if len(text) > 120:
        print(f"    {text[120:240]}")
    print()

print("\n" + "="*80)
print("JSON OUTPUT - EXTRACTED IDIOMS")
print("="*80)
print(f"\nTotal idioms: {len(json_idiom_texts)}\n")
for i, text in enumerate(json_idiom_texts, 1):
    print(f"{i:2}. {text[:120]}")
    if len(text) > 120:
        print(f"    {text[120:240]}")
    print()

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)
print(f"DOCX paragraphs: {len(docx_idiom_paras)}")
print(f"JSON idioms: {len(json_idiom_texts)}")
print(f"DATA LOSS: {len(docx_idiom_paras) - len(json_idiom_texts)} paragraphs lost ({((len(docx_idiom_paras) - len(json_idiom_texts)) / len(docx_idiom_paras) * 100):.1f}%)")

# Show which DOCX paragraphs are missing
print(f"\n🔍 MISSING FROM JSON:")
# Simple heuristic: check if any phrase from JSON appears in DOCX paragraph
for i, docx_text in enumerate(docx_idiom_paras, 1):
    found = False
    for json_text in json_idiom_texts:
        # Extract first 20 chars of phrase
        phrase_start = json_text.split("'")[0].strip()[:20]
        if phrase_start and phrase_start in docx_text:
            found = True
            break
    if not found:
        print(f"\n{i:2}. LOST: {docx_text[:150]}")
