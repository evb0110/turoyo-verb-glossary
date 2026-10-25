#!/usr/bin/env python3
"""
Diagnostic script to examine exact formatting of specific verbs in DOCX
"""

import re
from pathlib import Path
from docx import Document

def diagnose_verb(docx_path, target_root):
    """Extract detailed formatting info for a specific verb"""
    print(f"\n{'='*80}")
    print(f"Analyzing '{target_root}' in {docx_path.name}")
    print(f"{'='*80}")

    doc = Document(docx_path)
    in_verb_section = False
    para_count = 0

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        if not text:
            continue

        if target_root in text and not in_verb_section:
            in_verb_section = True
            print(f"\n🎯 FOUND ROOT at paragraph {i}: '{text[:100]}'")

        if in_verb_section:
            para_count += 1

            if para_count > 30:
                print("\n⛔ Stopping after 30 paragraphs")
                break

            if text and len(text) < 200:
                print(f"\n--- Para {i} (count {para_count}) ---")
                print(f"Text: {text[:150]}")
                print(f"Style: {para.style.name if para.style else 'None'}")

                for j, run in enumerate(para.runs):
                    if run.text.strip():
                        size = run.font.size.pt if run.font.size else None
                        print(f"  Run {j}: text='{run.text[:50]}' | bold={run.bold} | italic={run.italic} | size={size}pt")

                has_bold = any(r.bold for r in para.runs)
                has_italic = any(r.italic for r in para.runs)
                sizes = [r.font.size.pt for r in para.runs if r.font.size]

                print(f"  Summary: has_bold={has_bold}, has_italic={has_italic}, sizes={sizes}")

                is_stem = re.match(r'^([IVX]+):\s*', text)
                if is_stem:
                    print(f"  ⚠️  MATCHES STEM PATTERN: {is_stem.group(1)}")
                    print(f"  Stem detection checks:")
                    print(f"    - has_bold: {has_bold}")
                    print(f"    - has_italic: {has_italic}")
                    print(f"    - has_14pt: {14.0 in sizes}")
                    print(f"    - matches pattern: True")

                if re.match(r'^[IVX]+:', text):
                    print(f"  🔍 This looks like a stem header!")

            if re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})\s', text) and para_count > 5:
                print(f"\n⏹️  Next verb detected, stopping")
                break

def main():
    docx_dir = Path('source/glossary-docx/2026-10-21')

    diagnose_verb(docx_dir / '4. l,m,n,p.docx', 'pčq')
    diagnose_verb(docx_dir / '6. š,t,ṭ,ṯ.docx', 'ṯny')

if __name__ == '__main__':
    main()
