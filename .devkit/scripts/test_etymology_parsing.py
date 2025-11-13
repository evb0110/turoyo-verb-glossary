#!/usr/bin/env python3
"""
TEST: Why is the multi-paragraph etymology parsing failing?
"""

import re

def parse_etymology_full(text, next_para_text=None):
    """Full etymology parsing with multi-paragraph support and flexible patterns"""

    match = None
    paren_start = text.find('(<')
    if paren_start >= 0:
        # Find matching closing paren by counting depth
        depth = 1
        i = paren_start + 1
        while i < len(text) and depth > 0:
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
            i += 1

        if depth == 0:
            # Found matching closing paren
            etym_content = text[paren_start+2:i-1].strip()
            print(f"✅ Found closed etymology: {repr(etym_content)}")
            return {'raw': etym_content}
        else:
            print(f"⚠️  Opening paren at {paren_start}, but depth={depth} (unclosed)")

    # Pattern 7: Multi-paragraph - unclosed paren
    if not match and next_para_text:
        print(f"🔍 Checking multi-paragraph pattern...")
        print(f"   Text: {repr(text)}")
        print(f"   Next: {repr(next_para_text)}")

        # Check if text has opening paren but no closing
        paren_match = re.search(r'\(<\s*(.+)$', text)
        if paren_match:
            print(f"   ✅ Found opening pattern: {repr(paren_match.group(0))}")
            # Look for closing paren in next paragraph
            close_match = re.search(r'^(.+?)\)', next_para_text)
            if close_match:
                print(f"   ✅ Found closing in next para: {repr(close_match.group(0))}")
                # Combine both paragraphs
                combined = paren_match.group(1) + ' ' + close_match.group(1)
                print(f"   ✅ Combined: {repr(combined)}")
                return {'raw': combined}
            else:
                print(f"   ❌ No closing paren found in next paragraph")
        else:
            print(f"   ❌ No opening pattern found")

    return None


# Test case 1: pčq etymology (the failing case)
text1 = "pčq (< prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush,"
next1 = "press, smash, squash, KED 107)"

print("=" * 80)
print("TEST CASE: pčq etymology")
print("=" * 80)
result1 = parse_etymology_full(text1, next1)
if result1:
    print(f"\n✅ Result: {result1}")
else:
    print(f"\n❌ No etymology extracted")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

# Let me trace through what's happening
print("\n1. Checking for '(<' pattern...")
paren_start = text1.find('(<')
print(f"   paren_start = {paren_start}")

if paren_start >= 0:
    print(f"\n2. Counting parentheses from position {paren_start}...")
    depth = 1
    i = paren_start + 1
    print(f"   Starting: depth={depth}, i={i}")

    while i < len(text1) and depth > 0:
        char = text1[i]
        if text1[i] == '(':
            depth += 1
            print(f"   i={i}, char='{char}' -> depth={depth}")
        elif text1[i] == ')':
            depth -= 1
            print(f"   i={i}, char='{char}' -> depth={depth}")
        i += 1

    print(f"\n3. Final state: depth={depth}, i={i}, len(text1)={len(text1)}")

    if depth == 0:
        print(f"   ✅ Found matching closing paren")
        print(f"   Content: {repr(text1[paren_start+2:i-1])}")
    else:
        print(f"   ❌ No matching closing paren (depth={depth})")
        print(f"   This should trigger multi-paragraph pattern")
