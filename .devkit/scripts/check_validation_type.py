#!/usr/bin/env python3
"""Check validation report data types"""

import json
from pathlib import Path

report_path = Path('.devkit/analysis/validation_report_v2.json')
with open(report_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

discreps = data.get('discrepancies', [])
print(f"Type of discrepancies: {type(discreps)}")
print(f"Length: {len(discreps)}")

if isinstance(discreps, dict):
    print(f"Keys: {list(discreps.keys())}")
    for key in list(discreps.keys())[:3]:
        print(f"\n{key}:")
        print(json.dumps(discreps[key], indent=2, ensure_ascii=False)[:500])
