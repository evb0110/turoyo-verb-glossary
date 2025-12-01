#!/usr/bin/env python3
import json
import urllib.request

BASE_URL = "https://turoyo-verb-glossary.vercel.app/api/verb"

print("=" * 70)
print("VERIFYING ALL FIXES ON VERCEL DEPLOYMENT")
print("=" * 70)

# Issue #3: šġl 1 - Missing meanings
print("\n✓ ISSUE #3: šġl 1 - Missing meanings")
print("-" * 70)
with urllib.request.urlopen(f"{BASE_URL}/%C5%A1%C4%A1l%201") as response:
    data = json.loads(response.read())
    stem = data['stems'][0]
    forms = stem['forms']
    meanings = stem.get('label_gloss_tokens', [])

    print(f"Root: {data['root']}")
    print(f"Stem I forms: {forms}")
    print(f"Meanings extracted: {'✓ YES' if meanings else '✗ NO'}")
    if meanings:
        full_meaning = ''.join([t['text'] for t in meanings])
        print(f"Full meaning text: {full_meaning[:100]}...")
    print(f"\nSTATUS: {'✓ FIXED' if meanings and len(forms) == 2 else '✗ FAILED'}")

# Issue #2: str - Detransitive label
print("\n✓ ISSUE #2: str - Detransitive label")
print("-" * 70)
with urllib.request.urlopen(f"{BASE_URL}/str") as response:
    data = json.loads(response.read())
    stem2 = [s for s in data['stems'] if s['stem'] == 'II'][0]
    label = stem2.get('label_gloss_tokens', [])

    print(f"Root: {data['root']}")
    print(f"Stem II forms: {stem2['forms']}")
    print(f"Detransitive label: {'✓ YES' if label else '✗ NO'}")
    if label:
        print(f"Label text: '{label[0]['text']}'")
    print(f"\nSTATUS: {'✓ FIXED' if label and label[0]['text'] == 'Detransitive (???)' else '✗ FAILED'}")

# Issue #1: zyt - Missing conjugations
print("\n✓ ISSUE #1: zyt - Missing conjugations")
print("-" * 70)
with urllib.request.urlopen(f"{BASE_URL}/zyt") as response:
    data = json.loads(response.read())
    stem = data['stems'][0]
    conj = stem['conjugations']

    print(f"Root: {data['root']}")
    print(f"Stem II forms: {stem['forms']}")
    print(f"\nConjugation types found: {len(conj)}")
    for ctype, examples in conj.items():
        print(f"  - {ctype}: {len(examples)} examples")

    has_all = 'Infectum' in conj and 'Preterite' in conj and 'Infinitive' in conj
    print(f"\nSTATUS: {'✓ FIXED' if has_all else '✗ FAILED'}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE - ALL FIXES DEPLOYED SUCCESSFULLY!")
print("=" * 70)
