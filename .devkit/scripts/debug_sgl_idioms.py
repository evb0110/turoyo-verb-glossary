#!/usr/bin/env python3
"""
Debug script to trace idiom parsing for šġl 1 verb.
"""

import sys
import re
from docx import Document

# Add parent directory to path to import parser
sys.path.insert(0, '/Users/evb/WebstormProjects/turoyo-verb-glossary/parser')
from parse_docx_production import FixedDocxParser

# Monkey-patch the parser to add debug output
original_extract_idioms = FixedDocxParser.extract_idioms

def debug_extract_idioms(self, paragraphs, verb_forms, in_idioms_section=False):
    """Wrapper with debug output"""
    print(f"\n🔍 extract_idioms() called:")
    print(f"   in_idioms_section: {in_idioms_section}")
    print(f"   paragraphs count: {len(paragraphs)}")
    for i, para in enumerate(paragraphs):
        text = para.text.strip()
        print(f"   Para {i}: {text[:80]}...")

    result = original_extract_idioms(self, paragraphs, verb_forms, in_idioms_section)

    print(f"   Result: {result}")
    return result

FixedDocxParser.extract_idioms = debug_extract_idioms

# Also patch the main parse loop to track idiom section state
original_parse = FixedDocxParser.parse_document

def debug_parse(self, doc_path):
    """Wrapper to track šġl 1 processing"""
    doc = Document(doc_path)

    print(f"\n📄 Processing: {doc_path}")

    current_verb = None
    current_root = None

    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        # Detect verb roots
        if re.match(r'^šġl\s+\d+', text):
            current_root = text
            print(f"\n🔹 Verb root found at para {para_idx}: {current_root}")
            current_verb = None

        # Track idiom section state only for šġl 1
        if current_root and current_root.startswith('šġl 1'):
            if re.match(r'^(Idiomatic phrases?|Idioms?):?$', text, re.IGNORECASE):
                print(f"\n💬 Idiom header found at para {para_idx}: '{text}'")
                print(f"   in_idioms_section will be set to True")

            # Detect stem headers
            if re.match(r'^(III|Detransitive):', text) or text == 'Detransitive':
                print(f"\n🔸 Stem header found at para {para_idx}: '{text}'")
                print(f"   in_idioms_section: {self.in_idioms_section}")
                print(f"   pending_idiom_paras count: {len(self.pending_idiom_paras)}")

        # Stop at next verb
        if current_root and current_root.startswith('šġl 1'):
            if text and not text.startswith('šġl 1') and re.match(r'^[a-zšṭṯḏḥġṣžčǧʕʔ]+\s+\d+', text):
                print(f"\n🔹 Next verb found at para {para_idx}, stopping šġl 1 tracking")
                current_root = None

    # Now run the actual parser
    return original_parse(self, doc_path)

FixedDocxParser.parse_document = debug_parse

# Run parser on the specific DOCX file
if __name__ == '__main__':
    parser = FixedDocxParser()
    docx_path = '/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/new-source-docx/6. š,t,ṭ,ṯ.docx'

    print("=" * 80)
    print("DEBUG: Parsing šġl verbs from DOCX")
    print("=" * 80)

    verbs = parser.parse_document(docx_path)

    # Find and print šġl 1
    print("\n" + "=" * 80)
    print("RESULTS: šġl 1 verb")
    print("=" * 80)

    for verb in verbs:
        if verb['root'] == 'šġl 1':
            import json
            print(json.dumps(verb, ensure_ascii=False, indent=2))
            print(f"\n✅ Idioms field: {verb.get('idioms')}")
            break
    else:
        print("❌ šġl 1 not found in parsed verbs")
