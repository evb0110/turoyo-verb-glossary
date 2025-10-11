#!/usr/bin/env python3
"""
Split verbs_final.json into individual verb files for web serving
"""

import json
from pathlib import Path

def split_verbs():
    print("🔄 Splitting verbs_final.json into individual files...")

    # Read the master file
    data_file = Path('data/verbs_final.json')
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    verbs = data['verbs']
    print(f"📚 Processing {len(verbs)} verbs...")

    # Create output directory
    output_dir = Path('public/appdata/api/verbs')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write individual files
    for verb in verbs:
        root = verb['root']
        # Create filename from root
        filename = f"{root}.json"

        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(verb, f, ensure_ascii=False, indent=2)

    print(f"✅ Created {len(verbs)} individual verb files in {output_dir}")
    print(f"   📊 Total verbs: {data['metadata']['total_verbs']}")
    print(f"   📊 Total stems: {data['metadata']['total_stems']}")
    print(f"   📊 Total examples: {data['metadata']['total_examples']}")

if __name__ == '__main__':
    split_verbs()
