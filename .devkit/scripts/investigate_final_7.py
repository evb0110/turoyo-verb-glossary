#!/usr/bin/env python3
"""Investigate the final 7 missing fields cases"""

import json
from pathlib import Path

# Load validation report
report_path = Path('.devkit/analysis/validation_report_v3.json')
with open(report_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

etymology_issues = data['discrepancies']['etymology_mismatch']
missing_fields_issues = [e for e in etymology_issues if e.get('type') == 'missing_etymology_fields']

print("=" * 80)
print(f"INVESTIGATING FINAL {len(missing_fields_issues)} MISSING FIELDS CASES")
print("=" * 80)

for i, issue in enumerate(missing_fields_issues, 1):
    root = issue['root']
    missing = issue.get('missing', [])
    original = issue.get('original', {})
    docx = issue.get('docx', {})

    print(f"\n{'=' * 80}")
    print(f"{i}. ROOT: {root}")
    print(f"{'=' * 80}")
    print(f"Missing fields: {missing}")
    print(f"\nOriginal etymology:")
    print(json.dumps(original, indent=2, ensure_ascii=False))
    print(f"\nDOCX etymology:")
    print(json.dumps(docx, indent=2, ensure_ascii=False))

    # Load actual DOCX file to see full etymology
    docx_path = Path(f'.devkit/analysis/docx_v2_verbs/{root}.json')
    if docx_path.exists():
        with open(docx_path, 'r', encoding='utf-8') as f:
            verb = json.load(f)
            print(f"\nFull DOCX etymology:")
            print(json.dumps(verb.get('etymology'), indent=2, ensure_ascii=False))

print(f"\n{'=' * 80}")
print("ANALYSIS")
print(f"{'=' * 80}")
print("""
These 7 cases likely represent:
1. Non-standard etymology formats (e.g., "see Tezel", corpus references)
2. Genuinely different data in DOCX vs original
3. Edge cases that need special handling
4. Original parser using different extraction logic

Decision: Assess whether each is:
- ACCEPTABLE: Different but valid etymology structure
- FIXABLE: Can improve parser to match original
- DATA ISSUE: DOCX source doesn't contain the data
""")
