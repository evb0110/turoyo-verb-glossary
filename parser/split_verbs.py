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

    # Track written files to detect duplicates
    written_files = set()
    duplicate_count = 0

    # Write individual files
    for verb in verbs:
        root = verb['root']
        # Create filename from root
        filename = f"{root}.json"

        # Check for duplicate
        if filename in written_files:
            duplicate_count += 1
            print(f"   ⚠️  Warning: Duplicate root '{root}' - file already exists!")
            print(f"       This indicates a parser bug where multiple entries have the same root name.")
            print(f"       The second entry will overwrite the first.")

        written_files.add(filename)

        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(verb, f, ensure_ascii=False, indent=2)

    print(f"✅ Created {len(written_files)} individual verb files in {output_dir}")
    print(f"   📊 Total verbs: {data['metadata']['total_verbs']}")
    print(f"   📊 Total stems: {data['metadata']['total_stems']}")
    print(f"   📊 Total examples: {data['metadata']['total_examples']}")

    if duplicate_count > 0:
        print(f"   ⚠️  WARNING: {duplicate_count} duplicate roots detected!")
        print(f"       Data loss occurred - check parser's root extraction logic.")

if __name__ == '__main__':
    split_verbs()
