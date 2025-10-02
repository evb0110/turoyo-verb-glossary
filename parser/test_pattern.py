#!/usr/bin/env python3
import re

# The problem: greedy matches TOO MUCH - captures the whole entry
html = '(&lt; Arab. ʕdl (II) cf. Wehr 818: ins Gleichgewicht bringen, (wieder) in Ordnung bringen;) II: mʕadele/mʕadəl...'

print("Testing patterns:")
print("="*80)

# Pattern 1: Match to first ) that ends a sentence (;) or standalone )
# Use non-greedy but look for ;) explicitly
pattern1 = r'\(&lt;\s*(.+?)\s*\)(?:\s*[A-Z]|</)'
match1 = re.search(pattern1, html, re.DOTALL)
if match1:
    print(f'Pattern 1 (.+?) lookahead: {match1.group(1)}')

# Pattern 2: Greedy (current - too much)
pattern2 = r'\(&lt;\s*(.+)\s*\)'
match2 = re.search(pattern2, html, re.DOTALL)
if match2:
    print(f'Pattern 2 (.+):      {match2.group(1)[:80]}...')

# Test with actual cases
test_cases = [
    '(&lt; Arab. ʕdl (II) cf. Wehr 818: ins Gleichgewicht bringen, (wieder) in Ordnung bringen;) II: more stuff',
    '(&lt; MEA ṣʕr (Pa.) cf. SL 1296: to insult, abuse;) III: other',
    '(&lt; Arab. ʕbd, Wehr 807: dienen, göttliche Verehrung erweisen) I: ʕbədle',
    '(&lt; Arab. ʕǧl, Wehr 814: eilen, sich beeilen, in Eile sein; cf.)',
]

print("\nTest cases:")
print("="*80)
for test in test_cases:
    match = re.search(pattern1, test, re.DOTALL)
    if match:
        result = match.group(1).rstrip(';').strip()
        print(f'{result}')
    else:
        print(f'NO MATCH: {test[:60]}')
