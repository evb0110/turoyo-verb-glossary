#!/usr/bin/env python3
"""
Verification Tool - Compare extracted JSON against original HTML
Allows manual spot-checking of specific verbs
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

class SourceVerifier:
    def __init__(self, json_path, html_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.verbs = {v['root']: v for v in self.data['verbs']}

    def find_verb_in_html(self, root):
        """Find the HTML section for a specific root"""
        # Pattern to find the root entry
        pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>' + re.escape(root) + r'</span>'

        match = re.search(pattern, self.html)
        if not match:
            return None

        start = match.start()

        # Find next root or end
        next_pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6}</span>'
        next_match = re.search(next_pattern, self.html[match.end():])

        end = match.end() + next_match.start() if next_match else len(self.html)

        return self.html[start:end]

    def verify_verb(self, root):
        """Verify a specific verb against source"""
        print(f"\n{'='*70}")
        print(f"VERIFYING: {root}")
        print('='*70)

        # Get JSON data
        verb_data = self.verbs.get(root)
        if not verb_data:
            print(f"❌ {root} not found in JSON")
            return

        # Get HTML source
        html_section = self.find_verb_in_html(root)
        if not html_section:
            print(f"❌ {root} not found in HTML")
            return

        print(f"\n✓ Found in both JSON and HTML")

        # Display JSON data
        print(f"\n📋 JSON DATA:")
        print(f"  Root: {verb_data['root']}")

        etym = verb_data.get('etymology')
        if etym:
            print(f"  Etymology: {etym.get('source', 'N/A')}")
            if 'source_root' in etym:
                print(f"    Source root: {etym['source_root']}")
            if 'meaning' in etym:
                print(f"    Meaning: {etym['meaning'][:80]}...")

        print(f"  Stems: {len(verb_data.get('stems', []))}")

        for i, stem in enumerate(verb_data.get('stems', []), 1):
            print(f"\n  Stem {i}: {stem['stem']}")
            print(f"    Forms: {', '.join(stem['forms'])}")
            print(f"    Conjugations: {', '.join(stem['conjugations'].keys())}")

            # Show first example from each conjugation
            for conj_type, examples in stem['conjugations'].items():
                if examples:
                    ex = examples[0]
                    turoyo = ex.get('turoyo', '')[:60]
                    trans = ex.get('translations', [''])[0][:60] if ex.get('translations') else ''
                    print(f"      {conj_type}:")
                    print(f"        Turoyo: {turoyo}...")
                    if trans:
                        print(f"        Trans:  {trans}...")

        # Display HTML source (formatted)
        print(f"\n📄 HTML SOURCE (first 1000 chars):")
        soup = BeautifulSoup(html_section[:1000], 'html.parser')
        print(soup.get_text()[:800])

        return True

    def batch_verify(self, roots):
        """Verify multiple roots"""
        results = []

        for root in roots:
            result = self.verify_verb(root)
            results.append((root, result))
            print()

        # Summary
        print(f"\n{'='*70}")
        print("VERIFICATION SUMMARY")
        print('='*70)

        verified = sum(1 for _, r in results if r)
        print(f"  Verified: {verified}/{len(roots)}")

    def interactive_verify(self):
        """Interactive verification mode"""
        print("\n" + "="*70)
        print("INTERACTIVE VERIFICATION MODE")
        print("="*70)
        print("\nEnter verb roots to verify (or 'quit' to exit)")
        print("Available roots:", ', '.join(list(self.verbs.keys())[:20]), "...")
        print()

        while True:
            root = input("Enter root: ").strip()

            if root.lower() in ['quit', 'exit', 'q']:
                break

            if root == 'random':
                import random
                root = random.choice(list(self.verbs.keys()))
                print(f"Random verb: {root}")

            if root in self.verbs:
                self.verify_verb(root)
            else:
                print(f"❌ '{root}' not found. Try one of: {', '.join(list(self.verbs.keys())[:10])}")


def main():
    json_file = Path('data/verbs_final.json')
    html_file = Path('source/Turoyo_all_2024.html')

    if not json_file.exists() or not html_file.exists():
        print("❌ Required files not found")
        return

    verifier = SourceVerifier(json_file, html_file)

    # Verify some sample roots
    sample_roots = ['ʕbd', 'ʕbr', 'ʔbʕ', 'ʔḏʕ', 'ʔmr']
    print("🔍 Verifying sample roots...")
    verifier.batch_verify(sample_roots)

    # Uncomment for interactive mode:
    # verifier.interactive_verify()


if __name__ == '__main__':
    main()
