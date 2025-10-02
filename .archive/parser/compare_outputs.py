#!/usr/bin/env python3
"""
Compare old (buggy) vs new (clean) extraction output
Validates the improvements
"""

import json
from pathlib import Path
import re

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_word_fragmentation(text):
    """Check for suspicious word fragments"""
    # Pattern: single char/syllable with spaces around it
    fragments = re.findall(r'\b[ʔʕḥṭəbdēaioug]\s+[ʔʕḥṭəbdēaioug]\b', text)
    return len(fragments)

def check_whitespace_noise(text):
    """Check for tabs/newlines"""
    return '\t' in text or '\n' in text

def analyze_dataset(data, name):
    """Analyze quality of dataset"""
    print(f"\n{'='*70}")
    print(f"ANALYSIS: {name}")
    print('='*70)

    verbs = data['verbs']
    total_examples = 0
    fragmented_examples = 0
    whitespace_issues = 0

    for verb in verbs:
        for stem in verb.get('stems', []):
            for conj_type, examples in stem.get('conjugations', {}).items():
                for ex in examples:
                    total_examples += 1

                    turoyo = ex.get('turoyo', '')

                    # Check fragmentation
                    frags = check_word_fragmentation(turoyo)
                    if frags > 0:
                        fragmented_examples += 1

                    # Check whitespace
                    if check_whitespace_noise(turoyo):
                        whitespace_issues += 1

    print(f"\n📊 Statistics:")
    print(f"  Total verbs: {len(verbs)}")
    print(f"  Total examples: {total_examples}")
    print(f"  Word fragmentation issues: {fragmented_examples} ({fragmented_examples/total_examples*100:.1f}%)")
    print(f"  Whitespace noise (tabs/newlines): {whitespace_issues} ({whitespace_issues/total_examples*100:.1f}%)")

    return {
        'total_examples': total_examples,
        'fragmented': fragmented_examples,
        'whitespace': whitespace_issues
    }

def compare_examples(old_data, new_data):
    """Side-by-side comparison of specific examples"""
    print(f"\n{'='*70}")
    print("SIDE-BY-SIDE COMPARISON")
    print('='*70)

    old_verbs = {v['root']: v for v in old_data['verbs']}
    new_verbs = {v['root']: v for v in new_data['verbs']}

    # Test cases
    test_roots = ['ʕbd', 'ʕbr', 'ʔbʕ']

    for root in test_roots:
        if root not in old_verbs or root not in new_verbs:
            continue

        print(f"\n\n🔍 Root: {root}")
        print("-" * 70)

        old_verb = old_verbs[root]
        new_verb = new_verbs[root]

        # Compare first example from first stem
        if old_verb['stems'] and new_verb['stems']:
            old_stem = old_verb['stems'][0]
            new_stem = new_verb['stems'][0]

            old_conjs = old_stem['conjugations']
            new_conjs = new_stem['conjugations']

            # Get first conjugation type
            if old_conjs and new_conjs:
                conj_type = list(old_conjs.keys())[0]

                if conj_type in old_conjs and conj_type in new_conjs:
                    old_ex = old_conjs[conj_type][0]
                    new_ex = new_conjs[conj_type][0]

                    print(f"\n{conj_type}:")
                    print(f"\nOLD (buggy):")
                    print(f"  Turoyo: {old_ex['turoyo'][:100]}...")

                    print(f"\nNEW (clean):")
                    print(f"  Turoyo: {new_ex['turoyo'][:100]}...")

                    # Highlight improvements
                    old_frags = check_word_fragmentation(old_ex['turoyo'])
                    new_frags = check_word_fragmentation(new_ex['turoyo'])

                    old_ws = check_whitespace_noise(old_ex['turoyo'])
                    new_ws = check_whitespace_noise(new_ex['turoyo'])

                    if old_frags > new_frags or old_ws and not new_ws:
                        print(f"\n  ✅ IMPROVED:")
                        if old_frags > new_frags:
                            print(f"     - Word fragments: {old_frags} → {new_frags}")
                        if old_ws and not new_ws:
                            print(f"     - Whitespace noise: FIXED")

def main():
    old_file = Path('data/verbs_final.json')
    new_file = Path('data/verbs_clean_v2.json')

    if not old_file.exists() or not new_file.exists():
        print("❌ Missing data files")
        return

    print("📊 Loading datasets...")
    old_data = load_data(old_file)
    new_data = load_data(new_file)

    old_stats = analyze_dataset(old_data, "OLD (Buggy)")
    new_stats = analyze_dataset(new_data, "NEW (Clean)")

    # Summary comparison
    print(f"\n\n{'='*70}")
    print("IMPROVEMENT SUMMARY")
    print('='*70)

    print(f"\n🎯 Fragmentation Fix:")
    old_frag_rate = old_stats['fragmented'] / old_stats['total_examples'] * 100
    new_frag_rate = new_stats['fragmented'] / new_stats['total_examples'] * 100
    improvement = old_frag_rate - new_frag_rate
    print(f"  {old_frag_rate:.1f}% → {new_frag_rate:.1f}%  ({improvement:+.1f}% improvement)")

    print(f"\n🎯 Whitespace Fix:")
    old_ws_rate = old_stats['whitespace'] / old_stats['total_examples'] * 100
    new_ws_rate = new_stats['whitespace'] / new_stats['total_examples'] * 100
    ws_improvement = old_ws_rate - new_ws_rate
    print(f"  {old_ws_rate:.1f}% → {new_ws_rate:.1f}%  ({ws_improvement:+.1f}% improvement)")

    # Side-by-side
    compare_examples(old_data, new_data)

    print(f"\n\n✅ VALIDATION COMPLETE\n")

if __name__ == '__main__':
    main()
