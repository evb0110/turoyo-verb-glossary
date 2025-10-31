#!/usr/bin/env python3
"""Check the NEW validation report (just generated)"""

import json
from pathlib import Path

report_path = Path('.devkit/analysis/validation_report_v3.json')
with open(report_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("NEW VALIDATION REPORT ANALYSIS")
print("=" * 80)

# Check structure
if 'discrepancies' in data:
    discreps = data['discrepancies']
    if isinstance(discreps, dict):
        print(f"\nDiscrepancy types:")
        for key in discreps.keys():
            value = discreps[key]
            if isinstance(value, list):
                print(f"  {key}: {len(value)} issues")
            else:
                print(f"  {key}: {value}")

        # Check etymology issues specifically
        if 'etymology_mismatch' in discreps:
            etym_issues = discreps['etymology_mismatch']
            print(f"\n{'=' * 80}")
            print(f"ETYMOLOGY ISSUES: {len(etym_issues)}")
            print(f"{'=' * 80}")

            # Categorize
            missing_etym = [e for e in etym_issues if e.get('type') == 'missing_etymology']
            extra_etym = [e for e in etym_issues if e.get('type') == 'extra_etymology']
            missing_fields = [e for e in etym_issues if e.get('type') == 'missing_etymology_fields']

            print(f"\n  Missing etymology: {len(missing_etym)}")
            print(f"  Extra etymology: {len(extra_etym)}")
            print(f"  Missing fields: {len(missing_fields)}")

            # Show missing etymologies (should be 0 or very few now)
            if missing_etym:
                print(f"\n  STILL MISSING ETYMOLOGY:")
                for e in missing_etym[:10]:
                    print(f"    - {e.get('root')}")

            # Show missing fields examples
            if missing_fields:
                print(f"\n  MISSING FIELDS (first 10):")
                for e in missing_fields[:10]:
                    print(f"    - {e.get('root')}: {e.get('missing', [])}")
