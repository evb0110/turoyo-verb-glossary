#!/usr/bin/env python3
"""Check if the 5 missing etymologies are now extracted"""

import json
from pathlib import Path

# The 5 roots that were missing etymology
missing_roots = ['dyq 1', 'frʕ 2', 'gwlʕ', 'ʕyr 1', 'ḏyr']

print("=" * 80)
print("CHECKING IF MISSING ETYMOLOGIES ARE NOW EXTRACTED")
print("=" * 80)

for root in missing_roots:
    docx_path = Path(f'.devkit/analysis/docx_v2_verbs/{root}.json')

    if not docx_path.exists():
        print(f"\n❌ {root}: FILE NOT FOUND")
        continue

    with open(docx_path, 'r', encoding='utf-8') as f:
        verb = json.load(f)

    etymology = verb.get('etymology')

    print(f"\n{'=' * 80}")
    print(f"ROOT: {root}")
    print(f"{'=' * 80}")

    if etymology:
        print(f"✅ ETYMOLOGY EXTRACTED:")
        print(json.dumps(etymology, indent=2, ensure_ascii=False))
    else:
        print(f"❌ STILL MISSING")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
