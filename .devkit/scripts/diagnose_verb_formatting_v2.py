#!/usr/bin/env python3
"""
Diagnostic script v2 - Better root detection
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

        turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə'
        is_root_line = re.match(f'^({target_root})(\s+\d+|\s+\\(|$)', text)

        if is_root_line and not in_verb_section:
            in_verb_section = True
            print(f"\n🎯 FOUND ROOT HEADER at paragraph {i}: '{text[:100]}'")

        if in_verb_section:
            para_count += 1

            if para_count > 50:
                print("\n⛔ Stopping after 50 paragraphs")
                break

            if text:
                print(f"\n--- Para {i} (count {para_count}) ---")
                print(f"Text: {text[:200]}")
                print(f"Style: {para.style.name if para.style else 'None'}")

                for j, run in enumerate(para.runs[:5]):
                    if run.text.strip():
                        size = run.font.size.pt if run.font.size else None
                        print(f"  Run {j}: text='{run.text[:40]}' | bold={run.bold} | italic={run.italic} | size={size}pt")

                has_bold = any(r.bold for r in para.runs)
                has_italic = any(r.italic for r in para.runs)
                sizes = [r.font.size.pt for r in para.runs if r.font.size]

                print(f"  Summary: has_bold={has_bold}, has_italic={has_italic}, sizes={list(set(sizes))}")

                is_stem = re.match(r'^([IVX]+):\s*', text)
                if is_stem:
                    print(f"  ⚠️  MATCHES STEM PATTERN: {is_stem.group(1)}")
                    print(f"  Stem detection checks:")
                    print(f"    - has_bold: {has_bold}")
                    print(f"    - has_italic: {has_italic}")
                    print(f"    - has_14pt: {14.0 in sizes}")

                if 'Detransitive' in text:
                    print(f"  🔍 DETRANSITIVE marker found!")

            next_root = re.match(f'^([{turoyo_chars}]{{2,6}})(\s+\d+|\s+\\()', text)
            if next_root and para_count > 5 and next_root.group(1) != target_root:
                print(f"\n⏹️  Next verb '{next_root.group(1)}' detected, stopping")
                break

def main():
    docx_dir = Path('.devkit/new-source-docx')

    diagnose_verb(docx_dir / '4. l,m,n,p.docx', 'pčq')
    diagnose_verb(docx_dir / '6. š,t,ṭ,ṯ.docx', 'ṯny')

if __name__ == '__main__':
    main()
