#!/usr/bin/env python3
"""
Comprehensive HTML normalizer for new source files
This does ALL normalization in the correct order
"""

import re
from pathlib import Path

def normalize_html(html):
    """Normalize new LibreOffice 25.8 HTML to old LibreOffice 7.3 format"""

    print("  Step 1: Converting font tags to span tags...")
    html = re.sub(r'<font face="Times New Roman, serif">([^<]+)</font>', r'<span>\1</span>', html)
    html = re.sub(r'<font face="Times New Roman, serif">', r'<font>', html)

    print("  Step 1b: Wrapping bare roots in span tags...")
    # Match: <p...class="western"> followed immediately by Turoyo letters (no tags)
    html = re.sub(
        r'(<p[^>]*class="western"[^>]*>)([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})',
        r'\1<span>\2</span>',
        html
    )

    print("  Step 2: Wrapping bare h1 letter tags...")
    html = re.sub(
        r'(<h1[^>]*>)\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūəḎḌḤṬṢŠǦĠČŽ]+)\s*(</h1>)',
        r'\1<span>\2</span>\3',
        html
    )

    print("  Step 3: Adding span tags to stem headers (I:, II:, etc)...")
    html = re.sub(
        r'(<font size="4"[^>]*><b>)([IVX]+:\s*)(</b></font>)',
        r'\1<span>\2</span>\3',
        html
    )

    print("  Step 4: Fixing stem form structure...")
    # Pattern: </font></font> followed by <font size="4"><i><b>form
    # Goal: </font></font><font><font><i><b><span>form</span>

    # First, wrap forms in span if not already
    html = re.sub(
        r'(<font[^>]*><i><b>)([^<]+)(</b></i></font>)',
        r'\1<span>\2</span>\3',
        html
    )

    # Now fix the nested font structure for stem forms specifically
    # Match: (stem header closing) followed by (italic form opening)
    # This pattern ensures we only match actual stem forms, not other italic text
    pattern = r'(</font></font>)(<font[^>]*><i><b><span>[^<]+</span></b></i></font>)'

    def replace_func(m):
        closing = m.group(1)
        form_part = m.group(2)
        # Remove any size/style attributes from the font tag
        form_part = re.sub(r'<font[^>]*>', '<font>', form_part)
        # Wrap in double font
        return f'{closing}<font><font>{form_part}'

    html = re.sub(pattern, replace_func, html)

    return html

def main():
    print("=" * 80)
    print("COMPREHENSIVE HTML NORMALIZER")
    print("=" * 80)

    input_path = Path('.devkit/analysis/new_sources_combined.html')
    output_path = Path('.devkit/analysis/new_sources_normalized.html')

    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return 1

    html = input_path.read_text(encoding='utf-8')
    print(f"\nOriginal size: {len(html):,} bytes")

    normalized = normalize_html(html)

    print(f"Normalized size: {len(normalized):,} bytes")

    output_path.write_text(normalized, encoding='utf-8')
    print(f"\n✅ Saved: {output_path}")

    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    h1_count = len(re.findall(r'<h1[^>]*>\s*<span[^>]*>(?:&shy;)?([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūəḎḌḤṬṢŠǦĠČŽ]+)</span></h1>', normalized))
    print(f"✓ Letter headers: {h1_count}")

    stem_count = len(re.findall(r'<font size="4"[^>]*><b><span[^>]*>[IVX]+:', normalized))
    print(f"✓ Stem headers: {stem_count}")

    # Check for the exact pattern the parser needs
    parser_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'
    parser_matches = len(re.findall(parser_pattern, normalized))
    print(f"✓ Full parser pattern matches: {parser_matches}")

    if parser_matches > 0:
        print(f"\n🎉 SUCCESS! Parser should now extract {parser_matches} stems!")
    else:
        print(f"\n⚠️  Warning: Parser pattern not matching. Showing sample:")
        sample = re.search(r'<font size="4".*?[IVX]+:.*?</font></font>.*?<font.*?<i>', normalized[:50000], re.DOTALL)
        if sample:
            print(sample.group(0)[:300])

if __name__ == '__main__':
    main()
