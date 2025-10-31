#!/usr/bin/env python3
"""
Comprehensive Data Quality Audit for Turoyo Verb Glossary

Analyzes all verb JSON files and generates a detailed quality report.
"""

import json
import os
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any, Set
import statistics

# ANSI color codes
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_all_verbs(verbs_dir: str) -> List[Dict[str, Any]]:
    """Load all verb JSON files."""
    verbs = []
    json_files = sorted(Path(verbs_dir).glob('*.json'))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                verb = json.load(f)
                verb['_filename'] = json_file.name
                verbs.append(verb)
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}ERROR: Failed to parse {json_file.name}: {e}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}ERROR: Failed to load {json_file.name}: {e}{Colors.END}")

    return verbs

def audit_verbs(verbs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Perform comprehensive audit on all verbs."""

    audit = {
        'total_verbs': len(verbs),
        'total_stems': 0,
        'total_examples': 0,
        'total_etymology_entries': 0,

        # Quality issues
        'empty_turoyo_fields': [],
        'empty_translation_arrays': [],
        'verbs_without_stems': [],
        'verbs_without_examples': [],
        'malformed_structure': [],
        'duplicate_roots': [],

        # Etymology analysis
        'etymology_null': [],
        'etymology_partial': [],
        'etymology_complete': [],
        'etymology_arabic_only': [],
        'etymology_kurdish_only': [],
        'etymology_both_sources': [],

        # Statistical data
        'stems_per_verb': [],
        'examples_per_verb': [],
        'examples_per_stem': [],
        'stem_distribution': Counter(),

        # Translation quality
        'examples_missing_all_translations': [],
        'examples_with_some_translations': [],
        'examples_with_all_translations': [],

        # Empty field tracking
        'empty_turoyo_by_type': defaultdict(list),
    }

    seen_roots = {}

    for verb in verbs:
        root = verb.get('root', 'UNKNOWN')
        filename = verb.get('_filename', 'UNKNOWN')

        # Check for duplicate roots
        if root in seen_roots:
            audit['duplicate_roots'].append({
                'root': root,
                'files': [seen_roots[root], filename]
            })
        else:
            seen_roots[root] = filename

        # Validate structure
        try:
            if not isinstance(verb.get('root'), str):
                audit['malformed_structure'].append({
                    'root': root,
                    'issue': 'root is not a string'
                })
            if not isinstance(verb.get('stems'), list):
                audit['malformed_structure'].append({
                    'root': root,
                    'issue': 'stems is not a list'
                })
        except Exception as e:
            audit['malformed_structure'].append({
                'root': root,
                'issue': str(e)
            })
            continue

        # Etymology analysis (new structure with etymons array)
        etymology = verb.get('etymology')
        if etymology is None or not etymology.get('etymons'):
            audit['etymology_null'].append(root)
        else:
            etymons = etymology.get('etymons', [])
            audit['total_etymology_entries'] += len(etymons)

            # Categorize by source languages
            sources = set()
            for etymon in etymons:
                source = etymon.get('source', '').lower()
                if 'arab' in source:
                    sources.add('arabic')
                elif 'kurd' in source:
                    sources.add('kurdish')

            if 'arabic' in sources and 'kurdish' in sources:
                audit['etymology_both_sources'].append(root)
                audit['etymology_complete'].append(root)
            elif 'arabic' in sources:
                audit['etymology_arabic_only'].append(root)
                audit['etymology_partial'].append(root)
            elif 'kurdish' in sources:
                audit['etymology_kurdish_only'].append(root)
                audit['etymology_partial'].append(root)
            else:
                audit['etymology_null'].append(root)

        # Stems analysis
        stems = verb.get('stems', [])
        if not stems:
            audit['verbs_without_stems'].append(root)

        audit['total_stems'] += len(stems)
        audit['stems_per_verb'].append(len(stems))

        verb_examples_count = 0

        for stem in stems:
            stem_name = stem.get('stem', 'UNKNOWN')
            audit['stem_distribution'][stem_name] += 1

            # New structure: conjugations contain tense groups with arrays of examples
            conjugations = stem.get('conjugations', {})
            stem_examples = []

            for tense, examples in conjugations.items():
                if isinstance(examples, list):
                    stem_examples.extend(examples)

            verb_examples_count += len(stem_examples)
            audit['total_examples'] += len(stem_examples)

            if stem_examples:
                audit['examples_per_stem'].append(len(stem_examples))

            # Analyze examples for empty fields
            for example in stem_examples:
                turoyo = example.get('turoyo', '').strip()
                translations = example.get('translations', [])

                # Empty Turoyo field
                if not turoyo:
                    audit['empty_turoyo_fields'].append({
                        'root': root,
                        'stem': stem_name,
                        'translations': translations,
                        'type': 'example'
                    })
                    audit['empty_turoyo_by_type']['example'].append(root)

                # Translation analysis
                if not translations:
                    audit['empty_translation_arrays'].append({
                        'root': root,
                        'stem': stem_name,
                        'turoyo': turoyo
                    })
                    audit['examples_missing_all_translations'].append(root)
                elif all(t.strip() for t in translations):
                    audit['examples_with_all_translations'].append(root)
                else:
                    audit['examples_with_some_translations'].append(root)

        audit['examples_per_verb'].append(verb_examples_count)

        if verb_examples_count == 0:
            audit['verbs_without_examples'].append(root)

    return audit

def calculate_statistics(audit: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate statistical metrics."""
    stats = {}

    # Stems per verb
    if audit['stems_per_verb']:
        stats['stems_per_verb'] = {
            'mean': statistics.mean(audit['stems_per_verb']),
            'median': statistics.median(audit['stems_per_verb']),
            'min': min(audit['stems_per_verb']),
            'max': max(audit['stems_per_verb']),
            'stdev': statistics.stdev(audit['stems_per_verb']) if len(audit['stems_per_verb']) > 1 else 0
        }

    # Examples per verb
    if audit['examples_per_verb']:
        stats['examples_per_verb'] = {
            'mean': statistics.mean(audit['examples_per_verb']),
            'median': statistics.median(audit['examples_per_verb']),
            'min': min(audit['examples_per_verb']),
            'max': max(audit['examples_per_verb']),
            'stdev': statistics.stdev(audit['examples_per_verb']) if len(audit['examples_per_verb']) > 1 else 0
        }

    # Examples per stem
    if audit['examples_per_stem']:
        stats['examples_per_stem'] = {
            'mean': statistics.mean(audit['examples_per_stem']),
            'median': statistics.median(audit['examples_per_stem']),
            'min': min(audit['examples_per_stem']),
            'max': max(audit['examples_per_stem']),
            'stdev': statistics.stdev(audit['examples_per_stem']) if len(audit['examples_per_stem']) > 1 else 0
        }

    return stats

def print_report(audit: Dict[str, Any], stats: Dict[str, Any]):
    """Print comprehensive audit report."""

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}COMPREHENSIVE DATA QUALITY AUDIT REPORT{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

    # Overall Statistics
    print(f"{Colors.BOLD}{Colors.BLUE}OVERALL STATISTICS{Colors.END}")
    print(f"{'─' * 80}")
    print(f"Total Verbs:              {Colors.GREEN}{audit['total_verbs']:,}{Colors.END}")
    print(f"Total Stems:              {Colors.GREEN}{audit['total_stems']:,}{Colors.END}")
    print(f"Total Examples:           {Colors.GREEN}{audit['total_examples']:,}{Colors.END}")
    print(f"Total Etymology Entries:  {Colors.GREEN}{audit['total_etymology_entries']:,}{Colors.END}")
    print()

    # Statistical Metrics
    print(f"{Colors.BOLD}{Colors.BLUE}STATISTICAL METRICS{Colors.END}")
    print(f"{'─' * 80}")

    if 'stems_per_verb' in stats:
        s = stats['stems_per_verb']
        print(f"{Colors.BOLD}Stems per Verb:{Colors.END}")
        print(f"  Mean:    {s['mean']:.2f}")
        print(f"  Median:  {s['median']:.2f}")
        print(f"  Range:   {s['min']} - {s['max']}")
        print(f"  StdDev:  {s['stdev']:.2f}")
        print()

    if 'examples_per_verb' in stats:
        s = stats['examples_per_verb']
        print(f"{Colors.BOLD}Examples per Verb:{Colors.END}")
        print(f"  Mean:    {s['mean']:.2f}")
        print(f"  Median:  {s['median']:.2f}")
        print(f"  Range:   {s['min']} - {s['max']}")
        print(f"  StdDev:  {s['stdev']:.2f}")
        print()

    if 'examples_per_stem' in stats:
        s = stats['examples_per_stem']
        print(f"{Colors.BOLD}Examples per Stem:{Colors.END}")
        print(f"  Mean:    {s['mean']:.2f}")
        print(f"  Median:  {s['median']:.2f}")
        print(f"  Range:   {s['min']} - {s['max']}")
        print(f"  StdDev:  {s['stdev']:.2f}")
        print()

    # Stem Distribution
    print(f"{Colors.BOLD}Stem Distribution:{Colors.END}")
    for stem, count in audit['stem_distribution'].most_common():
        percentage = (count / audit['total_stems'] * 100) if audit['total_stems'] > 0 else 0
        print(f"  {stem:12} {count:4,} ({percentage:5.1f}%)")
    print()

    # Etymology Analysis
    print(f"{Colors.BOLD}{Colors.BLUE}ETYMOLOGY ANALYSIS{Colors.END}")
    print(f"{'─' * 80}")
    total = audit['total_verbs']

    null_count = len(audit['etymology_null'])
    partial_count = len(audit['etymology_partial'])
    complete_count = len(audit['etymology_complete'])

    print(f"No Etymology:             {null_count:4,} ({null_count/total*100:5.1f}%)")
    print(f"Partial Etymology:        {partial_count:4,} ({partial_count/total*100:5.1f}%)")
    print(f"  Arabic only:            {len(audit['etymology_arabic_only']):4,}")
    print(f"  Kurdish only:           {len(audit['etymology_kurdish_only']):4,}")
    print(f"Complete Etymology:       {complete_count:4,} ({complete_count/total*100:5.1f}%)")
    print(f"  (Both Arabic & Kurdish)")
    print()

    # Quality Issues
    print(f"{Colors.BOLD}{Colors.BLUE}QUALITY ISSUES{Colors.END}")
    print(f"{'─' * 80}")

    issues = [
        ('CRITICAL', [
            ('Malformed Structure', len(audit['malformed_structure']), audit['malformed_structure']),
            ('Duplicate Roots', len(audit['duplicate_roots']), audit['duplicate_roots']),
            ('Verbs Without Stems', len(audit['verbs_without_stems']), audit['verbs_without_stems']),
        ]),
        ('HIGH', [
            ('Verbs Without Examples', len(audit['verbs_without_examples']), audit['verbs_without_examples']),
            ('Empty Turoyo Fields', len(audit['empty_turoyo_fields']), audit['empty_turoyo_fields']),
        ]),
        ('MEDIUM', [
            ('Empty Translation Arrays', len(audit['empty_translation_arrays']), audit['empty_translation_arrays']),
        ]),
    ]

    for severity, issue_list in issues:
        color = Colors.RED if severity == 'CRITICAL' else Colors.YELLOW if severity == 'HIGH' else Colors.MAGENTA
        print(f"\n{Colors.BOLD}{color}{severity} SEVERITY{Colors.END}")

        for issue_name, count, data in issue_list:
            if count > 0:
                print(f"  {color}✗{Colors.END} {issue_name}: {color}{count:,}{Colors.END}")

                # Show sample details
                if issue_name == 'Malformed Structure' and count > 0:
                    for item in data[:5]:
                        print(f"      → {item['root']}: {item['issue']}")
                    if count > 5:
                        print(f"      → ... and {count - 5} more")

                elif issue_name == 'Duplicate Roots' and count > 0:
                    for item in data[:5]:
                        print(f"      → {item['root']}: {', '.join(item['files'])}")
                    if count > 5:
                        print(f"      → ... and {count - 5} more")

                elif issue_name == 'Empty Turoyo Fields' and count > 0:
                    for item in data[:5]:
                        print(f"      → {item['root']} (stem {item['stem']})")
                    if count > 5:
                        print(f"      → ... and {count - 5} more")

                elif count <= 10 and isinstance(data, list) and isinstance(data[0], str):
                    print(f"      → {', '.join(data[:10])}")
                elif count > 10 and isinstance(data, list) and isinstance(data[0], str):
                    print(f"      → {', '.join(data[:10])}")
                    print(f"      → ... and {count - 10} more")
            else:
                print(f"  {Colors.GREEN}✓{Colors.END} {issue_name}: {Colors.GREEN}0{Colors.END}")

    print()

    # Translation Quality
    print(f"{Colors.BOLD}{Colors.BLUE}TRANSLATION QUALITY{Colors.END}")
    print(f"{'─' * 80}")
    total_examples = audit['total_examples']

    missing = len(audit['examples_missing_all_translations'])
    some = len(audit['examples_with_some_translations'])
    complete = len(audit['examples_with_all_translations'])

    print(f"Examples with no translations:   {missing:4,} ({missing/total_examples*100 if total_examples > 0 else 0:5.1f}%)")
    print(f"Examples with some translations: {some:4,} ({some/total_examples*100 if total_examples > 0 else 0:5.1f}%)")
    print(f"Examples with all translations:  {complete:4,} ({complete/total_examples*100 if total_examples > 0 else 0:5.1f}%)")
    print()

    # Expected Baseline Comparison
    print(f"{Colors.BOLD}{Colors.BLUE}BASELINE COMPARISON{Colors.END}")
    print(f"{'─' * 80}")
    print(f"{Colors.BOLD}Expected (from DOCX analysis):{Colors.END}")
    print(f"  Total verbs:   ~1,696")
    print(f"  Total stems:   ~3,553")
    print(f"  Total examples: ~4,685")
    print()
    print(f"{Colors.BOLD}Actual:{Colors.END}")
    print(f"  Total verbs:   {audit['total_verbs']:,}")
    print(f"  Total stems:   {audit['total_stems']:,}")
    print(f"  Total examples: {audit['total_examples']:,}")
    print()

    if audit['total_verbs'] < 1696:
        diff = 1696 - audit['total_verbs']
        print(f"  {Colors.YELLOW}⚠ Missing {diff} verbs from expected baseline{Colors.END}")
    else:
        print(f"  {Colors.GREEN}✓ Verb count meets or exceeds baseline{Colors.END}")

    if audit['total_stems'] < 3553:
        diff = 3553 - audit['total_stems']
        print(f"  {Colors.YELLOW}⚠ Missing {diff} stems from expected baseline{Colors.END}")
    else:
        print(f"  {Colors.GREEN}✓ Stem count meets or exceeds baseline{Colors.END}")

    if audit['total_examples'] < 4685:
        diff = 4685 - audit['total_examples']
        print(f"  {Colors.YELLOW}⚠ Missing {diff} examples from expected baseline{Colors.END}")
    else:
        print(f"  {Colors.GREEN}✓ Example count meets or exceeds baseline{Colors.END}")

    print()

    # Summary
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

    critical_count = sum(count for _, count, _ in issues[0][1])
    high_count = sum(count for _, count, _ in issues[1][1])
    medium_count = sum(count for _, count, _ in issues[2][1])

    if critical_count > 0:
        print(f"{Colors.RED}✗ CRITICAL ISSUES FOUND: {critical_count:,}{Colors.END}")
        print(f"  Action required: Fix malformed structures and duplicates immediately")
        print()

    if high_count > 0:
        print(f"{Colors.YELLOW}⚠ HIGH PRIORITY ISSUES: {high_count:,}{Colors.END}")
        print(f"  Action recommended: Review verbs without stems/examples and empty Turoyo fields")
        print()

    if medium_count > 0:
        print(f"{Colors.MAGENTA}ℹ MEDIUM PRIORITY ISSUES: {medium_count:,}{Colors.END}")
        print(f"  Note: Some verbs have Turoyo-only examples (expected)")
        print()

    if critical_count == 0 and high_count == 0:
        print(f"{Colors.GREEN}✓ DATA QUALITY: EXCELLENT{Colors.END}")
        print(f"  No critical or high-priority issues found")
        print()

    print(f"Overall data completeness: {audit['total_examples'] / 4685 * 100:.1f}% of expected baseline")
    print()

def save_detailed_report(audit: Dict[str, Any], output_file: str):
    """Save detailed JSON report for programmatic analysis."""

    # Convert to serializable format
    report = {
        'summary': {
            'total_verbs': audit['total_verbs'],
            'total_stems': audit['total_stems'],
            'total_examples': audit['total_examples'],
            'total_etymology_entries': audit['total_etymology_entries'],
        },
        'issues': {
            'critical': {
                'malformed_structure': audit['malformed_structure'],
                'duplicate_roots': audit['duplicate_roots'],
                'verbs_without_stems': audit['verbs_without_stems'],
            },
            'high': {
                'verbs_without_examples': audit['verbs_without_examples'],
                'empty_turoyo_fields': audit['empty_turoyo_fields'],
            },
            'medium': {
                'empty_translation_arrays': audit['empty_translation_arrays'],
            }
        },
        'etymology': {
            'null': audit['etymology_null'],
            'partial': audit['etymology_partial'],
            'complete': audit['etymology_complete'],
            'arabic_only': audit['etymology_arabic_only'],
            'kurdish_only': audit['etymology_kurdish_only'],
            'both_sources': audit['etymology_both_sources'],
        },
        'stem_distribution': dict(audit['stem_distribution']),
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"{Colors.GREEN}Detailed report saved to: {output_file}{Colors.END}\n")

def main():
    verbs_dir = '/Users/evb/WebstormProjects/turoyo-verb-glossary/server/assets/verbs'
    output_dir = '/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/analysis'

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{Colors.CYAN}Loading all verb files...{Colors.END}")
    verbs = load_all_verbs(verbs_dir)
    print(f"{Colors.GREEN}Loaded {len(verbs):,} verbs{Colors.END}")

    print(f"\n{Colors.CYAN}Running comprehensive audit...{Colors.END}")
    audit = audit_verbs(verbs)

    print(f"\n{Colors.CYAN}Calculating statistics...{Colors.END}")
    stats = calculate_statistics(audit)

    print_report(audit, stats)

    output_file = os.path.join(output_dir, 'comprehensive_audit_report.json')
    save_detailed_report(audit, output_file)

if __name__ == '__main__':
    main()
