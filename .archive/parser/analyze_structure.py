#!/usr/bin/env python3
"""
Turoyo HTML Structure Analyzer
Identifies all patterns, inconsistencies, and edge cases before parsing
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
import json

class TuroyoAnalyzer:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        with open(html_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

        self.issues = defaultdict(list)
        self.stats = {}

    def analyze_all(self):
        """Run all analysis methods"""
        print("🔍 Analyzing Turoyo HTML structure...\n")

        self.analyze_roots()
        self.analyze_binyanim()
        self.analyze_table_headers()
        self.analyze_etymology()
        self.analyze_cross_references()
        self.analyze_tables_structure()
        self.analyze_edge_cases()

        self.print_report()
        self.save_report()

    def analyze_roots(self):
        """Find all root entries"""
        # Pattern: root followed by etymology in parentheses
        pattern = r'<p lang="en-GB" class="western"><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)</span></font><font[^>]*><font[^>]*><i><span[^>]*>\s*\([^)]*\)'
        roots = re.findall(pattern, self.content)

        # Also find simple roots (without immediate etymology)
        simple_roots = re.findall(
            r'<p lang="en-GB" class="western"><font[^>]*><span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]{2,6})</span>',
            self.content
        )

        self.stats['roots_with_etym'] = len(roots)
        self.stats['total_potential_roots'] = len(set(simple_roots))
        self.stats['root_list'] = sorted(set(simple_roots))[:50]  # First 50

        # Check for roots with numbers (variants)
        numbered_roots = [r for r in simple_roots if any(c.isdigit() for c in r)]
        self.stats['numbered_roots'] = numbered_roots

    def analyze_binyanim(self):
        """Find all binyan markers and patterns"""
        # Pattern: I:, II:, III:, etc.
        binyan_pattern = r'<font size="4" style="font-size: (\d+)pt"><b><span[^>]*>(.*?):</span>'
        binyanim = re.findall(binyan_pattern, self.content)

        binyan_types = Counter([b[1] for b in binyanim])
        self.stats['binyan_types'] = dict(binyan_types)

        # Check for inconsistencies in font sizes
        binyan_fonts = Counter([b[0] for b in binyanim])
        self.stats['binyan_font_sizes'] = dict(binyan_fonts)

        # Find "Detransitive" markers
        detrans = re.findall(
            r'<p[^>]*><span[^>]*>(\(Detrans\.\)|Detransitive)</span>',
            self.content
        )
        self.stats['detransitive_markers'] = len(detrans)

    def analyze_table_headers(self):
        """Analyze all table header variations"""
        # Extract first column of tables (headers)
        header_pattern = r'<td width="154"[^>]*><p[^>]*>\s*<span[^>]*>([^<]+)</span></p>'
        headers = re.findall(header_pattern, self.content)

        header_counts = Counter(headers)
        self.stats['table_headers'] = dict(header_counts)

        # Find problematic headers
        issues = []

        # Multiple spaces
        multi_space = [h for h in headers if '  ' in h or h.startswith(' ')]
        if multi_space:
            issues.append(f"Headers with extra spaces: {len(set(multi_space))}")

        # Different dash types
        infectum_wa_variants = [h for h in headers if 'Infectum' in h and 'wa' in h]
        if len(set(infectum_wa_variants)) > 1:
            issues.append(f"Infectum-wa variants: {set(infectum_wa_variants)}")

        # Case inconsistencies
        part_variants = [h for h in headers if 'Part' in h]
        if len(set(part_variants)) > 5:
            issues.append(f"Participle header variants: {len(set(part_variants))}")

        self.issues['table_headers'] = issues

    def analyze_etymology(self):
        """Analyze etymology patterns"""
        # Pattern: (< SOURCE root cf. REF: meaning)
        etym_pattern = r'\(&lt;\s*([^)]+?)\s+([^\s]+)\s+cf\.\s+([^:]+):\s*([^)]+)\)'
        etymologies = re.findall(etym_pattern, self.content)

        sources = Counter([e[0] for e in etymologies])
        self.stats['etymology_sources'] = dict(sources.most_common(10))

        # Check for malformed etymologies
        malformed = re.findall(r'\([^)]{0,5}&lt;[^)]{200,}\)', self.content)
        if malformed:
            self.issues['etymology'].append(f"Very long etymologies: {len(malformed)}")

    def analyze_cross_references(self):
        """Find all cross-references (root redirects)"""
        xref_pattern = r'<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)\s*→\s*([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə]+)</span>'
        xrefs = re.findall(xref_pattern, self.content)

        self.stats['cross_references'] = len(xrefs)
        self.stats['xref_list'] = xrefs[:20]

    def analyze_tables_structure(self):
        """Analyze table structures"""
        # Count tables
        tables = re.findall(r'<table[^>]*>', self.content)
        self.stats['total_tables'] = len(tables)

        # Check for tables with different column widths
        col_widths = re.findall(r'<col width="(\d+)"/>', self.content)
        width_combos = []
        for i in range(0, len(col_widths), 2):
            if i+1 < len(col_widths):
                width_combos.append(f"{col_widths[i]}+{col_widths[i+1]}")

        width_counter = Counter(width_combos)
        self.stats['table_column_widths'] = dict(width_counter.most_common(5))

        # Check for single-column tables
        if '0+0' in str(width_counter) or len(width_counter) > 3:
            self.issues['tables'].append("Non-standard table widths detected")

    def analyze_edge_cases(self):
        """Find specific edge cases"""
        # Find entries with question marks (uncertain data)
        uncertain = re.findall(r'<span[^>]*>[^<]*\?\?\?[^<]*</span>', self.content)
        self.stats['uncertain_entries'] = len(uncertain)

        # Find very long table cells (might indicate parsing issues)
        long_cells = re.findall(r'<td[^>]*><p[^>]*>(.{2000,}?)</p>', self.content)
        self.stats['very_long_cells'] = len(long_cells)

        # Check for nested tables
        nested_tables = re.findall(r'<table[^>]*>.*?<table', self.content, re.DOTALL)
        if nested_tables:
            self.issues['tables'].append(f"Possible nested tables: {len(nested_tables)}")

        # Find footnotes
        footnotes = re.findall(r'class="sdfootnote', self.content)
        self.stats['footnotes'] = len(footnotes)

    def print_report(self):
        """Print analysis report"""
        print("=" * 70)
        print("TUROYO HTML STRUCTURE ANALYSIS REPORT")
        print("=" * 70)

        print("\n📊 STATISTICS:")
        print(f"  Total potential roots: {self.stats.get('total_potential_roots', 0)}")
        print(f"  Roots with etymology: {self.stats.get('roots_with_etym', 0)}")
        print(f"  Cross-references: {self.stats.get('cross_references', 0)}")
        print(f"  Total tables: {self.stats.get('total_tables', 0)}")
        print(f"  Footnotes: {self.stats.get('footnotes', 0)}")
        print(f"  Uncertain entries (???): {self.stats.get('uncertain_entries', 0)}")

        print("\n📚 BINYAN DISTRIBUTION:")
        for binyan, count in sorted(self.stats.get('binyan_types', {}).items()):
            print(f"  {binyan}: {count}")

        print("\n📋 TABLE HEADERS (top 15):")
        headers = self.stats.get('table_headers', {})
        for header, count in sorted(headers.items(), key=lambda x: -x[1])[:15]:
            print(f"  {count:4d}x  {header!r}")

        print("\n🔗 ETYMOLOGY SOURCES:")
        for source, count in list(self.stats.get('etymology_sources', {}).items())[:10]:
            print(f"  {count:3d}x  {source}")

        print("\n⚠️  ISSUES DETECTED:")
        if not any(self.issues.values()):
            print("  ✅ No major issues detected")
        else:
            for category, issues in self.issues.items():
                print(f"\n  {category.upper()}:")
                for issue in issues:
                    print(f"    - {issue}")

        print("\n💡 RECOMMENDATIONS:")
        print("  1. Normalize table headers (Part.Pass → Part. Pass.)")
        print("  2. Standardize Infectum-wa dash types")
        print("  3. Trim extra spaces from headers")
        print("  4. Handle cross-references as separate entries")
        print("  5. Mark uncertain entries (???) in output JSON")

        print("\n" + "=" * 70)

    def save_report(self):
        """Save detailed report to JSON"""
        output = {
            'stats': self.stats,
            'issues': dict(self.issues),
            'recommendations': [
                'Normalize table headers',
                'Standardize dash types',
                'Trim whitespace',
                'Handle cross-references',
                'Mark uncertain data'
            ]
        }

        report_path = Path(self.html_path).parent.parent / 'parser' / 'analysis_report.json'
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Detailed report saved to: {report_path}")


if __name__ == '__main__':
    html_file = Path(__file__).parent.parent / 'source' / 'Turoyo_all_2024.html'

    analyzer = TuroyoAnalyzer(html_file)
    analyzer.analyze_all()
