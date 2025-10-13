#!/usr/bin/env python3
"""
REGRESSION VALIDATOR
====================
Validates parser output against baseline to detect regressions.

This script:
- Compares current parser output with baseline
- Detects added, removed, and modified verbs
- Classifies changes as improvements, neutral, or regressions
- Generates detailed HTML diff report
- Returns exit code 0 (no regressions) or 1 (regressions found)

Usage:
    python3 parser/regression_validator.py           # Validate and generate report
    python3 parser/regression_validator.py --strict  # Fail on any changes
    python3 parser/regression_validator.py --json    # Output JSON summary only

Author: Claude Code
Created: 2025-10-13
"""

import json
import sys
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import difflib


class ChangeType:
    """Classification of changes"""
    IMPROVEMENT = 'improvement'
    NEUTRAL = 'neutral'
    REGRESSION = 'regression'
    ADDED = 'added'
    REMOVED = 'removed'


class RegressionValidator:
    """Validate parser output against baseline"""

    def __init__(self, verbs_dir='public/appdata/api/verbs', baseline_dir='data/baseline'):
        self.verbs_dir = Path(verbs_dir)
        self.baseline_dir = Path(baseline_dir)
        self.validation_dir = Path('data/validation')
        self.validation_dir.mkdir(parents=True, exist_ok=True)

        self.baseline = None
        self.current = {}
        self.changes = {
            'added': [],
            'removed': [],
            'modified': {
                ChangeType.IMPROVEMENT: [],
                ChangeType.NEUTRAL: [],
                ChangeType.REGRESSION: []
            },
            'unchanged': []
        }
        self.validation_errors = []

    def load_baseline(self):
        """Load baseline snapshot"""
        baseline_file = self.baseline_dir / 'baseline.json'
        if not baseline_file.exists():
            print("❌ No baseline found. Run: python3 parser/snapshot_baseline.py")
            sys.exit(1)

        with open(baseline_file, 'r', encoding='utf-8') as f:
            self.baseline = json.load(f)

        print(f"✅ Loaded baseline: {len(self.baseline['verbs'])} verbs")

    def compute_file_hash(self, filepath):
        """Compute SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            sha256.update(f.read())
        return sha256.hexdigest()

    def load_current(self):
        """Load current parser output"""
        print("🔄 Loading current parser output...")

        verb_files = sorted(self.verbs_dir.glob('*.json'))
        for filepath in verb_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    verb_data = json.load(f)

                root = verb_data['root']
                file_hash = self.compute_file_hash(filepath)

                self.current[root] = {
                    'filename': filepath.name,
                    'hash': file_hash,
                    'data': verb_data,
                    'filepath': filepath
                }
            except Exception as e:
                self.validation_errors.append(f"Error loading {filepath.name}: {e}")

        print(f"✅ Loaded current output: {len(self.current)} verbs")

    def detect_changes(self):
        """Detect added, removed, and modified verbs"""
        print("🔍 Detecting changes...")

        baseline_roots = set(self.baseline['verbs'].keys())
        current_roots = set(self.current.keys())

        # Added verbs
        added = current_roots - baseline_roots
        for root in sorted(added):
            self.changes['added'].append({
                'root': root,
                'data': self.current[root]['data']
            })

        # Removed verbs
        removed = baseline_roots - current_roots
        for root in sorted(removed):
            self.changes['removed'].append({
                'root': root,
                'baseline': self.baseline['verbs'][root]
            })

        # Modified verbs (compare hashes)
        common = baseline_roots & current_roots
        for root in sorted(common):
            baseline_hash = self.baseline['verbs'][root]['hash']
            current_hash = self.current[root]['hash']

            if baseline_hash != current_hash:
                # File changed - classify the change
                change_type = self.classify_change(
                    root,
                    self.baseline['verbs'][root],
                    self.current[root]['data']
                )
                self.changes['modified'][change_type].append({
                    'root': root,
                    'baseline': self.baseline['verbs'][root],
                    'current': self.current[root]['data'],
                    'details': self.get_change_details(
                        root,
                        self.baseline['verbs'][root],
                        self.current[root]['data']
                    )
                })
            else:
                self.changes['unchanged'].append(root)

        print(f"   • Added: {len(self.changes['added'])}")
        print(f"   • Removed: {len(self.changes['removed'])}")
        print(f"   • Modified (improvements): {len(self.changes['modified'][ChangeType.IMPROVEMENT])}")
        print(f"   • Modified (neutral): {len(self.changes['modified'][ChangeType.NEUTRAL])}")
        print(f"   • Modified (regressions): {len(self.changes['modified'][ChangeType.REGRESSION])}")
        print(f"   • Unchanged: {len(self.changes['unchanged'])}")

    def classify_change(self, root, baseline_entry, current_data):
        """Classify a change as improvement, neutral, or regression"""
        baseline_struct = baseline_entry['structure']
        current_struct = self.extract_structure(current_data)

        regression_indicators = []
        improvement_indicators = []
        neutral_indicators = []

        # Check stem count
        baseline_stems = baseline_struct['stem_count']
        current_stems = current_struct['stem_count']
        if current_stems < baseline_stems:
            regression_indicators.append(f"Lost stems: {baseline_stems} → {current_stems}")
        elif current_stems > baseline_stems:
            improvement_indicators.append(f"Added stems: {baseline_stems} → {current_stems}")

        # Check etymology
        baseline_etym = baseline_struct.get('has_etymology', False)
        current_etym = current_struct.get('has_etymology', False)
        if baseline_etym and not current_etym:
            regression_indicators.append("Lost etymology")
        elif not baseline_etym and current_etym:
            improvement_indicators.append("Added etymology")

        # Check examples per stem
        for i, baseline_stem in enumerate(baseline_struct.get('stems', [])):
            if i < len(current_struct.get('stems', [])):
                current_stem = current_struct['stems'][i]
                baseline_examples = baseline_stem['example_count']
                current_examples = current_stem['example_count']

                if current_examples < baseline_examples:
                    regression_indicators.append(
                        f"Stem {baseline_stem['stem']}: Lost examples ({baseline_examples} → {current_examples})"
                    )
                elif current_examples > baseline_examples:
                    improvement_indicators.append(
                        f"Stem {current_stem['stem']}: Added examples ({baseline_examples} → {current_examples})"
                    )

        # Check for HTML artifacts (regression)
        if self.has_html_artifacts(current_data):
            regression_indicators.append("Contains HTML artifacts")

        # Check conjugation types
        baseline_conj_types = set()
        current_conj_types = set()
        for stem in baseline_struct.get('stems', []):
            baseline_conj_types.update(stem['conjugation_types'])
        for stem in current_struct.get('stems', []):
            current_conj_types.update(stem['conjugation_types'])

        lost_conj = baseline_conj_types - current_conj_types
        added_conj = current_conj_types - baseline_conj_types
        if lost_conj:
            regression_indicators.append(f"Lost conjugations: {', '.join(sorted(lost_conj))}")
        if added_conj:
            improvement_indicators.append(f"Added conjugations: {', '.join(sorted(added_conj))}")

        # Classify
        if regression_indicators:
            return ChangeType.REGRESSION
        elif improvement_indicators:
            return ChangeType.IMPROVEMENT
        else:
            return ChangeType.NEUTRAL

    def extract_structure(self, verb_data):
        """Extract structural metadata from verb data"""
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

        return structure

    def get_change_details(self, root, baseline_entry, current_data):
        """Get detailed change information"""
        details = []

        baseline_struct = baseline_entry['structure']
        current_struct = self.extract_structure(current_data)

        # Stem changes
        if baseline_struct['stem_count'] != current_struct['stem_count']:
            details.append({
                'field': 'stem_count',
                'baseline': baseline_struct['stem_count'],
                'current': current_struct['stem_count']
            })

        # Etymology changes
        if baseline_struct['has_etymology'] != current_struct['has_etymology']:
            details.append({
                'field': 'etymology',
                'baseline': 'present' if baseline_struct['has_etymology'] else 'absent',
                'current': 'present' if current_struct['has_etymology'] else 'absent'
            })

        return details

    def has_html_artifacts(self, verb_data):
        """Check for HTML tags in text fields (indicates parsing error)"""
        # Check all text fields recursively
        def check_value(val):
            if isinstance(val, str):
                # Check for common HTML tags
                html_patterns = ['<p>', '<span>', '<font>', '<i>', '<b>', '&lt;', '&gt;', '&amp;']
                return any(pattern in val for pattern in html_patterns)
            elif isinstance(val, dict):
                return any(check_value(v) for v in val.values())
            elif isinstance(val, list):
                return any(check_value(item) for item in val)
            return False

        return check_value(verb_data)

    def run_validation_rules(self):
        """Run validation rules"""
        print("🔍 Running validation rules...")

        # Rule 1: Total verb count must not decrease
        baseline_count = len(self.baseline['verbs'])
        current_count = len(self.current)
        removed_count = len(self.changes['removed'])

        if current_count < baseline_count:
            self.validation_errors.append(
                f"REGRESSION: Total verb count decreased ({baseline_count} → {current_count})"
            )

        # Rule 2: Check for missing verbs (removals)
        if self.changes['removed']:
            self.validation_errors.append(
                f"REGRESSION: {removed_count} verbs removed from baseline"
            )

        # Rule 3: Check for data loss in modified verbs
        for change in self.changes['modified'][ChangeType.REGRESSION]:
            self.validation_errors.append(
                f"REGRESSION: {change['root']} - {', '.join(d['field'] for d in change['details'])}"
            )

        if self.validation_errors:
            print(f"   ❌ Found {len(self.validation_errors)} validation errors")
        else:
            print("   ✅ All validation rules passed")

    def generate_html_report(self):
        """Generate HTML diff report"""
        print("📝 Generating HTML report...")

        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html lang="en">')
        html.append('<head>')
        html.append('<meta charset="UTF-8">')
        html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append('<title>Parser Regression Report</title>')
        html.append('<style>')
        html.append('''
            body { font-family: system-ui, -apple-system, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #1a1a1a; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
            h2 { color: #333; margin-top: 30px; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }
            h3 { color: #555; margin-top: 20px; }
            .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .summary-card { background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }
            .summary-card.success { border-left-color: #28a745; }
            .summary-card.warning { border-left-color: #ffc107; }
            .summary-card.danger { border-left-color: #dc3545; }
            .summary-card .label { font-size: 12px; color: #666; text-transform: uppercase; }
            .summary-card .value { font-size: 24px; font-weight: bold; color: #1a1a1a; }
            .change-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #6c757d; }
            .change-item.improvement { border-left-color: #28a745; background: #f0f9f4; }
            .change-item.regression { border-left-color: #dc3545; background: #fef5f6; }
            .change-item.neutral { border-left-color: #17a2b8; background: #f0f8ff; }
            .change-item.added { border-left-color: #28a745; background: #f0f9f4; }
            .change-item.removed { border-left-color: #dc3545; background: #fef5f6; }
            .change-header { font-weight: bold; margin-bottom: 8px; }
            .change-details { font-size: 14px; color: #555; margin-left: 15px; }
            .change-details li { margin: 4px 0; }
            .badge { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
            .badge.improvement { background: #28a745; color: white; }
            .badge.regression { background: #dc3545; color: white; }
            .badge.neutral { background: #17a2b8; color: white; }
            .badge.added { background: #28a745; color: white; }
            .badge.removed { background: #dc3545; color: white; }
            .error-list { background: #fef5f6; padding: 15px; border-left: 4px solid #dc3545; border-radius: 6px; margin: 15px 0; }
            .error-list li { color: #721c24; margin: 5px 0; }
            .status-icon { font-size: 48px; text-align: center; margin: 20px 0; }
            .collapsible { cursor: pointer; padding: 10px; background: #e9ecef; border-radius: 4px; margin-top: 5px; }
            .collapsible:hover { background: #dee2e6; }
            .content { display: none; padding: 10px; background: white; border: 1px solid #e9ecef; border-radius: 4px; margin-top: 5px; }
            .content.active { display: block; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px; }
        ''')
        html.append('</style>')
        html.append('</head>')
        html.append('<body>')
        html.append('<div class="container">')

        # Header
        html.append('<h1>🧪 Parser Regression Report</h1>')
        html.append(f'<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')

        # Status
        has_regressions = bool(self.validation_errors or self.changes['removed'] or self.changes['modified'][ChangeType.REGRESSION])
        if has_regressions:
            html.append('<div class="status-icon">❌</div>')
            html.append('<h2 style="color: #dc3545; text-align: center;">REGRESSIONS DETECTED</h2>')
        else:
            html.append('<div class="status-icon">✅</div>')
            html.append('<h2 style="color: #28a745; text-align: center;">NO REGRESSIONS</h2>')

        # Summary
        html.append('<h2>Summary</h2>')
        html.append('<div class="summary">')
        html.append(f'<div class="summary-card success"><div class="label">Unchanged</div><div class="value">{len(self.changes["unchanged"])}</div></div>')
        html.append(f'<div class="summary-card success"><div class="label">Improvements</div><div class="value">{len(self.changes["modified"][ChangeType.IMPROVEMENT])}</div></div>')
        html.append(f'<div class="summary-card warning"><div class="label">Neutral Changes</div><div class="value">{len(self.changes["modified"][ChangeType.NEUTRAL])}</div></div>')
        html.append(f'<div class="summary-card danger"><div class="label">Regressions</div><div class="value">{len(self.changes["modified"][ChangeType.REGRESSION])}</div></div>')
        html.append(f'<div class="summary-card success"><div class="label">Added</div><div class="value">{len(self.changes["added"])}</div></div>')
        html.append(f'<div class="summary-card danger"><div class="label">Removed</div><div class="value">{len(self.changes["removed"])}</div></div>')
        html.append('</div>')

        # Validation Errors
        if self.validation_errors:
            html.append('<h2>Validation Errors</h2>')
            html.append('<div class="error-list"><ul>')
            for error in self.validation_errors:
                html.append(f'<li>{error}</li>')
            html.append('</ul></div>')

        # Regressions
        if self.changes['modified'][ChangeType.REGRESSION]:
            html.append('<h2>🔴 Regressions</h2>')
            for change in self.changes['modified'][ChangeType.REGRESSION]:
                html.append(f'<div class="change-item regression">')
                html.append(f'<div class="change-header"><span class="badge regression">Regression</span> {change["root"]}</div>')
                if change['details']:
                    html.append('<ul class="change-details">')
                    for detail in change['details']:
                        html.append(f'<li><strong>{detail["field"]}</strong>: {detail["baseline"]} → {detail["current"]}</li>')
                    html.append('</ul>')
                html.append('</div>')

        # Removed verbs
        if self.changes['removed']:
            html.append('<h2>🔴 Removed Verbs</h2>')
            for change in self.changes['removed']:
                html.append(f'<div class="change-item removed">')
                html.append(f'<div class="change-header"><span class="badge removed">Removed</span> {change["root"]}</div>')
                html.append('</div>')

        # Improvements
        if self.changes['modified'][ChangeType.IMPROVEMENT]:
            html.append('<h2>✅ Improvements</h2>')
            for change in self.changes['modified'][ChangeType.IMPROVEMENT]:
                html.append(f'<div class="change-item improvement">')
                html.append(f'<div class="change-header"><span class="badge improvement">Improvement</span> {change["root"]}</div>')
                if change['details']:
                    html.append('<ul class="change-details">')
                    for detail in change['details']:
                        html.append(f'<li><strong>{detail["field"]}</strong>: {detail["baseline"]} → {detail["current"]}</li>')
                    html.append('</ul>')
                html.append('</div>')

        # Added verbs
        if self.changes['added']:
            html.append('<h2>✅ Added Verbs</h2>')
            for change in self.changes['added']:
                html.append(f'<div class="change-item added">')
                html.append(f'<div class="change-header"><span class="badge added">Added</span> {change["root"]}</div>')
                html.append('</div>')

        # Neutral changes
        if self.changes['modified'][ChangeType.NEUTRAL]:
            html.append('<h2>ℹ️  Neutral Changes</h2>')
            html.append('<p>These changes are neither improvements nor regressions (e.g., formatting, whitespace).</p>')
            for change in self.changes['modified'][ChangeType.NEUTRAL]:
                html.append(f'<div class="change-item neutral">')
                html.append(f'<div class="change-header"><span class="badge neutral">Neutral</span> {change["root"]}</div>')
                html.append('</div>')

        html.append('</div>')
        html.append('<script>')
        html.append('''
            document.querySelectorAll('.collapsible').forEach(item => {
                item.addEventListener('click', () => {
                    const content = item.nextElementSibling;
                    content.classList.toggle('active');
                });
            });
        ''')
        html.append('</script>')
        html.append('</body>')
        html.append('</html>')

        report_file = self.validation_dir / 'regression_report.html'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))

        print(f"   ✅ Report saved to: {report_file}")
        return report_file

    def generate_json_summary(self):
        """Generate JSON summary for CI/CD"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'status': 'fail' if self.validation_errors else 'pass',
            'counts': {
                'unchanged': len(self.changes['unchanged']),
                'improvements': len(self.changes['modified'][ChangeType.IMPROVEMENT]),
                'neutral': len(self.changes['modified'][ChangeType.NEUTRAL]),
                'regressions': len(self.changes['modified'][ChangeType.REGRESSION]),
                'added': len(self.changes['added']),
                'removed': len(self.changes['removed'])
            },
            'validation_errors': self.validation_errors,
            'regressions': [c['root'] for c in self.changes['modified'][ChangeType.REGRESSION]],
            'removed': [c['root'] for c in self.changes['removed']],
            'improvements': [c['root'] for c in self.changes['modified'][ChangeType.IMPROVEMENT]],
            'added': [c['root'] for c in self.changes['added']]
        }

        json_file = self.validation_dir / 'regression_summary.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        return summary

    def validate(self, strict=False):
        """Run complete validation"""
        self.load_baseline()
        self.load_current()
        self.detect_changes()
        self.run_validation_rules()

        # Generate reports
        report_file = self.generate_html_report()
        summary = self.generate_json_summary()

        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        print(f"Report: {report_file}")
        print(f"Summary: {self.validation_dir / 'regression_summary.json'}")
        print()

        if self.validation_errors or self.changes['removed'] or self.changes['modified'][ChangeType.REGRESSION]:
            print("❌ REGRESSIONS DETECTED")
            print(f"   • Validation errors: {len(self.validation_errors)}")
            print(f"   • Removed verbs: {len(self.changes['removed'])}")
            print(f"   • Modified with regressions: {len(self.changes['modified'][ChangeType.REGRESSION])}")
            return 1
        elif strict and (self.changes['added'] or self.changes['modified'][ChangeType.NEUTRAL] or self.changes['modified'][ChangeType.IMPROVEMENT]):
            print("⚠️  CHANGES DETECTED (strict mode)")
            return 1
        else:
            print("✅ NO REGRESSIONS")
            if self.changes['added']:
                print(f"   • Added verbs: {len(self.changes['added'])}")
            if self.changes['modified'][ChangeType.IMPROVEMENT]:
                print(f"   • Improvements: {len(self.changes['modified'][ChangeType.IMPROVEMENT])}")
            return 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate parser output against baseline'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on any changes (not just regressions)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON summary to stdout'
    )
    args = parser.parse_args()

    validator = RegressionValidator()

    try:
        exit_code = validator.validate(strict=args.strict)

        if args.json:
            print(json.dumps(validator.generate_json_summary(), indent=2))

        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
