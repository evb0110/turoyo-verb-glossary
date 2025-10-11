#!/usr/bin/env python3
"""
Comprehensive validation of parsed data against source HTML
Finds lost or corrupted data through multiple validation strategies
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

class ExtractionValidator:
    def __init__(self, html_path, json_path):
        self.html_path = Path(html_path)
        self.json_path = Path(json_path)

        # Load source HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        # Load parsed data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.verbs = data['verbs']

        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

    def extract_html_section_for_root(self, root):
        """Extract HTML section for a specific root"""
        # Find the root header
        root_clean = root.replace(' ', r'\s*')
        pattern = f'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>{root_clean}</span>'

        match = re.search(pattern, self.html)
        if not match:
            return None

        start = match.start()

        # Find next root header
        next_pattern = r'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6}(?:\s*\d+)?</span>'
        next_match = re.search(next_pattern, self.html[match.end():])

        if next_match:
            end = match.end() + next_match.start()
        else:
            # Last verb in section
            end = start + 100000  # Safe upper bound

        return self.html[start:end]

    def extract_turoyo_text_from_html(self, html_section):
        """Extract all Turoyo text (italic) from HTML"""
        if not html_section:
            return []

        soup = BeautifulSoup(html_section, 'html.parser')
        turoyo_texts = []

        # Find all italic elements
        for italic in soup.find_all('i'):
            text = italic.get_text()
            # Skip pure references (numbers and punctuation)
            if text.strip() and not re.match(r'^[\d;/\s\[\]A-Z]+$', text.strip()):
                turoyo_texts.append(text.strip())

        return turoyo_texts

    def count_stems_in_html(self, html_section):
        """Count stem headers in HTML"""
        if not html_section:
            return 0

        # Count Stem headers (I, II, III, etc.)
        stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):'
        stems = len(re.findall(stem_pattern, html_section))

        # Count Detransitive
        detrans_patterns = [
            r'<font size="4" style="font-size: 16pt"><b><span[^>]*>Detransitive',
            r'<p[^>]*><span[^>]*>Detransitive</span></p>'
        ]
        for pattern in detrans_patterns:
            if re.search(pattern, html_section):
                stems += 1
                break

        return stems

    def count_tables_in_html(self, html_section):
        """Count tables in HTML"""
        if not html_section:
            return 0
        return len(re.findall(r'<table', html_section))

    def validate_verb(self, verb):
        """Validate a single verb entry"""
        root = verb['root']
        html_section = self.extract_html_section_for_root(root)

        if not html_section:
            self.issues[root].append({
                'type': 'missing_html',
                'severity': 'critical',
                'message': 'Could not find HTML section for root'
            })
            self.stats['missing_html'] += 1
            return

        # 1. Character count comparison
        html_turoyo_texts = self.extract_turoyo_text_from_html(html_section)
        html_char_count = sum(len(t) for t in html_turoyo_texts)

        json_char_count = 0
        for stem in verb['stems']:
            for conj_type, examples in stem['conjugations'].items():
                for ex in examples:
                    json_char_count += len(ex.get('turoyo', ''))

        char_diff_pct = abs(html_char_count - json_char_count) / html_char_count * 100 if html_char_count > 0 else 0

        if char_diff_pct > 20:  # More than 20% difference
            self.issues[root].append({
                'type': 'character_count_mismatch',
                'severity': 'high',
                'message': f'HTML has {html_char_count} chars, JSON has {json_char_count} chars ({char_diff_pct:.1f}% diff)',
                'html_chars': html_char_count,
                'json_chars': json_char_count
            })
            self.stats['char_mismatch'] += 1

        # 2. Stem count validation
        html_stem_count = self.count_stems_in_html(html_section)
        json_stem_count = len(verb['stems'])

        if html_stem_count != json_stem_count:
            self.issues[root].append({
                'type': 'stem_count_mismatch',
                'severity': 'high',
                'message': f'HTML has {html_stem_count} stems, JSON has {json_stem_count} stems',
                'html_stems': html_stem_count,
                'json_stems': json_stem_count
            })
            self.stats['stem_mismatch'] += 1

        # 3. Check for empty conjugations
        empty_stems = []
        for stem in verb['stems']:
            if not stem['conjugations']:
                empty_stems.append(stem['stem'])

        if empty_stems:
            self.issues[root].append({
                'type': 'empty_conjugations',
                'severity': 'high',
                'message': f'Stems with no conjugations: {", ".join(empty_stems)}',
                'empty_stems': empty_stems
            })
            self.stats['empty_conjugations'] += 1

        # 4. Table count comparison
        html_table_count = self.count_tables_in_html(html_section)
        json_table_count = sum(len(stem['conjugations']) for stem in verb['stems'])

        if html_table_count > json_table_count + 2:  # Allow some tolerance
            self.issues[root].append({
                'type': 'table_count_mismatch',
                'severity': 'medium',
                'message': f'HTML has {html_table_count} tables, JSON has {json_table_count} conjugation types',
                'html_tables': html_table_count,
                'json_tables': json_table_count
            })
            self.stats['table_mismatch'] += 1

        # 5. Check for suspicious patterns in Turoyo text
        for stem in verb['stems']:
            for conj_type, examples in stem['conjugations'].items():
                for ex in examples:
                    turoyo = ex.get('turoyo', '')

                    # Check for excessive spaces (might indicate word boundary issues)
                    if re.search(r'\s{2,}', turoyo):
                        self.issues[root].append({
                            'type': 'excessive_spaces',
                            'severity': 'low',
                            'message': f'Multiple spaces in {stem["stem"]} {conj_type}',
                            'text': turoyo[:100]
                        })
                        self.stats['excessive_spaces'] += 1
                        break

    def validate_all(self):
        """Validate all verbs"""
        print("🔍 Validating all parsed verbs against source HTML...")
        print(f"   Total verbs to validate: {len(self.verbs)}")

        for i, verb in enumerate(self.verbs, 1):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(self.verbs)}...", end='\r')

            self.validate_verb(verb)

        print(f"\n✅ Validation complete!")
        return self.issues, self.stats

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*80)
        print("VALIDATION REPORT")
        print("="*80)

        print(f"\n📊 Statistics:")
        print(f"   Total verbs checked: {len(self.verbs)}")
        print(f"   Verbs with issues: {len(self.issues)}")
        print(f"   Missing HTML sections: {self.stats['missing_html']}")
        print(f"   Character count mismatches: {self.stats['char_mismatch']}")
        print(f"   Stem count mismatches: {self.stats['stem_mismatch']}")
        print(f"   Empty conjugations: {self.stats['empty_conjugations']}")
        print(f"   Table count mismatches: {self.stats['table_mismatch']}")
        print(f"   Excessive spaces: {self.stats['excessive_spaces']}")

        # Sort issues by severity
        critical_issues = []
        high_issues = []
        medium_issues = []
        low_issues = []

        for root, issues_list in self.issues.items():
            for issue in issues_list:
                severity = issue['severity']
                if severity == 'critical':
                    critical_issues.append((root, issue))
                elif severity == 'high':
                    high_issues.append((root, issue))
                elif severity == 'medium':
                    medium_issues.append((root, issue))
                else:
                    low_issues.append((root, issue))

        # Print critical issues
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
            for root, issue in critical_issues[:20]:  # Show first 20
                print(f"   {root}: {issue['message']}")

        # Print high-severity issues
        if high_issues:
            print(f"\n⚠️  HIGH SEVERITY ({len(high_issues)}):")
            for root, issue in high_issues[:20]:  # Show first 20
                print(f"   {root}: {issue['message']}")

        # Print medium-severity issues
        if medium_issues:
            print(f"\n⚡ MEDIUM SEVERITY ({len(medium_issues)}):")
            print(f"   (Showing first 10 of {len(medium_issues)})")
            for root, issue in medium_issues[:10]:
                print(f"   {root}: {issue['message']}")

        # Save detailed report
        report_file = Path('parser/validation_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': dict(self.stats),
                'issues': {k: v for k, v in self.issues.items()},
                'critical_count': len(critical_issues),
                'high_count': len(high_issues),
                'medium_count': len(medium_issues),
                'low_count': len(low_issues)
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Detailed report saved to: {report_file}")

        # Return most problematic verbs for manual inspection
        problematic_verbs = []
        for root, issues_list in self.issues.items():
            severity_score = sum(
                10 if i['severity'] == 'critical' else
                5 if i['severity'] == 'high' else
                2 if i['severity'] == 'medium' else 1
                for i in issues_list
            )
            if severity_score >= 5:
                problematic_verbs.append((root, severity_score, issues_list))

        problematic_verbs.sort(key=lambda x: x[1], reverse=True)

        print(f"\n🎯 TOP 20 VERBS FOR MANUAL INSPECTION:")
        for root, score, issues_list in problematic_verbs[:20]:
            print(f"   {root} (score: {score})")
            for issue in issues_list:
                print(f"      - {issue['message']}")

        return problematic_verbs

def main():
    validator = ExtractionValidator(
        'source/Turoyo_all_2024.html',
        'data/verbs_final.json'
    )

    validator.validate_all()
    problematic_verbs = validator.generate_report()

    print(f"\n✅ Validation complete. Found {len(validator.issues)} verbs with potential issues.")

if __name__ == '__main__':
    main()
