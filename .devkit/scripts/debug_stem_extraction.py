#!/usr/bin/env python3
"""
Debug why stem extraction is failing on new sources
"""

import re
from pathlib import Path

def main():
    print("=" * 80)
    print("STEM EXTRACTION DIAGNOSTIC")
    print("=" * 80)

    html = Path('.devkit/analysis/new_sources_normalized.html').read_text()

    first_verb_match = re.search(r'<p[^>]*><span>ʔbʕ</span>', html)
    if not first_verb_match:
        print("❌ Can't find first verb (ʔbʕ)")
        return

    start = first_verb_match.start()
    next_verb = re.search(r'<p[^>]*><span>[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,}', html[start+100:start+5000])
    end = next_verb.start() + start + 100 if next_verb else start + 5000

    entry_html = html[start:end]

    print(f"\nFirst verb entry (ʔbʕ) - {len(entry_html)} bytes")
    print("="*80)

    stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'
    matches = list(re.finditer(stem_pattern, entry_html))

    print(f"\nPrimary stem pattern matches: {len(matches)}")
    if matches:
        for m in matches:
            print(f"  Stem {m.group(1)}: {m.group(2)}")

    combined_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*([^<]+)</span></b></font>'
    combined_matches = list(re.finditer(combined_pattern, entry_html))
    print(f"\nCombined pattern matches: {len(combined_matches)}")
    if combined_matches:
        for m in combined_matches:
            print(f"  Stem {m.group(1)}: {m.group(2)[:50]}")

    print("\n" + "="*80)
    print("Searching for size=\"4\" font tags...")
    size4_tags = re.findall(r'<font size="4"[^>]*>.*?</font>', entry_html, re.DOTALL)
    print(f"Found {len(size4_tags)} size=4 font blocks")

    if size4_tags:
        print("\nFirst size=4 block:")
        print(size4_tags[0][:300])

    print("\n" + "="*80)
    print("Searching for roman numerals...")
    roman_matches = re.findall(r'([IVX]+):', entry_html)
    print(f"Found {len(roman_matches)} roman numeral patterns: {roman_matches}")

    print("\n" + "="*80)
    print("Looking for the EXACT structure around 'I:'...")
    context = re.search(r'.{200}<font size="4".*?I:.*?</font>.{200}', entry_html, re.DOTALL)
    if context:
        snippet = context.group(0)
        snippet = snippet.replace('\n', '↵\n')
        print(snippet)

if __name__ == '__main__':
    main()
