#!/usr/bin/env python3
"""
Test etymology parsing fix for nested parentheses
"""
import re
import json

def normalize_whitespace(text):
    """Clean whitespace"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_etymology_old(entry_html):
    """OLD VERSION - BROKEN: Parse etymology"""
    etym_pattern = r'\(&lt;\s*([^)]{1,300})\)'
    match = re.search(etym_pattern, entry_html)

    if not match:
        return None

    etym_text = match.group(1).strip()

    structured = re.match(
        r'([A-Za-z.]+)\s+([^\s]+)\s+cf\.\s+([^:]+):\s*(.+)',
        etym_text
    )

    if structured:
        return {
            'source': structured.group(1).strip(),
            'source_root': structured.group(2).strip(),
            'reference': structured.group(3).strip(),
            'meaning': normalize_whitespace(structured.group(4)),
        }

    simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
    if simple:
        return {
            'source': simple.group(1).strip(),
            'notes': normalize_whitespace(simple.group(2)),
        }

    return {'raw': etym_text}

def parse_etymology_new(entry_html):
    """NEW VERSION - FIXED: Parse etymology with nested parentheses support"""
    # Match (&lt; ... ;) where the content can include nested parentheses
    # Use a more sophisticated pattern that handles nested parens
    etym_pattern = r'\(&lt;\s*(.+?;)\s*\)'
    match = re.search(etym_pattern, entry_html, re.DOTALL)

    if not match:
        return None

    etym_text = match.group(1).strip()
    # Remove trailing semicolon for processing
    etym_text = etym_text.rstrip(';').strip()

    # Try structured format: Source root (binyan) cf. Reference: meaning
    structured = re.match(
        r'([A-Za-z.]+)\s+([^\s]+)\s+(?:\([^)]+\)\s+)?cf\.\s+([^:]+):\s*(.+)',
        etym_text
    )

    if structured:
        return {
            'source': structured.group(1).strip(),
            'source_root': structured.group(2).strip(),
            'reference': structured.group(3).strip(),
            'meaning': normalize_whitespace(structured.group(4)),
        }

    # Try simple format: Source notes
    simple = re.match(r'([A-Za-z.]+)\s+(.+)', etym_text)
    if simple:
        return {
            'source': simple.group(1).strip(),
            'notes': normalize_whitespace(simple.group(2)),
        }

    return {'raw': etym_text}

# Test cases from the source HTML
test_cases = [
    {
        'root': 'ʕdl',
        'html': '(&lt; Arab. ʕdl (II) cf. Wehr 818: ins Gleichgewicht bringen, (wieder) in Ordnung bringen;)',
        'expected_source': 'Arab.',
        'expected_root': 'ʕdl',
        'expected_ref': 'Wehr 818',
        'expected_meaning': 'ins Gleichgewicht bringen, (wieder) in Ordnung bringen'
    },
    {
        'root': 'ʕln',
        'html': '(&lt; Arab. ʕln (IV) cf. Wehr 871: offen erklären;)',
        'expected_source': 'Arab.',
        'expected_root': 'ʕln',
        'expected_ref': 'Wehr 871',
        'expected_meaning': 'offen erklären'
    },
    {
        'root': 'ṣʕr',
        'html': '(&lt; MEA ṣʕr (Pa.) cf. SL 1296: to insult, abuse;)',
        'expected_source': 'MEA',
        'expected_root': 'ṣʕr',
        'expected_ref': 'SL 1296',
        'expected_meaning': 'to insult, abuse'
    },
    {
        'root': 'ʕrf',
        'html': '(&lt; Arab. ʕrf (II) cf. Wehr 859: bekannt machen, benachrichtigen;)',
        'expected_source': 'Arab.',
        'expected_root': 'ʕrf',
        'expected_ref': 'Wehr 859',
        'expected_meaning': 'bekannt machen, benachrichtigen'
    },
]

print("="*80)
print("ETYMOLOGY PARSING FIX TEST")
print("="*80)

all_passed = True

for i, test in enumerate(test_cases, 1):
    print(f"\n--- Test {i}: {test['root']} ---")
    print(f"Input: {test['html'][:100]}...")

    # Test old version
    old_result = parse_etymology_old(test['html'])
    print(f"\nOLD (BROKEN):")
    print(f"  {json.dumps(old_result, ensure_ascii=False)}")

    # Test new version
    new_result = parse_etymology_new(test['html'])
    print(f"\nNEW (FIXED):")
    print(f"  {json.dumps(new_result, ensure_ascii=False)}")

    # Verify
    passed = True
    if new_result:
        if new_result.get('source') != test['expected_source']:
            print(f"  ❌ Source mismatch: {new_result.get('source')} != {test['expected_source']}")
            passed = False
        if new_result.get('source_root') != test['expected_root']:
            print(f"  ❌ Root mismatch: {new_result.get('source_root')} != {test['expected_root']}")
            passed = False
        if new_result.get('reference') != test['expected_ref']:
            print(f"  ❌ Reference mismatch: {new_result.get('reference')} != {test['expected_ref']}")
            passed = False
        if test['expected_meaning'] not in new_result.get('meaning', ''):
            print(f"  ❌ Meaning incomplete: {new_result.get('meaning')} should contain {test['expected_meaning']}")
            passed = False
    else:
        print(f"  ❌ No result returned")
        passed = False

    if passed:
        print("  ✅ PASSED")
    else:
        all_passed = False
        print("  ❌ FAILED")

print("\n" + "="*80)
if all_passed:
    print("✅ ALL TESTS PASSED")
else:
    print("❌ SOME TESTS FAILED")
print("="*80)
