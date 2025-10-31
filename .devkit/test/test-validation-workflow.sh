#!/bin/bash
# Test script for enhanced validation workflow
# Demonstrates the three scenarios: no changes, safe changes, critical regressions

set -e

PROJECT_ROOT="/Users/evb/WebstormProjects/turoyo-verb-glossary"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "PARSER VALIDATION WORKFLOW TEST"
echo "=========================================="
echo

# Ensure baseline exists
if [ ! -f "data/baseline/baseline.json" ]; then
    echo "❌ No baseline found. Creating one first..."
    python3 parser/snapshot_baseline.py
    echo
fi

echo "Test Scenario 1: No Changes"
echo "-------------------------------------------"
echo "Running validation without any parser changes..."
python3 parser/regression_validator.py
EXIT_CODE=$?
echo "Exit code: $EXIT_CODE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: No regressions detected"
else
    echo "⚠️  Note: Some changes detected (expected if parser was modified)"
fi
echo

echo "Test Scenario 2: View Validation Report"
echo "-------------------------------------------"
if [ -f "data/validation/regression_report.html" ]; then
    echo "✅ HTML report generated"
    echo "   Location: data/validation/regression_report.html"
else
    echo "❌ No report found"
fi

if [ -f "data/validation/regression_summary.json" ]; then
    echo "✅ JSON summary generated"
    echo "   Contents:"
    python3 -c "import json; data=json.load(open('data/validation/regression_summary.json')); print(f\"   Status: {data['status']}\"); print(f\"   Unchanged: {data['counts']['unchanged']}\"); print(f\"   Improvements: {data['counts']['improvements']}\"); print(f\"   Neutral: {data['counts']['neutral']}\"); print(f\"   Regressions: {data['counts']['regressions']}\"); print(f\"   Added: {data['counts']['added']}\"); print(f\"   Removed: {data['counts']['removed']}\")"
else
    echo "❌ No summary found"
fi
echo

echo "Test Scenario 3: Check Baseline Info"
echo "-------------------------------------------"
python3 parser/snapshot_baseline.py --report
echo

echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo
echo "Next Steps:"
echo "1. To test safe changes:"
echo "   - Make a cosmetic parser change (add comment)"
echo "   - Run: python3 parser/parse_verbs.py --validate"
echo "   - Should prompt for baseline update"
echo
echo "2. To test critical regression:"
echo "   - Break parser (comment out stem extraction)"
echo "   - Run: python3 parser/parse_verbs.py --validate"
echo "   - Should error without prompting"
echo
echo "3. To view HTML report:"
echo "   - open data/validation/regression_report.html"
