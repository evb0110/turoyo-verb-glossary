#!/usr/bin/env python3
"""Run validation with the NEW parser output (docx_v2_verbs)"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_validation import ComprehensiveValidator

print("=" * 80)
print("RUNNING VALIDATION WITH NEW PARSER OUTPUT")
print("=" * 80)

validator = ComprehensiveValidator(docx_dir='.devkit/analysis/docx_v2_verbs')
validator.validate_all()
validator.save_detailed_report('.devkit/analysis/validation_report_v3.json')

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
print(f"Report saved: .devkit/analysis/validation_report_v3.json")
