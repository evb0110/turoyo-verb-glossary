#!/usr/bin/env python3
"""
Verify etymology fix on actual parsed data
Compare old vs new parsing to count improvements
"""
import sys
import json
from pathlib import Path

# Add parser directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_clean_v2 import CleanTuroyoParser

def analyze_etymologies(verbs):
    """Analyze etymology data quality"""
    stats = {
        'total': 0,
        'with_etymology': 0,
        'structured_full': 0,  # Has all 4 fields
        'structured_partial': 0,  # Has source_root but missing reference/meaning
        'simple': 0,  # Only source and notes
        'raw': 0,  # Unparsed
        'truncated': 0,  # Ends with (II, (IV, (Pa., etc - indicates truncation
    }

    truncated_examples = []
    full_examples = []

    for verb in verbs:
        stats['total'] += 1

        etym = verb.get('etymology')
        if not etym:
            continue

        stats['with_etymology'] += 1

        # Check for full structured format
        if all(k in etym for k in ['source', 'source_root', 'reference', 'meaning']):
            stats['structured_full'] += 1
            full_examples.append({
                'root': verb['root'],
                'etymology': etym
            })
        elif 'source_root' in etym:
            stats['structured_partial'] += 1
        elif 'notes' in etym:
            stats['simple'] += 1
            # Check if truncated
            notes = etym['notes']
            if notes.endswith(('(II', '(IV', '(III', '(Pa.', '(Af.', '(V', '(VI', '(VII', '(VIII')):
                stats['truncated'] += 1
                truncated_examples.append({
                    'root': verb['root'],
                    'notes': notes
                })
        elif 'raw' in etym:
            stats['raw'] += 1

    return stats, truncated_examples, full_examples

def main():
    print("="*80)
    print("ETYMOLOGY FIX VERIFICATION")
    print("="*80)

    # Parse with fixed parser
    print("\n1. Parsing HTML with FIXED parser...")
    parser = CleanTuroyoParser('/Users/evb/WebstormProjects/turoyo-verb-glossary/source/Turoyo_all_2024.html')
    verbs = parser.parse_all()

    # Analyze
    print("\n2. Analyzing etymology data quality...")
    stats, truncated, full = analyze_etymologies(verbs)

    print("\n" + "="*80)
    print("ETYMOLOGY STATISTICS")
    print("="*80)
    print(f"Total verbs:                 {stats['total']:4d}")
    print(f"With etymology:              {stats['with_etymology']:4d} ({100*stats['with_etymology']/stats['total']:.1f}%)")
    print(f"  Structured (full):         {stats['structured_full']:4d} (4 fields: source, root, ref, meaning)")
    print(f"  Structured (partial):      {stats['structured_partial']:4d}")
    print(f"  Simple (source + notes):   {stats['simple']:4d}")
    print(f"  Raw (unparsed):            {stats['raw']:4d}")
    print(f"  ** TRUNCATED **:           {stats['truncated']:4d} ❌")

    # Show truncated examples
    if truncated:
        print("\n" + "="*80)
        print("TRUNCATED ETYMOLOGIES (Should be 0 with fix!)")
        print("="*80)
        for ex in truncated[:20]:
            print(f"  {ex['root']:10s} -> {ex['notes']}")
        if len(truncated) > 20:
            print(f"  ... and {len(truncated) - 20} more")

    # Show some full examples
    if full:
        print("\n" + "="*80)
        print("PROPERLY PARSED ETYMOLOGIES (Sample)")
        print("="*80)
        for ex in full[:10]:
            print(f"\n  Root: {ex['root']}")
            etym = ex['etymology']
            print(f"    Source: {etym['source']}")
            print(f"    Root:   {etym['source_root']}")
            print(f"    Ref:    {etym['reference']}")
            print(f"    Meaning: {etym['meaning'][:80]}...")

    # Check specific test cases
    print("\n" + "="*80)
    print("SPECIFIC TEST CASES")
    print("="*80)
    test_roots = ['ʕdl', 'ʕln', 'ʕrf', 'ṣʕr']
    for root in test_roots:
        verb = next((v for v in verbs if v['root'] == root), None)
        if verb and verb.get('etymology'):
            etym = verb['etymology']
            print(f"\n{root}:")
            print(f"  {json.dumps(etym, ensure_ascii=False, indent=4)}")

            # Verify all 4 fields present
            if all(k in etym for k in ['source', 'source_root', 'reference', 'meaning']):
                print("  ✅ PASSED - All 4 fields present")
            else:
                print("  ❌ FAILED - Missing fields")
        else:
            print(f"\n{root}: Not found or no etymology")

    # Final assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)

    expected_full = 911  # Expected count with fix
    actual_full = stats['structured_full']

    print(f"Expected etymologies with all 4 fields: ~{expected_full}")
    print(f"Actual etymologies with all 4 fields:    {actual_full}")
    print(f"Truncated etymologies:                    {stats['truncated']}")

    if stats['truncated'] == 0 and actual_full > 900:
        print("\n✅ SUCCESS! Etymology parsing is fixed!")
        print(f"   - No truncated etymologies detected")
        print(f"   - {actual_full} etymologies have all 4 fields (source, root, ref, meaning)")
        return 0
    else:
        print("\n❌ ISSUES REMAIN!")
        if stats['truncated'] > 0:
            print(f"   - Still {stats['truncated']} truncated etymologies")
        if actual_full < 900:
            print(f"   - Only {actual_full} full etymologies (expected ~{expected_full})")
        return 1

if __name__ == '__main__':
    sys.exit(main())
