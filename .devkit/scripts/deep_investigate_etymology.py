#!/usr/bin/env python3
"""Deep investigation of etymology issues"""

import json
from pathlib import Path

# Load the mismatch data
report_path = Path('.devkit/analysis/validation_report_v2.json')
with open(report_path, 'r', encoding='utf-8') as f:
    report = json.load(f)

etymology_issues = report['discrepancies']['etymology_mismatch']

# Categorize
extra_etymology = [e for e in etymology_issues if e['type'] == 'extra_etymology']
missing_etymology = [e for e in etymology_issues if e['type'] == 'missing_etymology']
missing_fields = [e for e in etymology_issues if e['type'] == 'missing_etymology_fields']

print("=" * 80)
print("DEEP ETYMOLOGY INVESTIGATION")
print("=" * 80)
print(f"\n📊 Categories:")
print(f"   Extra etymology (DOCX has, original doesn't): {len(extra_etymology)}")
print(f"   Missing etymology (original has, DOCX doesn't): {len(missing_etymology)}")
print(f"   Missing fields (both have, different structure): {len(missing_fields)}")

# Function to load and compare verbs
def compare_verbs(root):
    """Load both versions and compare"""
    original_path = Path(f'server/assets/verbs/{root}.json')
    docx_path = Path(f'.devkit/analysis/docx_v2_verbs/{root}.json')

    original = None
    docx = None

    if original_path.exists():
        with open(original_path, 'r', encoding='utf-8') as f:
            original = json.load(f)

    if docx_path.exists():
        with open(docx_path, 'r', encoding='utf-8') as f:
            docx = json.load(f)

    return original, docx

# Investigate Category 1: Extra Etymology (sample 10)
print("\n" + "=" * 80)
print("CATEGORY 1: EXTRA ETYMOLOGY (DOCX has it, original doesn't)")
print("=" * 80)

for i, issue in enumerate(extra_etymology[:10], 1):
    root = issue['root']
    original, docx = compare_verbs(root)

    print(f"\n{i}. ROOT: {root}")
    print(f"   Original etymology: {original.get('etymology') if original else 'FILE NOT FOUND'}")
    print(f"   DOCX etymology:     {docx.get('etymology') if docx else 'FILE NOT FOUND'}")

    # Check if original has etymology in a different location
    if original and not original.get('etymology'):
        # Sometimes etymology might be in root text or elsewhere
        print(f"   Original root field: {original.get('root')}")
        if 'uncertain' in original:
            print(f"   Original uncertain: {original.get('uncertain')}")

# Investigate Category 2: Missing Etymology (all 6)
print("\n" + "=" * 80)
print("CATEGORY 2: MISSING ETYMOLOGY (original has it, DOCX doesn't)")
print("=" * 80)

for i, issue in enumerate(missing_etymology, 1):
    root = issue['root']
    original, docx = compare_verbs(root)

    print(f"\n{i}. ROOT: {root}")
    print(f"   Original etymology: {json.dumps(original.get('etymology'), ensure_ascii=False) if original else 'FILE NOT FOUND'}")
    print(f"   DOCX etymology:     {json.dumps(docx.get('etymology'), ensure_ascii=False) if docx else 'FILE NOT FOUND'}")

    # This is critical - we need to extract these!

# Investigate Category 3: Missing Fields (all 3)
print("\n" + "=" * 80)
print("CATEGORY 3: MISSING FIELDS (structure difference)")
print("=" * 80)

for i, issue in enumerate(missing_fields, 1):
    root = issue['root']
    original, docx = compare_verbs(root)

    print(f"\n{i}. ROOT: {root}")
    print(f"   Missing fields: {issue['missing']}")
    print(f"   Original: {json.dumps(issue['original'], ensure_ascii=False)}")
    print(f"   DOCX:     {json.dumps(issue['docx'], ensure_ascii=False)}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
Category 1 (Extra etymology): {len(extra_etymology)} cases
  → These are GOOD! DOCX found etymologies that original parser missed.
  → Need to verify these are correct extractions from DOCX source.
  → If correct, this is an IMPROVEMENT, not a regression.

Category 2 (Missing etymology): {len(missing_etymology)} cases
  → These are BAD! Parser is missing etymologies that should be extracted.
  → CRITICAL: Must fix parser to extract these.

Category 3 (Missing fields): {len(missing_fields)} cases
  → These are STRUCTURE differences.
  → Original has "notes" field with raw text
  → DOCX has structured fields (source_root, reference, meaning)
  → Need to decide: Which structure is correct?
""")
