# Parser Validation Framework

**Automated regression testing system for the Turoyo Verb Glossary parser.**

This framework ensures that parser improvements never cause data loss or regressions by comparing new parser output against a known-good baseline.

---

## Quick Start

### 1. Create Initial Baseline

Before making any parser changes, snapshot the current "known good" output:

```bash
python3 parser/snapshot_baseline.py
```

This creates:
- `data/baseline/baseline.json` - Complete baseline snapshot with checksums
- `data/baseline/summary.json` - Quick summary statistics

### 2. Make Parser Changes

Edit `parser/parse_verbs.py` and make your improvements.

### 3. Run Parser with Validation

```bash
# Parse and validate in one step
python3 parser/parse_verbs.py --validate

# Or validate separately after parsing
python3 parser/parse_verbs.py
python3 parser/regression_validator.py
```

### 4. Review Results

Open the HTML report to see detailed changes:

```bash
open data/validation/regression_report.html
```

The report shows:
- ✅ **Improvements**: New data, fixed bugs, enhanced parsing
- ⚠️ **Neutral Changes**: Formatting, whitespace (no data impact)
- ❌ **Regressions**: Data loss, missing fields, parsing errors

### 5. Update Baseline (if changes are good)

Once you've verified the changes are improvements:

```bash
python3 parser/parse_verbs.py --update-baseline
```

Or update baseline separately:

```bash
python3 parser/snapshot_baseline.py
```

---

## What It Checks

### Validation Rules

The framework enforces these critical rules:

1. **Total verb count must not decrease**
   - Detects missing verbs
   - Ensures no data was accidentally dropped

2. **All baseline verbs must exist in new output**
   - Tracks removed verbs
   - Flags cross-reference resolution issues

3. **No verb should lose stems**
   - Counts stems per verb
   - Detects parsing failures for stem extraction

4. **No stem should lose conjugations**
   - Tracks conjugation types (Preterit, Infectum, etc.)
   - Ensures table extraction still works

5. **Text fields should not have HTML tags**
   - Checks for `<p>`, `<span>`, `<font>`, etc.
   - Detects failures in HTML cleaning

6. **Character encoding must be valid UTF-8**
   - Ensures special characters preserved: ʔʕġǧḥṣštṭḏṯẓāēīūə
   - Detects encoding corruption

7. **Etymology must be preserved**
   - Tracks etymology presence/absence
   - Ensures etymology parsing didn't break

8. **Examples must not be lost**
   - Counts examples per stem
   - Detects table parsing regressions

### Change Classification

Changes are automatically classified:

#### ✅ Improvements
- **New stems added** (e.g., missing stem IV now extracted)
- **More examples** (better table parsing)
- **Etymology added** (improved extraction)
- **Bug fixes** (HTML artifacts removed)

#### ⚠️ Neutral Changes
- **Whitespace normalization** (cosmetic only)
- **Formatting changes** (no semantic impact)
- **Comment updates** (metadata only)

#### ❌ Regressions
- **Stems lost** (parsing broke)
- **Examples removed** (table extraction failed)
- **Etymology disappeared** (parsing error)
- **HTML artifacts introduced** (cleaning broke)
- **Invalid characters** (encoding issue)

---

## Command Reference

### Baseline Management

```bash
# Create/update baseline
python3 parser/snapshot_baseline.py

# View baseline report
python3 parser/snapshot_baseline.py --report
```

### Validation

```bash
# Validate current output
python3 parser/regression_validator.py

# Strict mode (fail on ANY changes, not just regressions)
python3 parser/regression_validator.py --strict

# JSON output for CI/CD
python3 parser/regression_validator.py --json
```

### Integrated Parser Workflow

```bash
# Normal parsing
python3 parser/parse_verbs.py

# Parse + validate
python3 parser/parse_verbs.py --validate

# Parse + validate + update baseline
python3 parser/parse_verbs.py --validate --update-baseline
```

### Unit Tests

```bash
# Run all unit tests
python3 parser/test_parser.py

# Verbose output
python3 parser/test_parser.py -v

# Run specific test class
python3 parser/test_parser.py TestRootExtraction
```

