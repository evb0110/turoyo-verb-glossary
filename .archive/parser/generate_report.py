#!/usr/bin/env python3
"""
Generate comprehensive statistics report for the clean dataset
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def main():
    data_file = Path('data/verbs_clean_v2.json')

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    verbs = data['verbs']
    metadata = data.get('metadata', {})

    # Statistics
    stats = {
        'total_verbs': len(verbs),
        'cross_references': 0,
        'uncertain_entries': 0,
        'with_etymology': 0,
        'etymology_sources': Counter(),
        'binyanim': Counter(),
        'conjugation_types': Counter(),
        'total_stems': 0,
        'total_examples': 0,
        'verbs_with_multiple_stems': 0,
        'roots_by_length': Counter(),
    }

    # Analyze
    for verb in verbs:
        root = verb['root']
        stats['roots_by_length'][len(root)] += 1

        if verb.get('cross_reference'):
            stats['cross_references'] += 1
            continue

        if verb.get('uncertain'):
            stats['uncertain_entries'] += 1

        if verb.get('etymology'):
            stats['with_etymology'] += 1
            source = verb['etymology'].get('source', 'Unknown')
            stats['etymology_sources'][source] += 1

        stems = verb.get('stems', [])
        stats['total_stems'] += len(stems)

        if len(stems) > 1:
            stats['verbs_with_multiple_stems'] += 1

        for stem in stems:
            binyan = stem.get('binyan', 'Unknown')
            stats['binyanim'][binyan] += 1

            for conj_type, examples in stem.get('conjugations', {}).items():
                stats['conjugation_types'][conj_type] += len(examples)
                stats['total_examples'] += len(examples)

    # Generate report
    print("="*80)
    print("TUROYO VERB GLOSSARY - EXTRACTION REPORT")
    print("="*80)

    print(f"\n📚 DATASET OVERVIEW")
    print(f"   Parser version: {metadata.get('parser_version', 'N/A')}")
    print(f"   Total verbs: {stats['total_verbs']:,}")
    print(f"   Total stems: {stats['total_stems']:,}")
    print(f"   Total examples: {stats['total_examples']:,}")
    print(f"   Cross-references: {stats['cross_references']}")
    print(f"   Uncertain entries: {stats['uncertain_entries']}")

    print(f"\n📖 ROOT STRUCTURE")
    for length in sorted(stats['roots_by_length'].keys()):
        count = stats['roots_by_length'][length]
        pct = count / stats['total_verbs'] * 100
        print(f"   {length}-letter roots: {count:4} ({pct:5.1f}%)")

    print(f"\n🌍 ETYMOLOGY")
    print(f"   Verbs with etymology: {stats['with_etymology']} ({stats['with_etymology']/stats['total_verbs']*100:.1f}%)")
    print(f"\n   Sources:")
    for source, count in stats['etymology_sources'].most_common():
        pct = count / stats['with_etymology'] * 100
        print(f"     {source:12} {count:4} ({pct:5.1f}%)")

    print(f"\n🔤 BINYANIM (STEMS)")
    print(f"   Verbs with multiple stems: {stats['verbs_with_multiple_stems']}")
    print(f"\n   Distribution:")
    for binyan, count in sorted(stats['binyanim'].items(), key=lambda x: (x[0] not in ['I', 'II', 'III'], x[0])):
        pct = count / stats['total_stems'] * 100
        print(f"     {binyan:15} {count:4} ({pct:5.1f}%)")

    print(f"\n📝 CONJUGATION TYPES")
    print(f"   Total conjugation examples: {stats['total_examples']:,}")
    print(f"\n   Top 15 types:")
    for i, (conj_type, count) in enumerate(stats['conjugation_types'].most_common(15), 1):
        pct = count / stats['total_examples'] * 100
        print(f"     {i:2}. {conj_type:30} {count:4} ({pct:5.1f}%)")

    # Sample verbs
    print(f"\n\n📋 SAMPLE ENTRIES")
    print("="*80)

    # Find interesting examples
    samples = []

    # Verb with most stems
    max_stems_verb = max(verbs, key=lambda v: len(v.get('stems', [])))
    samples.append(("Most stems", max_stems_verb))

    # Verb with most examples
    max_examples_verb = max(verbs, key=lambda v: sum(
        len(conj_data)
        for stem in v.get('stems', [])
        for conj_data in stem.get('conjugations', {}).values()
    ))
    samples.append(("Most examples", max_examples_verb))

    # First verb
    samples.append(("First in dataset", verbs[0]))

    for label, verb in samples:
        print(f"\n{label}: {verb['root']}")
        print(f"  Stems: {len(verb.get('stems', []))}")

        total_ex = sum(
            len(conj_data)
            for stem in verb.get('stems', [])
            for conj_data in stem.get('conjugations', {}).values()
        )
        print(f"  Examples: {total_ex}")

        if verb.get('etymology'):
            etym = verb['etymology']
            print(f"  Etymology: {etym.get('source', 'N/A')}", end='')
            if 'source_root' in etym:
                print(f" < {etym['source_root']}")
            else:
                print()

        print(f"  Forms: ", end='')
        forms = []
        for stem in verb.get('stems', []):
            forms.extend(stem.get('forms', []))
        print(', '.join(forms[:5]))

        print("-"*80)

    print("\n✅ Report complete!")

    # Save summary
    summary_file = Path('data/extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'statistics': {
                'total_verbs': stats['total_verbs'],
                'total_stems': stats['total_stems'],
                'total_examples': stats['total_examples'],
                'cross_references': stats['cross_references'],
                'uncertain_entries': stats['uncertain_entries'],
                'with_etymology': stats['with_etymology'],
            },
            'etymology_sources': dict(stats['etymology_sources']),
            'binyanim': dict(stats['binyanim']),
            'top_conjugations': dict(stats['conjugation_types'].most_common(20)),
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Summary saved to: {summary_file}")

if __name__ == '__main__':
    main()
