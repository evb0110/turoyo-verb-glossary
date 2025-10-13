#!/usr/bin/env python3
"""
Generate search index from verbs_final.json
This creates a lightweight index optimized for fast searching
"""

import json
from pathlib import Path
from datetime import datetime

def generate_search_index():
    """Generate search index from parsed verbs"""

    # Load full verb data
    verbs_file = Path('data/verbs_final.json')
    with open(verbs_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    verbs = data.get('verbs', [])

    # Build search index
    index_verbs = []

    for verb in verbs:
        root = verb['root']

        # Extract etymology sources
        etymology_sources = []
        etymology = verb.get('etymology')
        if etymology and 'etymons' in etymology:
            for etymon in etymology['etymons']:
                source = etymon.get('source', '')
                if source and source not in etymology_sources:
                    etymology_sources.append(source)

        # Extract stems
        stems = []
        for stem in verb.get('stems', []):
            stem_name = stem.get('stem', '')
            if stem_name and stem_name not in stems:
                stems.append(stem_name)

        # Extract forms
        forms = []
        for stem in verb.get('stems', []):
            for form in stem.get('forms', []):
                if form and form not in forms:
                    forms.append(form)

        # Count examples
        example_count = 0
        for stem in verb.get('stems', []):
            conjugations = stem.get('conjugations', {})
            for conj_type, examples in conjugations.items():
                example_count += len(examples)

        # Build index entry
        index_entry = {
            'root': root,
            'etymology_sources': etymology_sources,
            'stems': stems,
            'forms': forms,
            'example_count': example_count
        }

        # Optional fields
        if 'Detransitive' in stems:
            index_entry['has_detransitive'] = True

        cross_ref = verb.get('cross_reference')
        if cross_ref:
            index_entry['cross_reference'] = cross_ref

        index_verbs.append(index_entry)

    # Build final index
    search_index = {
        'version': '1.0',
        'total_verbs': len(index_verbs),
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'verbs': index_verbs
    }

    # Save to file
    output_file = Path('public/appdata/api/search-index.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)

    print(f"✅ Search index generated: {output_file}")
    print(f"   📊 {len(index_verbs)} verbs indexed")

if __name__ == '__main__':
    generate_search_index()
