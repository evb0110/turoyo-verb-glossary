#!/usr/bin/env python3
"""
Verify hyw 1 specifically to understand what idioms we're missing
and refine the detection heuristic.
"""

from docx import Document
import re
from pathlib import Path

# Open the DOCX file
doc = Document('.devkit/new-source-docx/3. h,ḥ,k.docx')

# Find hyw 1 paragraphs (roughly 142-194 based on previous investigation)
turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə'
root_pattern = re.compile(rf'^(hyw\s+1)\s*[<(]', re.UNICODE)
stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

in_hyw1 = False
hyw1_paragraphs = []
para_index = 0

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()

    if not text:
        continue

    # Check if we found hyw 1
    if root_pattern.match(text):
        in_hyw1 = True
        hyw1_paragraphs.append({
            'index': i,
            'text': text,
            'type': 'ROOT',
            'in_table': para._element.getparent().tag.endswith('tbl')
        })
        para_index = 0
        continue

    # Check if we hit the next root (end of hyw 1)
    if in_hyw1 and re.match(rf'^([{turoyo_chars}]+(?:\s+\d+)?)\s*[<(]', text, re.UNICODE):
        # This is a new root, stop collecting
        break

    # Collect paragraphs for hyw 1
    if in_hyw1:
        para_index += 1

        # Determine type
        para_type = 'OTHER'
        if stem_pattern.match(text):
            para_type = 'STEM_HEADER'
        elif para._element.getparent().tag.endswith('tbl'):
            para_type = 'TABLE'
        else:
            # Check if it looks like an idiomatic expression
            # Patterns:
            # 1. obe/hule + Turoyo word(s) + optional translation
            # 2. Contains forms "obe" or "hule" with other Turoyo
            # 3. Has quotation marks indicating translation
            has_obe_hule = bool(re.search(r'\b(obe|hule)\b', text))
            has_quotation = bool(re.search(r'[ʻʼ""]', text))
            has_turoyo = bool(re.search(rf'[{turoyo_chars}]+', text, re.UNICODE))

            if has_obe_hule and (has_turoyo or has_quotation):
                para_type = 'IDIOM'
            elif has_turoyo and has_quotation:
                para_type = 'IDIOM'

        hyw1_paragraphs.append({
            'index': i,
            'text': text[:150] + '...' if len(text) > 150 else text,
            'type': para_type,
            'in_table': para._element.getparent().tag.endswith('tbl')
        })

# Print analysis
print("="*80)
print("HYW 1 DETAILED PARAGRAPH ANALYSIS")
print("="*80)

type_counts = {}
for para in hyw1_paragraphs:
    para_type = para['type']
    type_counts[para_type] = type_counts.get(para_type, 0) + 1

print(f"\nTotal paragraphs in hyw 1: {len(hyw1_paragraphs)}")
print(f"\nBreakdown by type:")
for para_type, count in sorted(type_counts.items()):
    print(f"  {para_type}: {count}")

print(f"\n🔍 DETAILED PARAGRAPH LISTING:")
print(f"{'='*80}")

for para in hyw1_paragraphs:
    marker = "📍" if para['type'] == 'IDIOM' else "  "
    in_table = " [IN TABLE]" if para['in_table'] else ""
    print(f"{marker} Para {para['index']} ({para['type']}{in_table}):")
    print(f"   {para['text']}")
    print()

# Count idioms not in tables
idioms_not_in_tables = [p for p in hyw1_paragraphs if p['type'] == 'IDIOM' and not p['in_table']]
print(f"\n💥 CRITICAL FINDING:")
print(f"   Idiomatic expressions NOT in tables: {len(idioms_not_in_tables)}")
print(f"   These are LOST by the current parser!")