---

## File Structure

```
turoyo-verb-glossary/
├── parser/
│   ├── parse_verbs.py              # Master parser (with --validate flag)
│   ├── snapshot_baseline.py        # Baseline snapshot generator
│   ├── regression_validator.py     # Regression detection engine
│   ├── test_parser.py              # Unit tests
│   └── test_fixtures/              # Test data (edge cases)
├── data/
│   ├── baseline/                   # Baseline snapshots
│   │   ├── baseline.json           # Complete baseline with checksums
│   │   └── summary.json            # Quick summary
│   └── validation/                 # Validation reports
│       ├── regression_report.html  # Visual diff report
│       └── regression_summary.json # JSON summary for CI/CD
└── public/appdata/api/verbs/       # Current parser output
```

---

## How It Works

### 1. Baseline Snapshot (`snapshot_baseline.py`)

**What it does:**
- Reads all 1,561 verb JSON files
- Computes SHA256 hash for each file
- Extracts structural metadata (stems, conjugations, etymology)
- Saves to `data/baseline/baseline.json`

**Metadata tracked:**
```json
{
  "root": "ʔmr 1",
  "filename": "ʔmr 1.json",
  "hash": "abc123...",
  "structure": {
    "stem_count": 3,
    "has_etymology": true,
    "stems": [
      {
        "stem": "I",
        "form_count": 2,
        "conjugation_types": ["Preterit", "Infectum", "Imperative"],
        "example_count": 45
      }
    ]
  }
}
```

### 2. Regression Validator (`regression_validator.py`)

**What it does:**
- Loads baseline snapshot
- Reads current parser output
- Compares file hashes (fast detection)
- For changed files:
  - Extracts current structure
  - Compares with baseline structure
  - Classifies change type
  - Generates detailed diff
- Produces HTML report + JSON summary

**Exit codes:**
- `0` = No regressions (safe to proceed)
- `1` = Regressions detected (review required)

### 3. Unit Tests (`test_parser.py`)

**What it tests:**
- Root extraction (including homonyms)
- Etymology parsing (MEA, Syr, etc.)
- Stem header detection (I, II, III, etc.)
- Token generation (italic marking, spacing)
- Conjugation extraction (tables)
- Edge cases (empty HTML, Unicode, malformed)

---

## Typical Workflows

### Adding New Parser Feature

```bash
# 1. Create baseline of current output
python3 parser/snapshot_baseline.py

# 2. Implement feature in parse_verbs.py
# ... edit code ...

# 3. Test your changes
python3 parser/test_parser.py

# 4. Run parser with validation
python3 parser/parse_verbs.py --validate

# 5. Review report
open data/validation/regression_report.html

# 6. If good, update baseline
python3 parser/snapshot_baseline.py
```

### Fixing Parser Bug

```bash
# 1. Ensure baseline exists (if not, create it)
python3 parser/snapshot_baseline.py --report

# 2. Fix bug in parse_verbs.py
# ... edit code ...

# 3. Validate fix
python3 parser/parse_verbs.py --validate

# 4. Should show improvements (bug fixes) but NO regressions
open data/validation/regression_report.html

# 5. Update baseline
python3 parser/parse_verbs.py --update-baseline
```

### Refactoring Parser Code

```bash
# 1. Create baseline
python3 parser/snapshot_baseline.py

# 2. Refactor code
# ... edit parse_verbs.py ...

# 3. Validate (should show ZERO changes if pure refactoring)
python3 parser/regression_validator.py

# 4. Exit code should be 0
echo $?

# 5. If output identical, no need to update baseline
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Parser Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install beautifulsoup4

      - name: Run unit tests
        run: python3 parser/test_parser.py

      - name: Parse HTML
        run: python3 parser/parse_verbs.py

      - name: Validate output
        run: python3 parser/regression_validator.py --json

      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: regression-report
          path: data/validation/regression_report.html
```

### Exit Codes

Use exit codes for automated decisions:

