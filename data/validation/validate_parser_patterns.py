#!/usr/bin/env python3
"""
Validate Parser Patterns Against Source HTML
============================================
This script tests parser regex patterns against the actual source HTML
to identify false positives, false negatives, and edge cases.

Usage: python3 data/validation/validate_parser_patterns.py
"""

import re
import json
from pathlib import Path
from collections import defaultdict

SOURCE_HTML = Path('source/Turoyo_all_2024.html')


def load_source_html():
    """Load source HTML file"""
    with open(SOURCE_HTML, 'r', encoding='utf-8') as f:
        return f.read()


def test_root_pattern(html):
    """Test root extraction pattern"""
    print("\n" + "=" * 80)
    print("TEST 1: ROOT PATTERN VALIDATION")
    print("=" * 80)

    root_pattern = r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)?<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(?:\s*\d+)?[^<]*</span>'

    matches = list(re.finditer(root_pattern, html))
    print(f"\n✓ Found {len(matches)} potential root matches")

    print("\nFirst 20 matches:")
    for i, match in enumerate(matches[:20], 1):
        root = match.group(1)
        context = html[match.start():match.end()]
        span_match = re.search(r'<span[^>]*>([^<]+)</span>', context)
        if span_match:
            full_text = span_match.group(1)
            has_semicolon = ';' in full_text
            has_special = any(c in full_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə')
            gloss_candidate = has_semicolon and not has_special

            print(f"{i:3}. '{root}' | Full: '{full_text[:30]}...' | Gloss? {gloss_candidate}")

    print("\n" + "-" * 80)
    print("Checking for German gloss false positives...")

    german_glosses = [
        'speichern;', 'erklären;', 'erlauben;', 'machen;',
        'bringen;', 'geben;', 'nehmen;', 'sehen;'
    ]

    found_glosses = []
    for gloss in german_glosses:
        if gloss in html:
            gloss_pattern = re.escape(gloss[:2])
            for match in matches:
                if match.group(1) == gloss[:2]:
                    found_glosses.append((gloss, match.group(1)))
                    break

    if found_glosses:
        print(f"\n⚠️  WARNING: Found {len(found_glosses)} German glosses that matched root pattern:")
        for gloss, matched in found_glosses:
            print(f"  - '{gloss}' matched as '{matched}'")
    else:
        print("\n✓ No German glosses matched root pattern")

    return matches


def test_stem_pattern(html):
    """Test stem extraction patterns"""
    print("\n" + "=" * 80)
    print("TEST 2: STEM PATTERN VALIDATION")
    print("=" * 80)

    stem_pattern_primary = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'

    stem_pattern_combined = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*([^<]+)</span></b></font>'

    stem_pattern_fallback = r'<p[^>]*>.*?<span[^>]*>([IVX]+):</span>.*?</p>'

    matches_primary = list(re.finditer(stem_pattern_primary, html))
    matches_combined = list(re.finditer(stem_pattern_combined, html))
    matches_fallback = list(re.finditer(stem_pattern_fallback, html))

    print(f"\n✓ Primary pattern: {len(matches_primary)} matches")
    print(f"✓ Combined pattern: {len(matches_combined)} matches")
    print(f"✓ Fallback pattern: {len(matches_fallback)} matches")
    print(f"✓ Total unique stems: ~{len(matches_primary) + len(matches_combined) + len(matches_fallback)}")

    print("\nSample primary pattern matches:")
    for match in matches_primary[:5]:
        stem = match.group(1)
        forms = match.group(2)
        print(f"  - {stem}: {forms[:50]}...")

    return {
        'primary': matches_primary,
        'combined': matches_combined,
        'fallback': matches_fallback
    }


def test_etymology_pattern(html):
    """Test etymology extraction pattern"""
    print("\n" + "=" * 80)
    print("TEST 3: ETYMOLOGY PATTERN VALIDATION")
    print("=" * 80)

    etym_pattern = r'\(&lt;\s*(.+?)\s*\)(?:\s*[A-Z<]|$)'
    matches = list(re.finditer(etym_pattern, html, re.DOTALL))

    print(f"\n✓ Found {len(matches)} etymology blocks")

    print("\nFirst 10 etymology blocks:")
    for i, match in enumerate(matches[:10], 1):
        etym_text = match.group(1).strip()
        etym_text = re.sub(r'<[^>]+>', '', etym_text)
        etym_text = etym_text.replace('\n', ' ')
        etym_text = re.sub(r'\s+', ' ', etym_text)
        print(f"{i:3}. {etym_text[:80]}...")

    print("\n" + "-" * 80)
    print("Checking for relationship keywords...")

    also_count = len(re.findall(r'\(&lt;[^)]*\salso\s', html))
    or_count = len(re.findall(r'\(&lt;[^)]*\sor\s', html))
    and_count = len(re.findall(r'\(&lt;[^)]*[;,]\s*and\s', html))

    print(f"\n✓ Etymologies with 'also': {also_count}")
    print(f"✓ Etymologies with 'or': {or_count}")
    print(f"✓ Etymologies with 'and': {and_count}")

    return matches


def test_number_detection(html):
    """Test homonym number detection patterns"""
    print("\n" + "=" * 80)
    print("TEST 4: HOMONYM NUMBER DETECTION")
    print("=" * 80)

    pattern1 = r'<i><span[^>]*>\s*(\d+)\s+\('
    pattern2 = r'<span[^>]*>\s*(\d+)\s*</span>'
    pattern3 = r'<sup[^>]*>.*?(\d+).*?</sup>'

    matches1 = list(re.finditer(pattern1, html))
    matches2 = list(re.finditer(pattern2, html))
    matches3 = list(re.finditer(pattern3, html))

    print(f"\n✓ Italic with paren: {len(matches1)} matches")
    print(f"✓ Separate span: {len(matches2)} matches")
    print(f"✓ Superscript: {len(matches3)} matches")

    print("\n" + "-" * 80)
    print("Looking for pre-numbered roots in source HTML...")

    numbered_roots = re.findall(
        r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)*<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})\s+(\d+)',
        html
    )

    if numbered_roots:
        print(f"\n✓ Found {len(numbered_roots)} pre-numbered roots:")
        root_counts = defaultdict(list)
        for root, num in numbered_roots:
            root_counts[root].append(num)

        for root, nums in sorted(root_counts.items())[:10]:
            print(f"  - {root}: numbers {', '.join(sorted(set(nums)))}")
    else:
        print("\n✓ No pre-numbered roots found in source HTML")

    return numbered_roots


