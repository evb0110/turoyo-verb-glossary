#!/usr/bin/env python3
"""Find all examples with unbalanced curly quotes (indicating nested quote issue)"""

import json
import glob
import os

split_examples = []

for filepath in glob.glob('/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/analysis/docx_v2_verbs/*.json'):
    try:
        data = json.load(open(filepath))
        root = data.get('root', '')

        for stem in data.get('stems', []):
            stem_name = stem.get('stem', '?')
            for conj_type, examples in stem.get('conjugations', {}).items():
                for ex in examples:
                    translations = ex.get('translations', [])
                    for trans in translations:
                        # Check for curly quote U+2018 followed by text ending with U+2019 but incomplete
                        if '\u2018' in trans:
                            # Count opening and closing curly quotes
                            open_count = trans.count('\u2018')
                            close_count = trans.count('\u2019')
                            if open_count != close_count:
                                split_examples.append({
                                    'file': os.path.basename(filepath),
                                    'root': root,
                                    'stem': stem_name,
                                    'conj': conj_type,
                                    'trans': trans,
                                    'open': open_count,
                                    'close': close_count
                                })
    except Exception as e:
        print(f"Error in {filepath}: {e}")

print(f'Found {len(split_examples)} examples with unbalanced curly quotes')
print()
for ex in split_examples:
    print(f'{ex["root"]:15} | {ex["stem"]:12} | {ex["conj"]:18} | O:{ex["open"]} C:{ex["close"]}')
    print(f'  {ex["trans"][:100]}')
    print()
