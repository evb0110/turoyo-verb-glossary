#!/usr/bin/env python3
"""Investigate the 298 missing fields cases"""

import json
from pathlib import Path

# Load validation report
report_path = Path('.devkit/analysis/validation_report_v3.json')
with open(report_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

etymology_issues = data['discrepancies']['etymology_mismatch']
missing_fields_issues = [e for e in etymology_issues if e.get('type') == 'missing_etymology_fields']

print("=" * 80)
print(f"INVESTIGATING {len(missing_fields_issues)} MISSING FIELDS CASES")
print("=" * 80)

# Categorize by what fields are missing
field_patterns = {}
for issue in missing_fields_issues:
    missing = tuple(sorted(issue.get('missing', [])))
    if missing not in field_patterns:
        field_patterns[missing] = []
    field_patterns[missing].append(issue)

print(f"\nField patterns:")
for pattern, issues in sorted(field_patterns.items(), key=lambda x: -len(x[1])):
    print(f"  Missing {list(pattern)}: {len(issues)} cases")

# Investigate top pattern
top_pattern = max(field_patterns.items(), key=lambda x: len(x[1]))
print(f"\n{'=' * 80}")
print(f"TOP PATTERN: Missing {list(top_pattern[0])} ({len(top_pattern[1])} cases)")
print(f"{'=' * 80}")

# Show 5 examples
for i, issue in enumerate(top_pattern[1][:5], 1):
    root = issue['root']
    print(f"\n{i}. ROOT: {root}")
    print(f"   Original: {json.dumps(issue.get('original'), ensure_ascii=False)}")
    print(f"   DOCX:     {json.dumps(issue.get('docx'), ensure_ascii=False)}")

    # Load the actual DOCX file to see what was extracted
    docx_path = Path(f'.devkit/analysis/docx_v2_verbs/{root}.json')
    if docx_path.exists():
        with open(docx_path, 'r', encoding='utf-8') as f:
            verb = json.load(f)
            print(f"   Full DOCX etymology: {json.dumps(verb.get('etymology'), ensure_ascii=False)}")

print(f"\n{'=' * 80}")
print("ANALYSIS")
print(f"{'=' * 80}")
print("""
The missing fields likely fall into these categories:
1. Truncated extraction - parser cuts off mid-text
2. Different etymology structure in DOCX vs original
3. Nested parentheses confusing the parser
4. Multi-line text not fully captured

Root cause: Need to improve the parser to extract complete structured fields.
""")
