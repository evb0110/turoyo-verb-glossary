#!/usr/bin/env python3
"""Test balanced quote counting fix for nested quote issue"""

import re

def is_apostrophe_not_quote_OLD(raw, pos):
    """OLD logic - Check if character at pos is an apostrophe in a word (not a closing quote)"""
    n = len(raw)
    if pos <= 0 or pos >= n - 1:
        return False
    return raw[pos - 1].isalpha() and raw[pos + 1].isalpha()

def tokenize_raw_OLD(raw):
    """OLD tokenizer - current broken logic"""
    tokens = []
    i = 0
    n = len(raw)

    def push(kind, value):
        if not value:
            return
        tokens.append({'kind': kind, 'value': value})

    quote_pairs = {
        'ʻ': 'ʼ',
        '\u2018': '\u2019',  # Curly single quotes
        '\u201C': '\u201D',  # Curly double quotes
        "'": "'",
        '"': '"',
    }

    ref_regex = re.compile(
        r'(?:'
        r'\+\s*[A-Z][a-zA-Z\s]+[a-z]+\.\s*\d+(?:[./]\d+)*'
        r'|(?<![A-Za-z])[a-z]+\.\s*\d+(?:[./]\d+)*'
        r'|(?<![A-Za-z])[A-Z][A-Za-z]{0,3}\s+\d+(?:[./]\d+)*'
        r'|(?<!\d)\d{1,3}(?:[./]\d+)*'
        r')(?=(?:[^\w]|$))'
    )

    while i < n:
        c = raw[i]

        if c in quote_pairs:
            close = quote_pairs[c]
            j = i + 1
            while j < n:
                if raw[j] == close:
                    if is_apostrophe_not_quote_OLD(raw, j):
                        j += 1
                        continue
                    break
                j += 1

            if j < n:
                push('translation', raw[i:j+1])
                i = j + 1
                continue
            push('text', c)
            i += 1
            continue

        if c == '[':
            j = raw.find(']', i + 1)
            if j != -1:
                push('note', raw[i:j+1])
                i = j + 1
                continue
            push('text', c)
            i += 1
            continue

        m = ref_regex.match(raw, i)
        if m:
            push('ref', m.group(0))
            i = m.end()
            continue

        if c in ';,:()':
            push('punct', c)
            i += 1
            continue

        j = i + 1
        while j < n:
            cj = raw[j]
            if (cj in quote_pairs) or cj == '[' or cj in ';,:()' or ref_regex.match(raw, j):
                break
            j += 1
        push('text', raw[i:j])
        i = j

    return tokens

def tokenize_raw_NEW(raw):
    """NEW tokenizer - with balanced quote counting"""
    tokens = []
    i = 0
    n = len(raw)

    def push(kind, value):
        if not value:
            return
        tokens.append({'kind': kind, 'value': value})

    quote_pairs = {
        'ʻ': 'ʼ',
        '\u2018': '\u2019',  # Curly single quotes
        '\u201C': '\u201D',  # Curly double quotes
        "'": "'",
        '"': '"',
    }

    ref_regex = re.compile(
        r'(?:'
        r'\+\s*[A-Z][a-zA-Z\s]+[a-z]+\.\s*\d+(?:[./]\d+)*'
        r'|(?<![A-Za-z])[a-z]+\.\s*\d+(?:[./]\d+)*'
        r'|(?<![A-Za-z])[A-Z][A-Za-z]{0,3}\s+\d+(?:[./]\d+)*'
        r'|(?<!\d)\d{1,3}(?:[./]\d+)*'
        r')(?=(?:[^\w]|$))'
    )

    def is_apostrophe_not_quote(pos):
        """Check if character at pos is an apostrophe in a word"""
        if pos <= 0 or pos >= n - 1:
            return False
        return raw[pos - 1].isalpha() and raw[pos + 1].isalpha()

    while i < n:
        c = raw[i]

        if c in quote_pairs:
            close = quote_pairs[c]

            # NEW LOGIC: Track quote nesting depth
            j = i + 1
            depth = 1  # Start with one opening quote

            while j < n and depth > 0:
                if raw[j] == c:
                    # Found another opening quote of the same type (nested)
                    depth += 1
                    j += 1
                elif raw[j] == close:
                    # Check if this is an apostrophe (not a closing quote)
                    if is_apostrophe_not_quote(j):
                        j += 1
                        continue
                    # Found a closing quote - decrease depth
                    depth -= 1
                    if depth == 0:
                        # Found balanced closing quote
                        push('translation', raw[i:j+1])
                        i = j + 1
                        break
                    j += 1
                else:
                    j += 1

            # If depth > 0, no balanced closing - treat as text
            if depth > 0:
                push('text', c)
                i += 1
            continue

        if c == '[':
            j = raw.find(']', i + 1)
            if j != -1:
                push('note', raw[i:j+1])
                i = j + 1
                continue
            push('text', c)
            i += 1
            continue

        m = ref_regex.match(raw, i)
        if m:
            push('ref', m.group(0))
            i = m.end()
            continue

        if c in ';,:()':
            push('punct', c)
            i += 1
            continue

        j = i + 1
        while j < n:
            cj = raw[j]
            if (cj in quote_pairs) or cj == '[' or cj in ';,:()' or ref_regex.match(raw, j):
                break
            j += 1
        push('text', raw[i:j])
        i = j

    return tokens

