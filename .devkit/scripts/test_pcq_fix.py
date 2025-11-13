#!/usr/bin/env python3
"""
TEST: Does the new malformed parentheses fix work for pčq?
"""

import re

def parse_etymology_full_fixed(text, next_para_text=None):
    """Fixed etymology parsing with malformed parentheses detection"""

    match = None
    paren_start = text.find('(<')
    if paren_start >= 0:
        depth = 1
        i = paren_start + 1
        while i < len(text) and depth > 0:
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
            i += 1

        if depth == 0:
            etym_content = text[paren_start+2:i-1].strip()

            # BUGFIX: Check for malformed parentheses (pčq case)
            text_after_paren = text[i:].strip()
            if next_para_text and text_after_paren and next_para_text.endswith(')'):
                # Check if etymology ends with ". N" pattern (incomplete list item)
                if re.search(r'\.\s+\d+$', etym_content):
                    print(f"   🔧 Detected malformed parentheses!")
                    print(f"      Etymology ends with: {repr(etym_content[-10:])}")
                    print(f"      Text after paren: {repr(text_after_paren[:30])}")
                    print(f"      Next para: {repr(next_para_text[:40])}")

                    # This is malformed - include text after paren and next para
                    continuation = text_after_paren + ' ' + next_para_text
                    etym_content = etym_content + ') ' + continuation
                    # Now find the REAL closing paren (the last one)
                    last_paren = etym_content.rfind(')')
                    if last_paren > 0:
                        etym_content = etym_content[:last_paren].strip()

            class MatchLike:
                def __init__(self, content):
                    self._content = content
                def group(self, n):
                    return self._content if n == 1 else None
            match = MatchLike(etym_content)

    if not match:
        return None

    return {'raw': match.group(1).strip()}


# Test case: pčq etymology
text1 = "pčq (< prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush,"
next1 = "press, smash, squash, KED 107)"

print("=" * 80)
print("TEST: pčq etymology with malformed parentheses fix")
print("=" * 80)

print("\n📝 INPUT:")
print(f"   Para 1: {repr(text1)}")
print(f"   Para 2: {repr(next1)}")

print("\n🔍 EXPECTED RESULT:")
expected = "prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush, press, smash, squash, KED 107"
print(f"   {repr(expected)}")

print("\n🧪 RUNNING PARSER:")
result = parse_etymology_full_fixed(text1, next1)

if result:
    actual = result['raw']
    print(f"\n✅ RESULT:")
    print(f"   {repr(actual)}")

    print(f"\n📊 COMPARISON:")
    print(f"   Expected: {repr(expected)}")
    print(f"   Actual:   {repr(actual)}")

    if actual == expected:
        print(f"\n🎉 SUCCESS! Etymology matches exactly!")
    else:
        print(f"\n⚠️  Close, but not exact match")
        print(f"   Expected length: {len(expected)}")
        print(f"   Actual length:   {len(actual)}")

        # Find differences
        for i, (e, a) in enumerate(zip(expected, actual)):
            if e != a:
                print(f"   First diff at position {i}: expected {repr(e)}, got {repr(a)}")
                break
else:
    print(f"\n❌ FAILED: No etymology extracted")
