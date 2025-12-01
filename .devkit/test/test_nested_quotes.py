#!/usr/bin/env python3
"""Test script to analyze nested quote issue in parser"""

import re

# Simulate the quote detection logic from parser
def is_apostrophe_not_quote(raw, pos):
    """Check if character at pos is an apostrophe in a word (not a closing quote)"""
    n = len(raw)
    if pos <= 0 or pos >= n - 1:
        return False
    # Apostrophe if: preceded AND followed by letter
    # Examples: "mother's", "Aren't", "it's"
    return raw[pos - 1].isalpha() and raw[pos + 1].isalpha()

def tokenize_raw(raw):
    """Replicate _split_raw_to_tokens logic"""
    tokens = []
    i = 0
    n = len(raw)

    def push(kind, value):
        if not value:
            return
        tokens.append({'kind': kind, 'value': value})

    # Quote pairs we recognize
    quote_pairs = {
        'ʻ': 'ʼ',  # Modifier letter quotes (U+02BB/U+02BC)
        '\u2018': '\u2019',  # Curly single quotes ' '
        '\u201C': '\u201D',  # Curly double quotes " "
        "'": "'",  # Straight single quote
        '"': '"',  # Straight double quote
    }

    # Reference patterns
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

        # Translation in quotes
        if c in quote_pairs:
            close = quote_pairs[c]

            # Find closing quote, but skip apostrophes within words
            j = i + 1
            while j < n:
                if raw[j] == close:
                    # Check if this is an apostrophe (not a closing quote)
                    if is_apostrophe_not_quote(raw, j):
                        print(f"  [SKIP] Position {j}: '{raw[max(0,j-3):j+4]}' - apostrophe in word")
                        j += 1  # Skip this apostrophe, keep looking
                        continue
                    # Found real closing quote
                    print(f"  [CLOSE] Position {j}: '{raw[max(0,j-3):j+4]}' - closing quote")
                    break
                j += 1

            if j < n:  # Found closing quote
                push('translation', raw[i:j+1])
                i = j + 1
                continue
            # No closing - treat as text
            push('text', c)
            i += 1
            continue

        # Note [ ... ]
        if c == '[':
            j = raw.find(']', i + 1)
            if j != -1:
                push('note', raw[i:j+1])
                i = j + 1
                continue
            push('text', c)
            i += 1
            continue

        # Reference
        m = ref_regex.match(raw, i)
        if m:
            push('ref', m.group(0))
            i = m.end()
            continue

        # Punctuation we want explicit
        if c in ';,:()':
            push('punct', c)
            i += 1
            continue

        # Whitespace or other text - accumulate until next special
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
        "name": "1977 example (BROKEN)",
        "raw": "'I drove (lit. 'worked on') minibuses and cabs until 1977' EL 20;",
    },
    {
        "name": "Simple translation (WORKING)",
        "raw": "'I drove his tractor' EL 11;",
    },
    {
        "name": "Nested parens without quotes (WORKING)",
        "raw": "'He works (every day) with people' 77/41;",
    },
    {
        "name": "dwq example (BROKEN)",
        "raw": "'We shall no longer stay in that bakehouse (lit. 'stove')' RT 11;",
    },
    {
        "name": "krx example (BROKEN)",
        "raw": "'The talk was around the people (lit. 'the world')' RT 11;",
    },
]

for test in test_cases:
    print("=" * 80)
    print(f"Test: {test['name']}")
    print(f"Raw: {test['raw']}")
    print()

    tokens = tokenize_raw(test['raw'])

    print("Tokens:")
    for tok in tokens:
        print(f"  {tok['kind']:12} | {tok['value']}")
    print()