```bash
# Validate and check result
python3 parser/regression_validator.py
if [ $? -eq 0 ]; then
    echo "✅ Validation passed"
    # Deploy or commit changes
else
    echo "❌ Validation failed"
    exit 1
fi
```

---

## Best Practices

### DO:
✅ **Create baseline before making changes**
✅ **Run validation after every parser modification**
✅ **Review HTML report for unexpected changes**
✅ **Update baseline after verifying improvements**
✅ **Run unit tests to catch issues early**
✅ **Use `--validate` flag during development**

### DON'T:
❌ **Don't skip validation "just this once"**
❌ **Don't update baseline without reviewing report**
❌ **Don't ignore regressions in "unrelated" areas**
❌ **Don't commit changes without running tests**
❌ **Don't manually edit JSON files (fix parser instead)**

---

## Troubleshooting

### "No baseline found"

**Problem:** Running validator before creating baseline.

**Solution:**
```bash
python3 parser/snapshot_baseline.py
```

### "Validation failed" but report shows only improvements

**Problem:** Validator is overly cautious.

**Solution:** Check report carefully. If truly improvements, update baseline:
```bash
python3 parser/snapshot_baseline.py
```

### Parser changes but validation shows no changes

**Problem:**
1. Changes didn't affect output structure
2. Changes only affected internal logic

**Solution:** This is GOOD! Pure refactoring shouldn't change output.

### "HTML artifacts detected" error

**Problem:** Parser is leaving HTML tags in text fields.

**Solution:** Check `html_to_tokens()` and `parse_etymology()` for incomplete HTML cleaning.

### Test failures after parser changes

**Problem:** Tests expect old behavior.

**Solution:** Update tests to match new (correct) behavior. Ensure tests validate correctness, not legacy bugs.

---

## Adding New Tests

### Add Test Fixture

Create test data in `parser/test_fixtures/`:

```python
# test_fixtures/edge_case_1.html
'''
<p class="western"><span>ʔmr</span></p>
<!-- Your edge case HTML -->
'''
```

### Add Test Case

Edit `parser/test_parser.py`:

```python
class TestNewFeature(unittest.TestCase):
    """Test new parser feature"""

    def setUp(self):
        self.parser = TuroyoVerbParser.__new__(TuroyoVerbParser)

    def test_feature(self):
        """Test that feature works"""
        html = '<your test HTML>'
        result = self.parser.your_method(html)
        self.assertEqual(result, expected_value)
```

### Run Tests

```bash
python3 parser/test_parser.py -v
```

---

## Performance

### Baseline Snapshot
- **Time:** ~3-5 seconds for 1,561 files
- **Output:** ~2MB baseline.json

### Validation
- **Time:** ~5-10 seconds (includes hash comparison)
- **Output:** HTML report + JSON summary

### Full Pipeline with Validation
- **Time:** ~2-3 minutes total
  - Parse HTML: 60-90 seconds
  - Generate files: 10-20 seconds
  - Validate: 5-10 seconds

---

## Support

### Report Issues

If you encounter:
- False positive regressions
- Missing validation rules
- Performance issues
- Unclear error messages

Document the issue with:
1. Command run
2. Error message / unexpected behavior
3. Relevant excerpt from report
4. Expected vs actual result

### Extend Framework

To add new validation rules:

Edit `regression_validator.py`:

```python
def run_validation_rules(self):
    """Run validation rules"""
    # Add your rule
    if your_condition:
        self.validation_errors.append("REGRESSION: description")
```

To add new change classification logic:

Edit `classify_change()` in `regression_validator.py`:

```python
# Check for your specific change type
if your_condition:
    regression_indicators.append("Your regression description")
```

---

## Summary

The validation framework provides:

1. **Safety:** Catch regressions before they reach production
2. **Confidence:** Make parser changes without fear
3. **Documentation:** Visual reports show exactly what changed
4. **Speed:** Fast validation (seconds, not minutes)
5. **Automation:** Easy CI/CD integration

**Remember:** The framework is only as good as your baseline. Keep it updated and trust the validation!

---

**Last Updated:** 2025-10-13
**Framework Version:** 1.0
**Parser Version:** 4.0.0-master
