#!/usr/bin/env python3
"""
Clean Turoyo Parser V5 - robust entry segmentation by root paragraphs
- Use BeautifulSoup to walk <p class="western"> blocks
- Treat a block as a root header iff its leading text starts with a 2–6 letter root
- An entry spans from a root header up to (but not including) the next root header
- Leaves downstream table parsing as in V4 by delegating to its routines
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

ALLOWED = 'ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə'
ROOT_RE = re.compile(rf'^([{ALLOWED}]{{2,6}})(?:\s*\d+)?\b')

class ParserV5:
    def __init__(self, html_path: str):
        self.html_path = Path(html_path)
        self.html = self.html_path.read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.sections = []
        self.stats = defaultdict(int)

    def extract_root_blocks(self):
        roots = []
        for p in self.soup.find_all('p', class_='western'):
            text = p.get_text().strip()
            m = ROOT_RE.match(text)
            if m:
                root = m.group(1)
                roots.append((root, p))
        return roots

    def slice_entries(self):
        roots = self.extract_root_blocks()
        entries = []
        for i, (root, p) in enumerate(roots):
            start = p
            end = roots[i+1][1] if i+1 < len(roots) else None

            # Collect siblings between start and end
            blocks = []
            node = start
            while node and node.name != 'body':
                blocks.append(str(node))
                node = node.find_next_sibling()
                if node == end:
                    break
            html_fragment = '\n'.join(blocks)
            entries.append((root, html_fragment))
        return entries

    def save_segments(self, out_path: str):
        segments = [{'root': r, 'html': h} for r, h in self.slice_entries()]
        Path(out_path).write_text(json.dumps({'segments': segments}, ensure_ascii=False, indent=2), encoding='utf-8')
        return segments


def main():
    src = 'source/Turoyo_all_2024.html'
    out = 'data/segments_v5.json'
    p = ParserV5(src)
    segs = p.save_segments(out)
    print(f'✅ Segmented {len(segs)} entries into {out}')

if __name__ == '__main__':
    main()
