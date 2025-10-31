#!/usr/bin/env python3
"""
Prepare new multi-file sources for parsing
Concatenates the 7 HTML files into a single file that the parser can process
"""

import re
from pathlib import Path

def extract_body_content(html_path):
    """Extract just the body content from an HTML file"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    if body_match:
        return body_match.group(1)
    return ""

def main():
    source_dir = Path('.devkit/new-source')

    source_files = [
        '1. ʔ, ʕ, b, č.html',
        '2. d, f, g, ġ, ǧ.html',
        '3. h,ḥ,k.html',
        '4. l,m,n,p.html',
        '5. q,r,s,ṣ.html',
        '6. š,t,ṭ,ṯ.html',
        '7. v, w, x, y, z, ž.html',
    ]

    print("🔄 Extracting body content from new source files...")

    combined_bodies = []
    for filename in source_files:
        filepath = source_dir / filename
        if not filepath.exists():
            print(f"❌ Missing file: {filename}")
            return

        print(f"  ✓ {filename}")
        body_content = extract_body_content(filepath)
        combined_bodies.append(body_content)

    first_file = source_dir / source_files[0]
    with open(first_file, 'r', encoding='utf-8') as f:
        first_html = f.read()

    head_match = re.search(r'(<!DOCTYPE html>.*?<body[^>]*>)', first_html, re.DOTALL)
    header = head_match.group(1) if head_match else '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8"/>\n</head>\n<body>\n'

    full_html = header + '\n'.join(combined_bodies) + '\n</body>\n</html>'

    output_path = Path('.devkit/analysis/new_sources_combined.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"\n✅ Combined file created: {output_path}")
    print(f"   Total size: {len(full_html):,} bytes")

    h1_count = len(re.findall(r'<h1', full_html))
    print(f"   Letter sections (h1 tags): {h1_count}")

    root_pattern = r'<p class="western"><font[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})'
    estimated_roots = len(re.findall(root_pattern, full_html))
    print(f"   Estimated root entries: {estimated_roots}")

if __name__ == '__main__':
    main()
