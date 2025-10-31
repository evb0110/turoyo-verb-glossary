#!/usr/bin/env python3
"""
Normalize new source HTML to match old source structure
Converts <font> tags to <span> tags so the existing parser can work
"""

import re
from pathlib import Path

def normalize_html(html):
    """
    Convert new LibreOffice 25.8 format to old LibreOffice 7.3 format
    Main change: <font face="...">text</font> -> <span>text</span>
    """

    html = re.sub(
        r'<font face="Times New Roman, serif">([^<]+)</font>',
        r'<span>\1</span>',
        html
    )

    html = re.sub(
        r'<font face="Times New Roman, serif"><font size="([^"]+)" style="font-size: ([^"]+)">',
        r'<font size="\1" style="font-size: \2">',
        html
    )

    html = re.sub(
        r'<font face="Times New Roman, serif">',
        r'<font>',
        html
    )

    return html

def main():
    print("🔄 Normalizing new source HTML structure...")

    input_path = Path('.devkit/analysis/new_sources_combined.html')
    output_path = Path('.devkit/analysis/new_sources_normalized.html')

    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return 1

    html = input_path.read_text(encoding='utf-8')

    print(f"   Original size: {len(html):,} bytes")

    normalized = normalize_html(html)

    print(f"   Normalized size: {len(normalized):,} bytes")

    output_path.write_text(normalized, encoding='utf-8')

    print(f"✅ Normalized HTML saved: {output_path}")

    old_h1 = re.findall(r'<h1[^>]*>\s*<span[^>]*>(?:&shy;)?([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə])</span></h1>', normalized)
    new_h1 = re.findall(r'<h1[^>]*>\s*<font[^>]*>(?:&shy;)?([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə])</font></h1>', normalized)

    print(f"   Letter headers (span format): {len(old_h1)}")
    print(f"   Letter headers (font format): {len(new_h1)}")

    if new_h1:
        print("\n⚠️  Still has font-based h1 tags, converting...")
        normalized = re.sub(
            r'(<h1[^>]*>)\s*<font[^>]*>((?:&shy;)?[^<]+)</font>(</h1>)',
            r'\1<span>\2</span>\3',
            normalized
        )

    bare_h1_pattern = r'(<h1[^>]*>)\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūəḎḌḤṬṢŠǦĠČŽ]+)\s*(</h1>)'
    bare_h1_matches = re.findall(bare_h1_pattern, normalized)
    if bare_h1_matches:
        print(f"\n⚠️  Found {len(bare_h1_matches)} bare h1 tags (no span/font), wrapping...")
        normalized = re.sub(bare_h1_pattern, r'\1<span>\2</span>\3', normalized)

    stem_header_pattern = r'(<font size="4"[^>]*><b>)([IVX]+:\s*)(</b></font>)'
    stem_matches = re.findall(stem_header_pattern, normalized)
    if stem_matches:
        print(f"\n⚠️  Found {len(stem_matches)} stem headers without span tags, adding...")
        normalized = re.sub(stem_header_pattern, r'\1<span>\2</span>\3', normalized)

    stem_form_pattern = r'(<font size="4"[^>]*><i><b>)([^<]+)(</b></i></font>)'
    form_matches = re.findall(stem_form_pattern, normalized)
    if form_matches:
        print(f"\n⚠️  Found {len(form_matches)} stem forms without span tags, adding...")
        normalized = re.sub(stem_form_pattern, r'\1<span>\2</span>\3', normalized)

    remove_size4_from_forms = r'<font size="4" style="font-size: 14pt"><i><b><span>'
    size4_form_count = len(re.findall(remove_size4_from_forms, normalized))
    if size4_form_count > 0:
        print(f"\n⚠️  Found {size4_form_count} italic forms with size=4, removing size attribute...")
        normalized = re.sub(r'(<font) size="4" style="font-size: 14pt"(><i><b><span>)', r'\1\2', normalized)

    double_font_pattern = r'(</font></font>)(<font><i>)'
    double_font_matches = re.findall(double_font_pattern, normalized)
    if double_font_matches:
        print(f"\n⚠️  Found {len(double_font_matches)} stem forms missing double font nesting, adding...")
        normalized = re.sub(double_font_pattern, r'\1<font><font>\2', normalized)

    output_path.write_text(normalized, encoding='utf-8')

    verification = re.findall(r'<h1[^>]*>\s*<span[^>]*>(?:&shy;)?([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūəḎḌḤṬṢŠǦĠČŽ]+)</span></h1>', normalized)
    print(f"   ✓ Final letter headers with span tags: {len(verification)}")
    print(f"   Letters: {', '.join(verification)}")

    stem_verification = re.findall(r'<font size="4"[^>]*><b><span[^>]*>[IVX]+:', normalized)
    print(f"   ✓ Stem headers with span tags: {len(stem_verification)}")

if __name__ == '__main__':
    main()