def test_table_structure(html):
    """Test table extraction patterns"""
    print("\n" + "=" * 80)
    print("TEST 5: TABLE STRUCTURE VALIDATION")
    print("=" * 80)

    table_pattern = r'<table[^>]*>(.*?)</table>'
    tables = list(re.finditer(table_pattern, html, re.DOTALL))

    print(f"\n✓ Found {len(tables)} tables in source HTML")

    if tables:
        first_table = tables[0].group(0)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', first_table, re.DOTALL)
        print(f"\nFirst table has {len(rows)} rows")

        if rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', rows[0], re.DOTALL)
            print(f"First row has {len(cells)} cells")

            if len(cells) >= 2:
                header = cells[0]
                header_text = re.sub(r'<[^>]+>', '', header).strip()
                print(f"First cell (header): '{header_text[:50]}...'")

                example = cells[1]
                has_italic = '<i>' in example
                has_span = '<span>' in example
                print(f"Second cell (examples): italic={has_italic}, span={has_span}")

    return tables


def test_edge_cases(html):
    """Test specific edge cases and known issues"""
    print("\n" + "=" * 80)
    print("TEST 6: EDGE CASES AND KNOWN ISSUES")
    print("=" * 80)

    print("\nTest 1: ʕmr homonym patterns...")
    omr_pattern1 = r'<p[^>]*class="western"[^>]*><span[^>]*>ʕmr'
    omr_pattern2 = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>ʕmr'

    omr1 = len(re.findall(omr_pattern1, html))
    omr2 = len(re.findall(omr_pattern2, html))

    print(f"  - ʕmr with <p><span>: {omr1}")
    print(f"  - ʕmr with <p><font><span>: {omr2}")

    if omr1 > omr2:
        print(f"  ✓ Pattern handles both formats (pattern should use optional <font>)")
    else:
        print(f"  ⚠️  All ʕmr entries have <font> tags")

    print("\nTest 2: Detransitive sections...")
    detrans1 = len(re.findall(r'<font[^>]*size="4"[^>]*><b><span[^>]*>Detransitive', html))
    detrans2 = len(re.findall(r'<p[^>]*><span[^>]*>Detransitive</span></p>', html))

    print(f"  - Detransitive with font size 4: {detrans1}")
    print(f"  - Detransitive in paragraph: {detrans2}")
    print(f"  - Total detransitive sections: {detrans1 + detrans2}")

    print("\nTest 3: Cross-references...")
    xref_pattern = r'→\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]+)'
    xrefs = re.findall(xref_pattern, html)

    print(f"  - Total cross-references: {len(xrefs)}")
    if xrefs:
        print(f"  - Sample: {', '.join(xrefs[:5])}")

    print("\nTest 4: Uncertain entries...")
    uncertain = len(re.findall(r'\?\?\?', html))
    print(f"  - Entries with '???': {uncertain}")

    print("\nTest 5: Root continuations...")
    cont_pattern = r'</span></font><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]+)</span>'
    continuations = len(re.findall(cont_pattern, html))
    print(f"  - Potential root continuations: {continuations}")


