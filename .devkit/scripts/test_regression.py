#!/usr/bin/env python3
"""
REGRESSION TEST: Verify fix didn't break other verbs
"""

import json
from pathlib import Path

print("=" * 80)
print("REGRESSION TEST: Checking other verbs for etymology integrity")
print("=" * 80)

# Test cases: verbs with known complete etymologies
test_cases = [
    {
        'root': 'bdl',
        'expected_substring': 'verändern',
        'description': 'Standard multi-word etymology'
    },
    {
        'root': 'brz',
        'expected_substring': 'hervortreten',
        'description': 'Etymology with "or" in translation (previously broke)'
    },
    {
        'root': 'pčq',
        'expected_substring': 'to crush, press, smash, squash, KED 107',
        'description': 'The fixed verb - malformed parentheses'
    },
    {
        'root': 'ḏyr',
        'expected_substring': 'harm',
        'description': 'Missing opening paren pattern'
    },
    {
        'root': 'šrqm',
        'expected_substring': 'denom',
        'description': 'Denominal pattern'
    }
]

verb_dir = Path('server/assets/verbs')
passed = 0
failed = 0

for test in test_cases:
    root = test['root']
    expected = test['expected_substring']
    desc = test['description']

    verb_file = verb_dir / f"{root}.json"

    if not verb_file.exists():
        print(f"\n❌ {root}: File not found!")
        failed += 1
        continue

    with open(verb_file, 'r', encoding='utf-8') as f:
        verb = json.load(f)

    etymology = verb.get('etymology')

    if not etymology:
        print(f"\n❌ {root} ({desc}): No etymology!")
        failed += 1
        continue

    # Get etymology text (handle different structures)
    etym_text = ''
    if 'etymons' in etymology and etymology['etymons']:
        first_etymon = etymology['etymons'][0]
        etym_text = str(first_etymon)

    if expected.lower() in etym_text.lower():
        print(f"\n✅ {root} ({desc}): Etymology intact")
        print(f"   Contains: {repr(expected)}")
        passed += 1
    else:
        print(f"\n❌ {root} ({desc}): Etymology missing expected content!")
        print(f"   Expected substring: {repr(expected)}")
        print(f"   Actual etymology: {etym_text[:200]}")
        failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 80)

if failed == 0:
    print("\n🎉 All tests passed! No regression detected.")
else:
    print(f"\n⚠️  {failed} test(s) failed! Please investigate.")
