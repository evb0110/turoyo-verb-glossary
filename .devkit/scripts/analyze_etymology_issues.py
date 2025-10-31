#!/usr/bin/env python3
"""Analyze the 49 remaining etymology issues"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_etymology_issues():
    """Extract and categorize etymology issues"""

    report_path = Path('.devkit/analysis/validation_report_v2.json')
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    issues = report.get('etymology_issues', [])
    print(f"\n📊 Total etymology issues: {len(issues)}")

    # Categorize issues
    categories = {
        'missing_in_docx': [],  # Type A
        'parsing_failed': [],    # Type B
        'missing_fields': [],    # Type C
        'structure_mismatch': [] # Type D
    }

    for issue in issues:
        root = issue['root']
        original_etym = issue.get('original_etymology')
        docx_etym = issue.get('docx_etymology')
        problem = issue.get('problem', '')

        # Type A: Missing in DOCX source (unrecoverable)
        if docx_etym is None:
            categories['missing_in_docx'].append(issue)

        # Type B: Present in DOCX but parser fails to extract
        elif original_etym and not docx_etym:
            categories['parsing_failed'].append(issue)

        # Type C: Extracted but missing specific fields
        elif docx_etym and original_etym:
            orig_etymons = original_etym.get('etymons', [])
            docx_etymons = docx_etym.get('etymons', [])

            if orig_etymons and docx_etymons:
                orig_first = orig_etymons[0]
                docx_first = docx_etymons[0]

                missing_fields = []
                for field in ['source', 'source_root', 'reference', 'meaning', 'notes']:
                    if field in orig_first and field not in docx_first:
                        missing_fields.append(field)

                if missing_fields:
                    issue['missing_fields'] = missing_fields
                    categories['missing_fields'].append(issue)
                else:
                    # Different structure
                    categories['structure_mismatch'].append(issue)
            else:
                categories['structure_mismatch'].append(issue)
        else:
            categories['structure_mismatch'].append(issue)

    # Print categorized summary
    print("\n" + "=" * 80)
    print("ETYMOLOGY ISSUES CATEGORIZED")
    print("=" * 80)

    for cat_name, cat_issues in categories.items():
        if cat_issues:
            print(f"\n{'=' * 80}")
            print(f"{cat_name.upper().replace('_', ' ')}: {len(cat_issues)} issues")
            print(f"{'=' * 80}")

            # Show first 10 examples from each category
            for i, issue in enumerate(cat_issues[:10], 1):
                print(f"\n{i}. ROOT: {issue['root']}")
                print(f"   Problem: {issue.get('problem', 'N/A')}")

                if issue.get('original_etymology'):
                    print(f"   ORIGINAL: {json.dumps(issue['original_etymology'], ensure_ascii=False)}")
                else:
                    print(f"   ORIGINAL: None")

                if issue.get('docx_etymology'):
                    print(f"   DOCX:     {json.dumps(issue['docx_etymology'], ensure_ascii=False)}")
                else:
                    print(f"   DOCX:     None")

                if issue.get('missing_fields'):
                    print(f"   MISSING FIELDS: {', '.join(issue['missing_fields'])}")

            if len(cat_issues) > 10:
                print(f"\n   ... and {len(cat_issues) - 10} more")

    # Save detailed analysis
    output = {
        'total_issues': len(issues),
        'categories': {
            'missing_in_docx': len(categories['missing_in_docx']),
            'parsing_failed': len(categories['parsing_failed']),
            'missing_fields': len(categories['missing_fields']),
            'structure_mismatch': len(categories['structure_mismatch'])
        },
        'detailed_issues': categories
    }

    output_path = Path('.devkit/analysis/etymology_issues_categorized.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n\n💾 Saved detailed analysis: {output_path}")

    return categories

if __name__ == '__main__':
    analyze_etymology_issues()
