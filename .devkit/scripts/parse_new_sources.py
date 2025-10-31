#!/usr/bin/env python3
"""
Parse new source files using the existing parser
This is a wrapper that points the parser at the combined new sources
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'parser'))

from parse_verbs import TuroyoVerbParser

def main():
    print("=" * 80)
    print("PARSING NEW SOURCES")
    print("=" * 80)

    normalized_path = '.devkit/analysis/new_sources_normalized.html'

    if not Path(normalized_path).exists():
        print(f"❌ Normalized source file not found: {normalized_path}")
        print("   Run prepare_new_sources.py and normalize_new_sources.py first!")
        return 1

    parser = TuroyoVerbParser(normalized_path)
    parser.parse_all()

    output_path = '.devkit/analysis/new_sources_parsed.json'
    parser.save_json(output_path)

    output_dir = Path('.devkit/analysis/new_verbs')
    output_dir.mkdir(parents=True, exist_ok=True)

    for f in output_dir.glob('*.json'):
        f.unlink()

    for verb in parser.verbs:
        root = verb['root']
        filename = f"{root}.json"
        filepath = output_dir / filename

        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(verb, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Split into {len(parser.verbs)} individual files in {output_dir}")

    print("\n" + "=" * 80)
    print("PARSING COMPLETE!")
    print("=" * 80)
    print(f"📚 Total verbs: {len(parser.verbs)}")
    print(f"📖 Total stems: {parser.stats['stems_parsed']}")
    print(f"🔗 Cross-references: {parser.stats.get('cross_references', 0)}")
    print(f"❓ Uncertain entries: {parser.stats.get('uncertain_entries', 0)}")
    print(f"🔢 Homonyms numbered: {parser.stats.get('homonyms_numbered', 0)}")
    print("=" * 80)

if __name__ == '__main__':
    sys.exit(main() or 0)
