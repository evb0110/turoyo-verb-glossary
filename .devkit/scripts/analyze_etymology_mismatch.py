#!/usr/bin/env python3
"""Analyze etymology mismatches in detail"""

import json
from pathlib import Path

report_path = Path('.devkit/analysis/validation_report_v2.json')
with open(report_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

etymology_issues = data.get('discrepancies', {}).get('etymology_mismatch', [])

print("=" * 80)
print(f"ETYMOLOGY MISMATCH ANALYSIS: {len(etymology_issues)} issues")
print("=" * 80)

if not etymology_issues:
    print("\n✅ NO ETYMOLOGY ISSUES FOUND! 100% accuracy achieved!")
    exit(0)

# Show all etymology issues
for i, issue in enumerate(etymology_issues, 1):
    print(f"\n{'=' * 80}")
    print(f"{i}. ROOT: {issue.get('root')}")
    print(f"{'=' * 80}")
    print(json.dumps(issue, indent=2, ensure_ascii=False))

# Save for detailed analysis
output_path = Path('.devkit/analysis/etymology_mismatch_detailed.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(etymology_issues, f, ensure_ascii=False, indent=2)

print(f"\n\n💾 Saved detailed etymology issues: {output_path}")