def generate_report(results):
    """Generate comprehensive validation report"""
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    report = {
        'total_root_matches': len(results['roots']),
        'total_stems': sum(len(v) for v in results['stems'].values()),
        'total_etymologies': len(results['etymologies']),
        'total_tables': len(results['tables']),
        'pre_numbered_roots': len(results['numbered_roots']),
        'pattern_statistics': {
            'stems_by_pattern': {
                'primary': len(results['stems']['primary']),
                'combined': len(results['stems']['combined']),
                'fallback': len(results['stems']['fallback'])
            }
        }
    }

    print(f"\n📊 Pattern Match Statistics:")
    print(f"  - Root matches: {report['total_root_matches']}")
    print(f"  - Stem matches: {report['total_stems']}")
    print(f"    • Primary pattern: {report['pattern_statistics']['stems_by_pattern']['primary']}")
    print(f"    • Combined pattern: {report['pattern_statistics']['stems_by_pattern']['combined']}")
    print(f"    • Fallback pattern: {report['pattern_statistics']['stems_by_pattern']['fallback']}")
    print(f"  - Etymology blocks: {report['total_etymologies']}")
    print(f"  - Tables: {report['total_tables']}")
    print(f"  - Pre-numbered roots: {report['pre_numbered_roots']}")

    output_file = Path('data/validation/pattern_validation_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Report saved to: {output_file}")


def main():
    """Run all validation tests"""
    print("=" * 80)
    print("PARSER PATTERN VALIDATION")
    print("=" * 80)
    print(f"\nSource: {SOURCE_HTML}")

    if not SOURCE_HTML.exists():
        print(f"\n❌ ERROR: Source file not found: {SOURCE_HTML}")
        return

    html = load_source_html()
    print(f"✓ Loaded source HTML ({len(html):,} bytes)")

    results = {}
    results['roots'] = test_root_pattern(html)
    results['stems'] = test_stem_pattern(html)
    results['etymologies'] = test_etymology_pattern(html)
    results['numbered_roots'] = test_number_detection(html)
    results['tables'] = test_table_structure(html)

    test_edge_cases(html)

    generate_report(results)

    print("\n" + "=" * 80)
    print("✅ VALIDATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
