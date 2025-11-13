#!/usr/bin/env python3
"""Test nql parsing with debug output"""

import re
import sys
from pathlib import Path

sys.path.insert(0, 'parser')

# Monkey-patch the parser to add debug output
original_code = open('parser/parse_docx_production.py', 'r', encoding='utf-8').read()

# Add debug output
debug_code = original_code.replace(
    "if para_text in ['Detransitive', 'Action Noun', 'Infinitiv']:",
    '''if para_text in ['Detransitive', 'Action Noun', 'Infinitiv']:
                            print(f"\\n>>> DEBUG: Found special stem '{para_text}' at element {idx}")'''
)

debug_code = debug_code.replace(
    "if re.match(forms_pattern, next_text):",
    '''print(f"    >>> Checking para {j}: '{next_text[:60]}'")
                                    if re.match(forms_pattern, next_text):
                                        print(f"    ✅ Matched as forms!")'''
)

debug_code = debug_code.replace(
    "if not label_gloss:",
    '''print(f"    >>> Checking for gloss: '{next_text[:60]}'")
                                if not label_gloss:
                                    print(f"    ✅ Using as gloss")'''
)

# Save and import
with open('/tmp/parse_docx_debug.py', 'w', encoding='utf-8') as f:
    f.write(debug_code)

sys.path.insert(0, '/tmp')
from parse_docx_debug import FixedDocxParser

print("Running parser with debug output...\n")
parser = FixedDocxParser()
parser.parse_document_with_tables(Path('.devkit/new-source-docx/4. l,m,n,p.docx'))

nql = next((v for v in parser.verbs if v['root'] == 'nql'), None)

if nql:
    print(f"\n{'='*60}")
    print(f"nql extracted with {len(nql['stems'])} stems:")
    for i, stem in enumerate(nql['stems'], 1):
        print(f"\n{i}. Stem: {stem['stem']}")
        print(f"   Forms: {stem['forms']}")
        if 'label_gloss_tokens' in stem:
            print(f"   Gloss: {stem['label_gloss_tokens'][0]['text']}")
    print(f"{'='*60}")
