#!/usr/bin/env python3
"""
Inspect the remaining 19 fragmentation cases
"""

import json
from pathlib import Path
import re

def check_word_fragmentation(text):
    """Check for suspicious word fragments"""
    # Pattern: single char/syllable with spaces around it
    fragments = re.findall(r'\b[ʔʕḥṭəbdēaioug]\s+[ʔʕḥṭəbdēaioug]\b', text)
    return fragments

def main():
    data_file = Path('data/verbs_clean_v2.json')

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("🔍 Inspecting remaining fragmentation cases...\n")

    fragmented_examples = []

    for verb in data['verbs']:
        for stem in verb.get('stems', []):
            for conj_type, examples in stem.get('conjugations', {}).items():
                for ex in examples:
                    turoyo = ex.get('turoyo', '')
                    frags = check_word_fragmentation(turoyo)

                    if frags:
                        fragmented_examples.append({
                            'root': verb['root'],
                            'stem': stem['stem'],
                            'conjugation': conj_type,
                            'turoyo': turoyo,
                            'fragments': frags
                        })

    print(f"Found {len(fragmented_examples)} fragmented examples\n")
    print("="*80)

    # Show first 10
    for i, ex in enumerate(fragmented_examples[:10], 1):
        print(f"\n{i}. Root: {ex['root']} ({ex['stem']} - {ex['conjugation']})")
        print(f"   Fragments: {ex['fragments']}")
        print(f"   Text: {ex['turoyo'][:150]}...")
        print("-"*80)

    if len(fragmented_examples) > 10:
        print(f"\n... and {len(fragmented_examples) - 10} more cases")

if __name__ == '__main__':
    main()
