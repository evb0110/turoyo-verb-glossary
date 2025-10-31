#!/usr/bin/env python3
"""Check validation report structure"""

import json
from pathlib import Path

report_path = Path('.devkit/analysis/validation_report_v2.json')
with open(report_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("VALIDATION REPORT STRUCTURE")
print("=" * 80)
print(f"\nKeys: {list(data.keys())}")

stats = data.get('stats', {})
print(f"\nStats:")
print(json.dumps(stats, indent=2, ensure_ascii=False))

discreps = data.get('discrepancies', [])
print(f"\nTotal discrepancies: {len(discreps)}")

if discreps:
    print("\nFirst 3 discrepancies:")
    for i, d in enumerate(discreps[:3], 1):
        print(f"\n{i}. {json.dumps(d, indent=2, ensure_ascii=False)}")

# Check if there are any etymology-specific issues
print("\n\nChecking for etymology fields in discrepancies...")
etymology_count = 0
for d in discreps:
    if 'etymology' in str(d).lower():
        etymology_count += 1
        if etymology_count <= 5:
            print(f"\nEtymology-related discrepancy:")
            print(json.dumps(d, indent=2, ensure_ascii=False))

print(f"\nTotal etymology-related discrepancies: {etymology_count}")
