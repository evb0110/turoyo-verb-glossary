#!/usr/bin/env python3
"""Debug balanced quote logic"""

import re

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
        print(f"  i={i}, c='{c}' (U+{ord(c):04X})")

        if c in quote_pairs:
            close = quote_pairs[c]
            print(f"    Quote detected! Opening='{c}' (U+{ord(c):04X}), Closing='{close}' (U+{ord(close):04X})")

            # NEW LOGIC: Track quote nesting depth
            j = i + 1
            depth = 1  # Start with one opening quote

            while j < n and depth > 0:
                print(f"      j={j}, depth={depth}, c='{raw[j]}' (U+{ord(raw[j]):04X})")
                if raw[j] == c:
                    # Found another opening quote of the same type (nested)
                    depth += 1
                    print(f"        Found nested opening quote, depth={depth}")
                    j += 1
                elif raw[j] == close:
                    # Check if this is an apostrophe (not a closing quote)
                    if is_apostrophe_not_quote(j):
                        print(f"        Apostrophe detected, skipping")
                        j += 1
                        continue
                    # Found a closing quote - decrease depth
                    depth -= 1
                    print(f"        Found closing quote, depth={depth}")
                    if depth == 0:
                        # Found balanced closing quote
                        result = raw[i:j+1]
                        print(f"        BALANCED! Translation: '{result}'")
                        push('translation', result)
                        i = j + 1
                        break
                    j += 1
                else:
                    j += 1

            # If depth > 0, no balanced closing - treat as text
            if depth > 0:
                print(f"    UNBALANCED (depth={depth}), treating as text")
                push('text', c)
                i += 1
            continue

        i += 1

    return tokens

# Test case
test = "'I drove (lit. 'worked on') minibuses and cabs until 1977' EL 20;"
print(f"Testing: {test}")
print()
tokens = tokenize_raw_NEW(test)
print()
print("RESULT:")
for tok in tokens:
    print(f"  {tok['kind']:12} | {tok['value']}")
