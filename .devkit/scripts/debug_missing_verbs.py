#!/usr/bin/env python3
"""
Debug parser to trace what happens to šry 1, tky, and zyr 2
"""

import re
import json
from pathlib import Path
from docx import Document
from collections import defaultdict

class DebugDocxParser:
    """Parser with extensive debug logging for 3 specific verbs"""

    def __init__(self):
        self.verbs = []
        self.stats = defaultdict(int)
        self.debug_roots = {'šry 1', 'tky', 'zyr 2', 'šry', 'zyr'}

    def is_letter_header(self, para):
        return para.style and para.style.name == 'Heading 1'

    def is_root_paragraph(self, para):
        if not para.text.strip():
            return False
        has_italic = any(r.italic for r in para.runs)
        sizes = [r.font.size.pt for r in para.runs if r.font.size]
        has_11pt = 11.0 in sizes
        text = para.text.strip()
        turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə'
        has_root = re.match(f'^([{turoyo_chars}]{{2,6}})(?:\s+\d+)?(?:\s|\(|$)', text)

        is_cross_ref = bool(re.search(r'→|See\s+[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]', text))

        return has_italic and has_11pt and has_root and not is_cross_ref

    def extract_root_and_etymology(self, text):
        root_match = re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6}(?:\s+\d+)?)(?:\s|\(|$)', text)
        if not root_match:
            return None, None

        root = root_match.group(1).strip()

        # DEBUG
        if any(target in root or target in text for target in self.debug_roots):
            print(f'\n🔍 DEBUG extract_root_and_etymology:')
            print(f'   Input text: {text[:100]}')
            print(f'   Extracted root: "{root}"')

        return root, None

    def parse_document(self, docx_path):
        """Simple parser focusing on root detection"""
        print(f"\n📖 {docx_path.name}")

        doc = Document(docx_path)
        current_verb = None

        for para in doc.paragraphs:
            if self.is_letter_header(para):
                continue

            if self.is_root_paragraph(para):
                if current_verb:
                    self.verbs.append(current_verb)
                    self.stats['verbs_saved'] += 1

                root, etymology = self.extract_root_and_etymology(para.text)
                if root:
                    # DEBUG
                    if any(target in root for target in self.debug_roots):
                        print(f'\n✅ ROOT PARAGRAPH DETECTED:')
                        print(f'   Root: "{root}"')
                        print(f'   Text: {para.text[:100]}')

                    current_verb = {
                        'root': root,
                        'stems': []
                    }
                    self.stats['verbs_parsed'] += 1

        if current_verb:
            self.verbs.append(current_verb)
            self.stats['verbs_saved'] += 1

        print(f"   ✓ {self.stats['verbs_parsed']} verbs parsed, {self.stats['verbs_saved']} saved")

    def add_homonym_numbers(self):
        """Add sequential numbers to homonyms"""
        print("\n🔍 Homonym numbering...")

        # DEBUG: Show verbs before numbering
        print('\n   Verbs before numbering:')
        for verb in self.verbs:
            if any(target in verb['root'] for target in self.debug_roots):
                print(f'     "{verb["root"]}"')

        root_groups = defaultdict(list)
        for idx, verb in enumerate(self.verbs):
            # Extract base root (without number)
            base_root = re.sub(r'\s+\d+$', '', verb['root'])
            root_groups[base_root].append((idx, verb))

        numbered_count = 0
        for base_root, entries in root_groups.items():
            if len(entries) > 1:
                print(f"\n   ℹ️  Found {len(entries)} entries for base root '{base_root}'")
                for entry_num, (idx, verb) in enumerate(entries, 1):
                    old_root = self.verbs[idx]['root']
                    self.verbs[idx]['root'] = f"{base_root} {entry_num}"
                    print(f"        {old_root} → {self.verbs[idx]['root']}")
                numbered_count += len(entries)

        # DEBUG: Show verbs after numbering
        print('\n   Verbs after numbering:')
        for verb in self.verbs:
            if any(target in verb['root'] for target in self.debug_roots):
                print(f'     "{verb["root"]}"')

        print(f"\n   ✅ Numbered {numbered_count} entries")

    def parse_files(self, docx_files):
        for docx_file in docx_files:
            self.parse_document(Path(docx_file))

        self.add_homonym_numbers()

        print(f'\n📊 FINAL RESULTS:')
        print(f'   Total verbs: {len(self.verbs)}')

        print(f'\n🎯 Target verbs in final output:')
        found = []
        for verb in self.verbs:
            if any(target in verb['root'] for target in self.debug_roots):
                found.append(verb['root'])
                print(f'     ✓ {verb["root"]}')

        missing = self.debug_roots - set(found)
        if missing:
            print(f'\n❌ Missing from output:')
            for m in missing:
                print(f'     ✗ {m}')

def main():
    parser = DebugDocxParser()

    # Parse only the files containing our target verbs
    files = [
        '.devkit/new-source-docx/6. š,t,ṭ,ṯ.docx',
        '.devkit/new-source-docx/7. v, w, x, y, z, ž.docx'
    ]

    parser.parse_files(files)

if __name__ == '__main__':
    main()
