#!/usr/bin/env python3
"""
Validation and Verification Tools for Turoyo Data
Generates reports for manual verification
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import random

class TuroyoValidator:
    def __init__(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.verbs = self.data['verbs']
        self.metadata = self.data['metadata']
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

    def validate_all(self):
        """Run all validation checks"""
        print("🔍 Validating extracted data...")

        self.check_completeness()
        self.check_data_quality()
        self.check_etymology()
        self.check_examples()
        self.check_references()
        self.detect_anomalies()

        self.print_report()
        self.generate_verification_samples()

    def check_completeness(self):
        """Check for missing or empty fields"""
        print("  Checking completeness...")

        for verb in self.verbs:
            if not verb.get('root'):
                self.issues['missing_root'].append(verb)

            if verb.get('cross_reference'):
                self.stats['cross_references'] += 1
                continue

            if not verb.get('etymology'):
                self.issues['missing_etymology'].append(verb['root'])
                self.stats['missing_etymology'] += 1

            if not verb.get('stems'):
                self.issues['no_stems'].append(verb['root'])
                self.stats['no_stems'] += 1
            else:
                for stem in verb['stems']:
                    if not stem.get('forms'):
                        self.issues['no_forms'].append(f"{verb['root']} - {stem['stem']}")

                    if not stem.get('conjugations'):
                        self.issues['no_conjugations'].append(f"{verb['root']} - {stem['stem']}")

    def check_data_quality(self):
        """Check quality of extracted data"""
        print("  Checking data quality...")

        for verb in self.verbs:
            for stem in verb.get('stems', []):
                for conj_type, examples in stem.get('conjugations', {}).items():
                    for example in examples:
                        if not example.get('turoyo'):
                            self.issues['empty_turoyo'].append(
                                f"{verb['root']} - {stem['stem']} - {conj_type}"
                            )

                        turoyo = example.get('turoyo', '')
                        if turoyo and len(turoyo.strip()) < 3:
                            self.issues['short_turoyo'].append(
                                f"{verb['root']}: '{turoyo}'"
                            )

                        if not example.get('translations'):
                            self.stats['no_translation'] += 1

                        if len(turoyo) > 1000:
                            self.issues['very_long_example'].append(
                                f"{verb['root']} - {len(turoyo)} chars"
                            )

    def check_etymology(self):
        """Analyze etymology data"""
        print("  Checking etymology...")

        sources = Counter()

        for verb in self.verbs:
            etym = verb.get('etymology')
            if etym:
                source = etym.get('source', 'unknown')
                sources[source] += 1

        self.stats['etymology_sources'] = dict(sources)

    def check_examples(self):
        """Analyze examples"""
        print("  Checking examples...")

        total_examples = 0
        examples_per_verb = []

        for verb in self.verbs:
            verb_examples = 0
            for stem in verb.get('stems', []):
                for conj_type, examples in stem.get('conjugations', {}).items():
                    verb_examples += len(examples)
                    total_examples += len(examples)

            examples_per_verb.append(verb_examples)

        self.stats['total_examples'] = total_examples
        self.stats['avg_examples_per_verb'] = total_examples / len(self.verbs) if self.verbs else 0
        self.stats['max_examples'] = max(examples_per_verb) if examples_per_verb else 0
        self.stats['min_examples'] = min(examples_per_verb) if examples_per_verb else 0

    def check_references(self):
        """Check reference patterns"""
        print("  Checking references...")

        ref_patterns = Counter()

        for verb in self.verbs:
            for stem in verb.get('stems', []):
                for conj_type, examples in stem.get('conjugations', {}).items():
                    for example in examples:
                        for ref in example.get('references', []):
                            if '/' in ref:
                                ref_patterns['page_reference'] += 1
                            elif ref.isupper():
                                ref_patterns['abbreviation'] += 1
                            elif ref.isdigit():
                                ref_patterns['number_only'] += 1
                            else:
                                ref_patterns['mixed'] += 1

        self.stats['reference_patterns'] = dict(ref_patterns)

    def detect_anomalies(self):
        """Detect potential parsing errors"""
        print("  Detecting anomalies...")

        for verb in self.verbs:
            if len(verb.get('stems', [])) > 8:
                self.issues['too_many_stems'].append(
                    f"{verb['root']}: {len(verb['stems'])} stems"
                )

            stems = [s['stem'] for s in verb.get('stems', [])]
            if len(stems) != len(set(stems)):
                self.issues['duplicate_stems'].append(verb['root'])

    def print_report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)

        print("\n📊 STATISTICS:")
        print(f"  Total verbs: {len(self.verbs)}")
        print(f"  Total stems: {sum(len(v.get('stems', [])) for v in self.verbs)}")
        print(f"  Total examples: {self.stats['total_examples']}")
        print(f"  Avg examples/verb: {self.stats['avg_examples_per_verb']:.1f}")
        print(f"  Cross-references: {self.stats['cross_references']}")
        print(f"  Uncertain entries (???): {sum(1 for v in self.verbs if v.get('uncertain'))}")

        print("\n📚 ETYMOLOGY SOURCES:")
        for source, count in sorted(self.stats['etymology_sources'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {source}: {count}")

        print("\n⚠️  POTENTIAL ISSUES:")
        issue_types = [
            ('missing_etymology', 'Missing etymology'),
            ('no_stems', 'No stems'),
            ('no_forms', 'No forms'),
            ('no_conjugations', 'No conjugations'),
            ('empty_turoyo', 'Empty Turoyo text'),
            ('short_turoyo', 'Suspiciously short Turoyo'),
            ('very_long_example', 'Very long examples'),
            ('too_many_stems', 'Too many stems'),
            ('duplicate_stems', 'Duplicate stems'),
        ]

        for issue_key, issue_name in issue_types:
            count = len(self.issues.get(issue_key, []))
            if count > 0:
                print(f"  {issue_name}: {count}")

        print("\n" + "="*70)

    def generate_verification_samples(self):
        """Generate random samples for manual verification"""
        output_dir = Path('data/verification')
        output_dir.mkdir(exist_ok=True)

        random_sample = random.sample(self.verbs, min(20, len(self.verbs)))
        with open(output_dir / 'random_sample.json', 'w', encoding='utf-8') as f:
            json.dump(random_sample, f, ensure_ascii=False, indent=2)

        verbs_with_counts = [
            (v, sum(len(examples) for stem in v.get('stems', [])
                    for examples in stem.get('conjugations', {}).values()))
            for v in self.verbs
        ]
        top_examples = sorted(verbs_with_counts, key=lambda x: -x[1])[:10]
        with open(output_dir / 'top_examples.json', 'w', encoding='utf-8') as f:
            json.dump([v[0] for v in top_examples], f, ensure_ascii=False, indent=2)

        verbs_by_stems = sorted(self.verbs, key=lambda v: -len(v.get('stems', [])))[:10]
        with open(output_dir / 'most_stems.json', 'w', encoding='utf-8') as f:
            json.dump(verbs_by_stems, f, ensure_ascii=False, indent=2)

        issues_sample = {
            'missing_etymology': self.issues.get('missing_etymology', [])[:10],
            'no_stems': self.issues.get('no_stems', [])[:10],
            'empty_turoyo': self.issues.get('empty_turoyo', [])[:10],
            'short_turoyo': self.issues.get('short_turoyo', [])[:10],
            'too_many_stems': self.issues.get('too_many_stems', [])[:10],
        }

        with open(output_dir / 'issues_sample.json', 'w', encoding='utf-8') as f:
            json.dump(issues_sample, f, ensure_ascii=False, indent=2)

        uncertain = [v for v in self.verbs if v.get('uncertain')]
        with open(output_dir / 'uncertain_entries.json', 'w', encoding='utf-8') as f:
            json.dump(uncertain, f, ensure_ascii=False, indent=2)

        print(f"\n📁 Verification samples saved to: {output_dir}/")
        print("  - random_sample.json (20 random verbs)")
        print("  - top_examples.json (10 verbs with most examples)")
        print("  - most_stems.json (10 verbs with most stems)")
        print("  - issues_sample.json (sample of potential issues)")
        print("  - uncertain_entries.json (all ??? marked entries)")

    def generate_html_report(self):
        """Generate an HTML report for easier manual review"""
        output_file = Path('data/verification/report.html')

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Turoyo Verb Glossary - Validation Report</title>
    <style>
        body {{ font-family: sans-serif; max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        h1 {{ color: #333; }}
        .stats {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .issue {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .success {{ background: #d4edda; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #333; color: white; }}
        .turoyo {{ font-size: 1.1em; color: #0056b3; }}
    </style>
</head>
<body>
    <h1>Turoyo Verb Glossary - Validation Report</h1>

    <div class="stats">
        <h2>Statistics</h2>
        <ul>
            <li>Total verbs: {len(self.verbs)}</li>
            <li>Total stems: {sum(len(v.get('stems', [])) for v in self.verbs)}</li>
            <li>Total examples: {self.stats['total_examples']}</li>
            <li>Average examples per verb: {self.stats['avg_examples_per_verb']:.1f}</li>
        </ul>
    </div>

    <h2>Sample Verbs</h2>
    <table>
        <tr>
            <th>Root</th>
            <th>Etymology</th>
            <th>Stems</th>
            <th>Examples</th>
        </tr>
"""

        for verb in self.verbs[:20]:
            etym = verb.get('etymology') or {}
            etym_str = f"{etym.get('source', 'N/A')}" if isinstance(etym, dict) else 'N/A'

            num_stems = len(verb.get('stems', []))
            num_examples = sum(len(examples) for stem in verb.get('stems', [])
                               for examples in stem.get('conjugations', {}).values())

            html += f"""
        <tr>
            <td class="turoyo">{verb['root']}</td>
            <td>{etym_str}</td>
            <td>{num_stems}</td>
            <td>{num_examples}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"  - report.html (HTML overview)")


def main():
        json_file = Path('.devkit/analysis/html_legacy/verbs.json')

    if not json_file.exists():
        print(f"❌ {json_file} not found. Run extract_final.py first.")
        return

    validator = TuroyoValidator(json_file)
    validator.validate_all()
    validator.generate_html_report()

if __name__ == '__main__':
    main()
