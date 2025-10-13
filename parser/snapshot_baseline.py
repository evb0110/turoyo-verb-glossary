#!/usr/bin/env python3
"""
BASELINE SNAPSHOT GENERATOR
============================
Creates a "known good" baseline of parser output for regression testing.

This script:
- Reads all verb JSON files from public/appdata/api/verbs/
- Generates SHA256 checksums for each file
- Creates summary statistics (counts, structures, etc.)
- Saves baseline data to data/baseline/

Usage:
    python3 parser/snapshot_baseline.py              # Create/update baseline
    python3 parser/snapshot_baseline.py --report     # Show current baseline info

Author: Claude Code
Created: 2025-10-13
"""

import json
import hashlib
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class BaselineSnapshot:
    """Generate baseline snapshot of parser output"""

    def __init__(self, verbs_dir='public/appdata/api/verbs'):
        self.verbs_dir = Path(verbs_dir)
        self.baseline_dir = Path('data/baseline')
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

    def compute_file_hash(self, filepath):
        """Compute SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            sha256.update(f.read())
        return sha256.hexdigest()

    def extract_verb_structure(self, verb_data):
        """Extract structural metadata from verb entry"""
        structure = {
            'root': verb_data.get('root'),
            'has_etymology': verb_data.get('etymology') is not None,
            'has_cross_reference': verb_data.get('cross_reference') is not None,
            'is_uncertain': verb_data.get('uncertain', False),
            'stem_count': len(verb_data.get('stems', [])),
            'stems': []
        }

        for stem in verb_data.get('stems', []):
            stem_info = {
                'stem': stem.get('stem'),
                'form_count': len(stem.get('forms', [])),
                'conjugation_types': sorted(stem.get('conjugations', {}).keys()),
                'example_count': sum(
                    len(examples) for examples in stem.get('conjugations', {}).values()
                )
            }
            structure['stems'].append(stem_info)

        # Etymology details
        if verb_data.get('etymology'):
            etym = verb_data['etymology']
            structure['etymology_details'] = {
                'etymon_count': len(etym.get('etymons', [])),
                'has_relationship': 'relationship' in etym,
                'sources': [e.get('source') for e in etym.get('etymons', [])]
            }

        return structure

    def generate_baseline(self):
        """Generate complete baseline snapshot"""
        print("📸 Generating baseline snapshot...")
        print(f"   Reading from: {self.verbs_dir}")

        baseline = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'parser_version': '4.0.0-master',
                'description': 'Known good parser output baseline'
            },
            'verbs': {},
            'summary': {
                'total_files': 0,
                'total_stems': 0,
                'total_examples': 0,
                'stem_type_counts': defaultdict(int),
                'conjugation_type_counts': defaultdict(int),
                'etymology_sources': defaultdict(int),
                'roots_with_homonyms': [],
                'roots_with_cross_refs': [],
                'uncertain_roots': []
            }
        }

        # Process each verb file
        verb_files = sorted(self.verbs_dir.glob('*.json'))
        for i, filepath in enumerate(verb_files, 1):
            if i % 100 == 0:
                print(f"   [{i}/{len(verb_files)}] Processing...", end='\r')

            try:
                # Read and parse
                with open(filepath, 'r', encoding='utf-8') as f:
                    verb_data = json.load(f)

                # Compute hash
                file_hash = self.compute_file_hash(filepath)

                # Extract structure
                structure = self.extract_verb_structure(verb_data)

                # Store in baseline
                root = verb_data['root']
                baseline['verbs'][root] = {
                    'filename': filepath.name,
                    'hash': file_hash,
                    'structure': structure
                }

                # Update summary statistics
                baseline['summary']['total_files'] += 1
                baseline['summary']['total_stems'] += structure['stem_count']

                for stem in structure['stems']:
                    baseline['summary']['stem_type_counts'][stem['stem']] += 1
                    baseline['summary']['total_examples'] += stem['example_count']
                    for conj_type in stem['conjugation_types']:
                        baseline['summary']['conjugation_type_counts'][conj_type] += 1

                # Track etymology sources
                if 'etymology_details' in structure:
                    for source in structure['etymology_details']['sources']:
                        baseline['summary']['etymology_sources'][source] += 1

                # Track special cases
                if ' ' in root and root[-1].isdigit():
                    baseline['summary']['roots_with_homonyms'].append(root)
                if verb_data.get('cross_reference'):
                    baseline['summary']['roots_with_cross_refs'].append(root)
                if verb_data.get('uncertain'):
                    baseline['summary']['uncertain_roots'].append(root)

            except Exception as e:
                print(f"\n   ⚠️  Error processing {filepath.name}: {e}")
                continue

        print(f"\n   ✅ Processed {baseline['summary']['total_files']} verb files")

        # Convert defaultdicts to regular dicts for JSON serialization
        baseline['summary']['stem_type_counts'] = dict(baseline['summary']['stem_type_counts'])
        baseline['summary']['conjugation_type_counts'] = dict(baseline['summary']['conjugation_type_counts'])
        baseline['summary']['etymology_sources'] = dict(baseline['summary']['etymology_sources'])

        return baseline

    def save_baseline(self, baseline):
        """Save baseline to disk"""
        baseline_file = self.baseline_dir / 'baseline.json'
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Baseline saved to: {baseline_file}")
        print(f"   📊 Summary:")
        print(f"      • Total verbs: {baseline['summary']['total_files']}")
        print(f"      • Total stems: {baseline['summary']['total_stems']}")
        print(f"      • Total examples: {baseline['summary']['total_examples']}")
        print(f"      • Homonyms: {len(baseline['summary']['roots_with_homonyms'])}")
        print(f"      • Cross-references: {len(baseline['summary']['roots_with_cross_refs'])}")
        print(f"      • Uncertain entries: {len(baseline['summary']['uncertain_roots'])}")

        # Save summary separately for quick access
        summary_file = self.baseline_dir / 'summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(baseline['summary'], f, ensure_ascii=False, indent=2)

        return baseline_file

    def load_baseline(self):
        """Load existing baseline"""
        baseline_file = self.baseline_dir / 'baseline.json'
        if not baseline_file.exists():
            return None

        with open(baseline_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def report_baseline(self):
        """Display baseline information"""
        baseline = self.load_baseline()
        if not baseline:
            print("❌ No baseline found. Run without --report to create one.")
            return

        print("=" * 80)
        print("BASELINE SNAPSHOT REPORT")
        print("=" * 80)
        print(f"Created: {baseline['metadata']['created']}")
        print(f"Parser Version: {baseline['metadata']['parser_version']}")
        print()
        print("SUMMARY STATISTICS:")
        print(f"  • Total verbs: {baseline['summary']['total_files']}")
        print(f"  • Total stems: {baseline['summary']['total_stems']}")
        print(f"  • Total examples: {baseline['summary']['total_examples']}")
        print(f"  • Homonyms: {len(baseline['summary']['roots_with_homonyms'])}")
        print(f"  • Cross-references: {len(baseline['summary']['roots_with_cross_refs'])}")
        print(f"  • Uncertain entries: {len(baseline['summary']['uncertain_roots'])}")
        print()
        print("STEM TYPES:")
        for stem_type, count in sorted(baseline['summary']['stem_type_counts'].items()):
            print(f"  • {stem_type}: {count}")
        print()
        print("TOP CONJUGATION TYPES:")
        conj_types = sorted(
            baseline['summary']['conjugation_type_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for conj_type, count in conj_types:
            print(f"  • {conj_type}: {count}")
        print()
        print("ETYMOLOGY SOURCES:")
        for source, count in sorted(baseline['summary']['etymology_sources'].items()):
            print(f"  • {source}: {count}")
        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate baseline snapshot of parser output'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Display baseline report instead of creating new baseline'
    )
    args = parser.parse_args()

    snapshot = BaselineSnapshot()

    if args.report:
        snapshot.report_baseline()
    else:
        print("=" * 80)
        print("CREATING BASELINE SNAPSHOT")
        print("=" * 80)
        baseline = snapshot.generate_baseline()
        snapshot.save_baseline(baseline)
        print("=" * 80)
        print("✅ BASELINE CREATION COMPLETE")
        print("=" * 80)


if __name__ == '__main__':
    main()
