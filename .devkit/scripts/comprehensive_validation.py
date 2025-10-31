#!/usr/bin/env python3
"""
Comprehensive validation comparing DOCX parsing against original baseline
17 years of linguistic research requires 100% accuracy
"""

import json
from pathlib import Path
from collections import defaultdict

class ComprehensiveValidator:
    """Validate DOCX parsing against original data with scientific rigor"""

    def __init__(self, docx_dir=None):
        self.original_dir = Path('server/assets/verbs')
        self.docx_dir = Path(docx_dir) if docx_dir else Path('.devkit/analysis/docx_verbs')

        self.discrepancies = {
            'missing_verbs': [],
            'extra_verbs': [],
            'stem_count_mismatch': [],
            'form_mismatch': [],
            'conjugation_mismatch': [],
            'translation_count_mismatch': [],
            'example_count_mismatch': [],
            'etymology_mismatch': []
        }

        self.stats = {
            'total_original': 0,
            'total_docx': 0,
            'perfect_matches': 0,
            'verbs_with_issues': 0
        }

    def load_all_verbs(self, directory):
        """Load all verb files from directory"""
        verbs = {}
        for file in directory.glob('*.json'):
            try:
                verb = json.loads(file.read_text())
                verbs[verb['root']] = {
                    'file': file.name,
                    'data': verb
                }
            except Exception as e:
                print(f"⚠️  Error loading {file.name}: {e}")
        return verbs

    def compare_stems(self, original_verb, docx_verb):
        """Compare stem structures in detail"""
        orig_stems = original_verb['stems']
        docx_stems = docx_verb['stems']

        issues = []

        if len(orig_stems) != len(docx_stems):
            issues.append({
                'type': 'stem_count',
                'original': len(orig_stems),
                'docx': len(docx_stems)
            })

        # Compare each stem
        for i, orig_stem in enumerate(orig_stems):
            if i >= len(docx_stems):
                issues.append({
                    'type': 'missing_stem',
                    'stem': orig_stem['stem'],
                    'forms': orig_stem['forms']
                })
                continue

            docx_stem = docx_stems[i]

            # Compare stem numbers
            if orig_stem['stem'] != docx_stem['stem']:
                issues.append({
                    'type': 'stem_number_mismatch',
                    'original': orig_stem['stem'],
                    'docx': docx_stem['stem']
                })

            # Compare forms
            orig_forms = set(orig_stem['forms'])
            docx_forms = set(docx_stem['forms'])

            if orig_forms != docx_forms:
                issues.append({
                    'type': 'form_mismatch',
                    'stem': orig_stem['stem'],
                    'missing_forms': list(orig_forms - docx_forms),
                    'extra_forms': list(docx_forms - orig_forms)
                })

            # Compare conjugations
            orig_conjs = set(orig_stem['conjugations'].keys())
            docx_conjs = set(docx_stem['conjugations'].keys())

            if orig_conjs != docx_conjs:
                issues.append({
                    'type': 'conjugation_types_mismatch',
                    'stem': orig_stem['stem'],
                    'missing': list(orig_conjs - docx_conjs),
                    'extra': list(docx_conjs - orig_conjs)
                })

            # Compare example counts per conjugation
            for conj_type in orig_conjs & docx_conjs:
                orig_count = len(orig_stem['conjugations'][conj_type])
                docx_count = len(docx_stem['conjugations'][conj_type])

                if orig_count != docx_count:
                    issues.append({
                        'type': 'example_count_mismatch',
                        'stem': orig_stem['stem'],
                        'conjugation': conj_type,
                        'original': orig_count,
                        'docx': docx_count
                    })

            # Compare translation counts
            orig_translations = sum(
                len(ex['translations'])
                for conj_list in orig_stem['conjugations'].values()
                for ex in conj_list
            )
            docx_translations = sum(
                len(ex['translations'])
                for conj_list in docx_stem['conjugations'].values()
                for ex in conj_list
            )

            if orig_translations != docx_translations:
                issues.append({
                    'type': 'translation_count',
                    'stem': orig_stem['stem'],
                    'original': orig_translations,
                    'docx': docx_translations,
                    'loss_pct': ((orig_translations - docx_translations) / orig_translations * 100) if orig_translations > 0 else 0
                })

        return issues

    def compare_etymology(self, original_verb, docx_verb):
        """Compare etymology structures"""
        orig_etym = original_verb.get('etymology')
        docx_etym = docx_verb.get('etymology')

        if orig_etym and not docx_etym:
            return {'type': 'missing_etymology'}

        if not orig_etym and docx_etym:
            return {'type': 'extra_etymology'}

        if not orig_etym and not docx_etym:
            return None

        # Compare structure
        orig_etymons = orig_etym.get('etymons', [])
        docx_etymons = docx_etym.get('etymons', [])

        if len(orig_etymons) != len(docx_etymons):
            return {
                'type': 'etymon_count_mismatch',
                'original': len(orig_etymons),
                'docx': len(docx_etymons)
            }

        # Check if fields are present
        for i, orig in enumerate(orig_etymons):
            if i >= len(docx_etymons):
                continue

            docx = docx_etymons[i]

            # Original might have: source, source_root, reference, meaning
            # DOCX currently only has: source, raw

            orig_fields = set(orig.keys())
            docx_fields = set(docx.keys())

            missing_fields = orig_fields - docx_fields

            if missing_fields:
                return {
                    'type': 'missing_etymology_fields',
                    'missing': list(missing_fields),
                    'original': orig,
                    'docx': docx
                }

        return None

    def validate_all(self):
        """Comprehensive validation of all verbs"""
        print("=" * 80)
        print("COMPREHENSIVE VALIDATION - 100% ACCURACY REQUIRED")
        print("=" * 80)

        print("\n📖 Loading original verbs...")
        original_verbs = self.load_all_verbs(self.original_dir)
        self.stats['total_original'] = len(original_verbs)
        print(f"   ✓ Loaded {len(original_verbs)} verbs")

        print("\n📖 Loading DOCX verbs...")
        docx_verbs = self.load_all_verbs(self.docx_dir)
        self.stats['total_docx'] = len(docx_verbs)
        print(f"   ✓ Loaded {len(docx_verbs)} verbs")

        # Find missing and extra verbs
        print("\n🔍 Comparing verb lists...")
        orig_roots = set(original_verbs.keys())
        docx_roots = set(docx_verbs.keys())

        missing = orig_roots - docx_roots
        extra = docx_roots - orig_roots

        if missing:
            self.discrepancies['missing_verbs'] = sorted(list(missing))
            print(f"   ⚠️  {len(missing)} verbs MISSING in DOCX")

        if extra:
            self.discrepancies['extra_verbs'] = sorted(list(extra))
            print(f"   ⚠️  {len(extra)} EXTRA verbs in DOCX")

        # Compare common verbs
        common_roots = orig_roots & docx_roots
        print(f"\n🔬 Validating {len(common_roots)} common verbs...")

        verb_issues = {}

        for i, root in enumerate(sorted(common_roots), 1):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(common_roots)}")

            orig_verb = original_verbs[root]['data']
            docx_verb = docx_verbs[root]['data']

            issues = []

            # Compare stems
            stem_issues = self.compare_stems(orig_verb, docx_verb)
            if stem_issues:
                issues.extend(stem_issues)

            # Compare etymology
            etym_issue = self.compare_etymology(orig_verb, docx_verb)
            if etym_issue:
                issues.append(etym_issue)

            if issues:
                verb_issues[root] = issues
                self.stats['verbs_with_issues'] += 1
            else:
                self.stats['perfect_matches'] += 1

        # Categorize issues
        for root, issues in verb_issues.items():
            for issue in issues:
                issue_type = issue['type']

                if issue_type == 'stem_count':
                    self.discrepancies['stem_count_mismatch'].append({
                        'root': root,
                        **issue
                    })
                elif issue_type in ['form_mismatch', 'missing_stem']:
                    self.discrepancies['form_mismatch'].append({
                        'root': root,
                        **issue
                    })
                elif issue_type in ['conjugation_types_mismatch']:
                    self.discrepancies['conjugation_mismatch'].append({
                        'root': root,
                        **issue
                    })
                elif issue_type == 'translation_count':
                    self.discrepancies['translation_count_mismatch'].append({
                        'root': root,
                        **issue
                    })
                elif issue_type == 'example_count_mismatch':
                    self.discrepancies['example_count_mismatch'].append({
                        'root': root,
                        **issue
                    })
                elif 'etymology' in issue_type:
                    self.discrepancies['etymology_mismatch'].append({
                        'root': root,
                        **issue
                    })

        return verb_issues

    def print_report(self):
        """Print comprehensive validation report"""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)

        print(f"\n📊 Overall Statistics:")
        print(f"   Original verbs: {self.stats['total_original']}")
        print(f"   DOCX verbs: {self.stats['total_docx']}")
        print(f"   Perfect matches: {self.stats['perfect_matches']}")
        print(f"   Verbs with issues: {self.stats['verbs_with_issues']}")

        accuracy = (self.stats['perfect_matches'] / self.stats['total_original'] * 100) if self.stats['total_original'] > 0 else 0
        print(f"\n   ✨ Accuracy: {accuracy:.1f}%")

        # Missing verbs
        if self.discrepancies['missing_verbs']:
            print(f"\n❌ MISSING VERBS ({len(self.discrepancies['missing_verbs'])}):")
            for root in self.discrepancies['missing_verbs'][:20]:
                print(f"   - {root}")
            if len(self.discrepancies['missing_verbs']) > 20:
                print(f"   ... and {len(self.discrepancies['missing_verbs']) - 20} more")

        # Extra verbs
        if self.discrepancies['extra_verbs']:
            print(f"\n➕ EXTRA VERBS ({len(self.discrepancies['extra_verbs'])}):")
            for root in self.discrepancies['extra_verbs'][:20]:
                print(f"   - {root}")
            if len(self.discrepancies['extra_verbs']) > 20:
                print(f"   ... and {len(self.discrepancies['extra_verbs']) - 20} more")

        # Stem count mismatches
        if self.discrepancies['stem_count_mismatch']:
            print(f"\n⚠️  STEM COUNT MISMATCHES ({len(self.discrepancies['stem_count_mismatch'])}):")
            for item in self.discrepancies['stem_count_mismatch'][:10]:
                print(f"   - {item['root']}: original={item['original']}, docx={item['docx']}")

        # Translation losses
        if self.discrepancies['translation_count_mismatch']:
            print(f"\n📝 TRANSLATION EXTRACTION ISSUES ({len(self.discrepancies['translation_count_mismatch'])}):")
            total_orig = sum(item['original'] for item in self.discrepancies['translation_count_mismatch'])
            total_docx = sum(item['docx'] for item in self.discrepancies['translation_count_mismatch'])
            loss_pct = ((total_orig - total_docx) / total_orig * 100) if total_orig > 0 else 0
            print(f"   Total original translations: {total_orig}")
            print(f"   Total DOCX translations: {total_docx}")
            print(f"   Loss: {loss_pct:.1f}%")

            print(f"\n   Top 10 verbs with translation losses:")
            sorted_by_loss = sorted(
                self.discrepancies['translation_count_mismatch'],
                key=lambda x: x['original'] - x['docx'],
                reverse=True
            )
            for item in sorted_by_loss[:10]:
                loss = item['original'] - item['docx']
                print(f"   - {item['root']} (stem {item['stem']}): lost {loss} translations ({item['loss_pct']:.0f}%)")

        # Etymology issues
        if self.discrepancies['etymology_mismatch']:
            print(f"\n📚 ETYMOLOGY PARSING ISSUES ({len(self.discrepancies['etymology_mismatch'])}):")
            missing_fields_count = sum(1 for item in self.discrepancies['etymology_mismatch'] if item['type'] == 'missing_etymology_fields')
            print(f"   Missing etymology fields: {missing_fields_count}")

            if missing_fields_count > 0:
                # Show example
                example = next((item for item in self.discrepancies['etymology_mismatch'] if item['type'] == 'missing_etymology_fields'), None)
                if example:
                    print(f"\n   Example ({example['root']}):")
                    print(f"      Missing fields: {example['missing']}")
                    print(f"      Original: {example['original']}")
                    print(f"      DOCX: {example['docx']}")

    def save_detailed_report(self, output_path):
        """Save detailed JSON report"""
        report = {
            'stats': self.stats,
            'discrepancies': self.discrepancies
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Detailed report saved: {output_file}")

def main():
    import sys
    docx_dir = sys.argv[1] if len(sys.argv) > 1 else '.devkit/analysis/docx_verbs'

    validator = ComprehensiveValidator(docx_dir)
    validator.validate_all()
    validator.print_report()

    report_name = 'validation_report_v2.json' if 'v2' in docx_dir else 'validation_report.json'
    validator.save_detailed_report(f'.devkit/analysis/{report_name}')

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    if validator.discrepancies['missing_verbs']:
        print(f"\n1. Investigate {len(validator.discrepancies['missing_verbs'])} missing verbs")
        print("   - Check if they exist in DOCX source files")
        print("   - Update parser root detection if needed")

    if validator.discrepancies['translation_count_mismatch']:
        print(f"\n2. Fix translation extraction")
        print("   - Current loss rate detected")
        print("   - Improve quote detection and multi-line handling")

    if validator.discrepancies['etymology_mismatch']:
        print(f"\n3. Improve etymology parsing")
        print("   - Extract all structured fields")
        print("   - Match original parser's detail level")

    print("\n📋 Review detailed report: .devkit/analysis/validation_report.json")

if __name__ == '__main__':
    main()