# Test cases
test_cases = [
    {
        "name": "1977 example (BROKEN in OLD)",
        "raw": "\u2018I drove (lit. \u2018worked on\u2019) minibuses and cabs until 1977\u2019 EL 20;",
        "expected_translations": ["\u2018I drove (lit. \u2018worked on\u2019) minibuses and cabs until 1977\u2019"],
    },
    {
        "name": "Simple translation",
        "raw": "\u2018I drove his tractor\u2019 EL 11;",
        "expected_translations": ["\u2018I drove his tractor\u2019"],
    },
    {
        "name": "Nested parens without quotes",
        "raw": "\u2018He works (every day) with people\u2019 77/41;",
        "expected_translations": ["\u2018He works (every day) with people\u2019"],
    },
    {
        "name": "dwq example (BROKEN in OLD)",
        "raw": "\u2018We shall no longer stay in that bakehouse (lit. \u2018stove\u2019)\u2019 RT 11;",
        "expected_translations": ["\u2018We shall no longer stay in that bakehouse (lit. \u2018stove\u2019)\u2019"],
    },
    {
        "name": "krx example (BROKEN in OLD)",
        "raw": "\u2018The talk was around the people (lit. \u2018the world\u2019)\u2019 RT 11;",
        "expected_translations": ["\u2018The talk was around the people (lit. \u2018the world\u2019)\u2019"],
    },
    {
        "name": "Apostrophe in word (it's)",
        "raw": "\u2018it\u2019s a nice day\u2019 EL 5;",
        "expected_translations": ["\u2018it\u2019s a nice day\u2019"],
    },
    {
        "name": "Apostrophe in word (mother's)",
        "raw": "\u2018The mother\u2019s house\u2019 123;",
        "expected_translations": ["\u2018The mother\u2019s house\u2019"],
    },
    {
        "name": "Multiple apostrophes",
        "raw": "\u2018John\u2019s father\u2019s brother\u2019s house\u2019 456;",
        "expected_translations": ["\u2018John\u2019s father\u2019s brother\u2019s house\u2019"],
    },
]

print("=" * 80)
print("TESTING OLD TOKENIZER (BROKEN)")
print("=" * 80)
for test in test_cases:
    tokens_old = tokenize_raw_OLD(test['raw'])
    translations_old = [t['value'] for t in tokens_old if t['kind'] == 'translation']

    print(f"\nTest: {test['name']}")
    print(f"Raw: {test['raw']}")
    print(f"Expected: {test['expected_translations']}")
    print(f"Got:      {translations_old}")

    if translations_old == test['expected_translations']:
        print("✓ PASS")
    else:
        print("✗ FAIL")

print("\n" + "=" * 80)
print("TESTING NEW TOKENIZER (FIXED)")
print("=" * 80)
for test in test_cases:
    tokens_new = tokenize_raw_NEW(test['raw'])
    translations_new = [t['value'] for t in tokens_new if t['kind'] == 'translation']

    print(f"\nTest: {test['name']}")
    print(f"Raw: {test['raw']}")
    print(f"Expected: {test['expected_translations']}")
    print(f"Got:      {translations_new}")

    if translations_new == test['expected_translations']:
        print("✓ PASS")
    else:
        print("✗ FAIL")
