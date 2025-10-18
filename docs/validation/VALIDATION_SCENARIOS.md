# Parser Validation Scenarios

This guide demonstrates the enhanced validation workflow with real-world examples.

## Table of Contents

1. [Scenario 1: No Changes](#scenario-1-no-changes)
2. [Scenario 2: Safe Changes (False Positives)](#scenario-2-safe-changes-false-positives)
3. [Scenario 3: Critical Regressions](#scenario-3-critical-regressions)
4. [Scenario 4: Improvements](#scenario-4-improvements)
5. [Scenario 5: CI/CD Mode](#scenario-5-cicd-mode)

---

## Scenario 1: No Changes

**Situation:** Run validation without modifying the parser.

### Command

```bash
python3 parser/parse_verbs.py --validate
```

### Expected Output

```
================================================================================
TUROYO VERB GLOSSARY - MASTER PARSER
================================================================================
🔄 Parsing Turoyo verb data...
  [46/46] ə...
✅ Parsed 1518 verbs, 3199 stems
🔍 Checking for homonyms with different etymologies...
✅ PARSING COMPLETE!
📚 Total verbs: 1518
📖 Total stems: 3199
🔗 Cross-references: 178
❓ Uncertain entries: 0
🔢 Homonyms numbered: 0
================================================================================

================================================================================
VALIDATING AGAINST BASELINE
================================================================================
✅ Loaded baseline: 1518 verbs
🔄 Loading current parser output...
✅ Loaded current output: 1518 verbs
🔍 Detecting changes...
   • Added: 0
   • Removed: 0
   • Modified (improvements): 0
   • Modified (neutral): 0
   • Modified (regressions): 0
   • Unchanged: 1518
🔍 Running validation rules...
   ✅ All validation rules passed

================================================================================
VALIDATION RESULTS
================================================================================
Report: data/validation/regression_report.html
Summary: data/validation/regression_summary.json

✅ NO REGRESSIONS
```

### Exit Code

`0` (Success)

### Next Steps

Continue working - parser is stable.

---

## Scenario 2: Safe Changes (False Positives)

**Situation:** Made cosmetic changes that don't affect data (formatting, comments, whitespace).

### Example Change

```python
# In parse_verbs.py, add a comment or reformat code
def parse_stems(self, entry_html):
    """Find all stem headers"""
    stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font>'

    stems = []
    for match in re.finditer(stem_pattern, entry_html):
        # Extract stem information
        stem_num = match.group(1)
        forms_text = match.group(2).strip()
        forms = [f.strip() for f in forms_text.split('/') if f.strip()]
        ...
```

### Command

```bash
python3 parser/parse_verbs.py --validate
```

### Expected Output

```
================================================================================
VALIDATING AGAINST BASELINE
================================================================================
✅ Loaded baseline: 1518 verbs
🔄 Loading current parser output...
✅ Loaded current output: 1518 verbs
🔍 Detecting changes...
   • Added: 0
   • Removed: 0
   • Modified (improvements): 0
   • Modified (neutral): 18
   • Modified (regressions): 0
   • Unchanged: 1500
🔍 Running validation rules...
   ✅ All validation rules passed

================================================================================
VALIDATION RESULTS
================================================================================
Report: data/validation/regression_report.html
Summary: data/validation/regression_summary.json

⚠️  Neutral changes detected - analyzing...

✅ Found 18 safe changes (false positives):
   • frq: only hash differs (likely formatting/whitespace)
   • kfr: only hash differs (likely formatting/whitespace)
   • mbr: only hash differs (likely formatting/whitespace)
   • qbl: only hash differs (likely formatting/whitespace)
   • šql: only hash differs (likely formatting/whitespace)
   ... and 13 more

These changes don't affect data integrity:
   ✅ All stems present
   ✅ All examples preserved
   ✅ Etymology intact
   ✅ Conjugations unchanged

Update baseline to clear these warnings? (y/n): y

🔄 Updating baseline...
📸 Generating baseline snapshot...
   Reading from: server/assets/verbs
   ✅ Processed 1518 verb files

💾 Baseline saved to: data/baseline/baseline.json
   📊 Summary:
      • Total verbs: 1518
      • Total stems: 3199
      • Total examples: 4685
      • Homonyms: 0
      • Cross-references: 178
      • Uncertain entries: 0
✅ Baseline updated successfully

✅ Baseline updated successfully
✅ Validation will pass on next run
```

### Exit Code

`0` (Success - user accepted update)

### If User Declines

```
Update baseline to clear these warnings? (y/n): n

⚠️  Baseline not updated - warnings will persist
```

**Exit Code:** `1` (Warning persists)

---

## Scenario 3: Critical Regressions

**Situation:** Parser change breaks data extraction (loses stems, examples, or etymology).

### Example Breaking Change

```python
# Accidentally comment out stem extraction
def parse_stems(self, entry_html):
    """Find all stem headers"""
    # stem_pattern = r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font>'
    return []  # BUG: Returns empty list!
```

### Command

```bash
python3 parser/parse_verbs.py --validate
```

### Expected Output

```
================================================================================
VALIDATING AGAINST BASELINE
================================================================================
✅ Loaded baseline: 1518 verbs
🔄 Loading current parser output...
✅ Loaded current output: 1518 verbs
🔍 Detecting changes...
   • Added: 0
   • Removed: 0
   • Modified (improvements): 0
   • Modified (neutral): 0
   • Modified (regressions): 1518
   • Unchanged: 0
🔍 Running validation rules...
   ❌ Found 1518 validation errors

================================================================================
VALIDATION RESULTS
================================================================================
Report: data/validation/regression_report.html
Summary: data/validation/regression_summary.json

❌ CRITICAL REGRESSIONS DETECTED

Validation Errors:
   • REGRESSION: ʔbl - stem_count
   • REGRESSION: ʔbš - stem_count
   • REGRESSION: ʔbz - stem_count
   • REGRESSION: ʔby - stem_count
   • REGRESSION: ʔdm - stem_count
   • REGRESSION: ʔdš - stem_count
   • REGRESSION: ʔhd - stem_count
   • REGRESSION: ʔhr - stem_count
   • REGRESSION: ʔkl - stem_count
   • REGRESSION: ʔlf - stem_count
   ... and 1508 more

Regression Changes (1518):
   • ʔbl: Lost stems: 2 → 0
   • ʔbš: Lost stems: 2 → 0
   • ʔbz: Lost stems: 2 → 0
   • ʔby: Lost stems: 3 → 0
   • ʔdm: Lost stems: 2 → 0
   • ʔdš: Lost stems: 2 → 0
   • ʔhr: Lost stems: 4 → 0
   • ʔkl: Lost stems: 2 → 0
   • ʔlf: Lost stems: 4 → 0
   • ʔmr: Lost stems: 4 → 0
   ... and 1508 more

❌ DO NOT update baseline! Fix parser first.
```

### Exit Code

`1` (Critical failure)

### Next Steps

1. Revert breaking change
2. Fix the bug properly
3. Re-run validation
4. Only update baseline when validation passes

---

## Scenario 4: Improvements

**Situation:** Enhanced parser extracts more data (new stems, examples, or etymology).

### Example Improvement

```python
# Added better stem extraction for edge cases
def parse_stems(self, entry_html):
    """Find all stem headers"""
    # ... original patterns ...

    # NEW: Better fallback pattern for rare cases
    fallback_pattern = r'<p[^>]*>.*?<span[^>]*>([IVX]+):</span>.*?</p>'
    for match in re.finditer(fallback_pattern, entry_html):
        # ... extract stem info ...
```

### Expected Output

```
================================================================================
VALIDATION RESULTS
================================================================================
Report: data/validation/regression_report.html
Summary: data/validation/regression_summary.json

✅ NO REGRESSIONS
   • Added verbs: 0
   • Improvements: 5

Improvements detected:
   • frq: Added 1 stem
   • kfr: Added 2 examples to Stem I
   • qbl: Added etymology
   • šql: Added conjugations (Imperative)
   • mbr: Added 1 stem
```

### Exit Code

`0` (Success - improvements are good!)

### Next Steps

1. Review improvements in HTML report
2. Update baseline if satisfied: `python3 parser/snapshot_baseline.py`
3. Consider documenting the improvement

---

## Scenario 5: CI/CD Mode

**Situation:** Running validation in automated pipeline (GitHub Actions, Jenkins, etc.).

### Environment

```yaml
# GitHub Actions example
env:
  CI: true
```

### Command

```bash
python3 parser/parse_verbs.py --validate
```

### Behavior with Safe Changes

```
================================================================================
VALIDATION RESULTS
================================================================================
Report: data/validation/regression_report.html
Summary: data/validation/regression_summary.json

⚠️  Neutral changes detected - analyzing...

✅ Found 18 safe changes (false positives):
   • frq: only hash differs (likely formatting/whitespace)
   ... and 17 more

These changes don't affect data integrity:
   ✅ All stems present
   ✅ All examples preserved
   ✅ Etymology intact
   ✅ Conjugations unchanged

⚠️  Running in non-interactive mode - skipping baseline update
⚠️  Run manually: python3 parser/snapshot_baseline.py
```

### Exit Code

`1` (Requires manual intervention)

### CI/CD Workflow

1. Validation fails with safe changes
2. Developer reviews changes locally
3. If satisfied, updates baseline manually
4. Commits updated baseline
5. CI passes on next run

---

## Quick Reference

| Scenario                   | Prompts? | Exit Code | Action                     |
| -------------------------- | -------- | --------- | -------------------------- |
| No changes                 | No       | 0         | Continue                   |
| Safe changes (interactive) | Yes      | 0 or 1    | User decides               |
| Safe changes (CI/CD)       | No       | 1         | Manual update needed       |
| Critical regressions       | No       | 1         | Fix parser                 |
| Improvements               | No       | 0         | Optionally update baseline |
| Unsafe neutral changes     | No       | 1         | Investigate                |

---

## Debugging Tips

### View Detailed Changes

```bash
open data/validation/regression_report.html
```

### Check JSON Summary

```bash
cat data/validation/regression_summary.json | python3 -m json.tool
```

### Compare Specific Verb

```bash
# Baseline
cat data/baseline/baseline.json | jq '.verbs["frq"]'

# Current
cat server/assets/verbs/frq.json
```

### Force Baseline Update (Skip Validation)

```bash
# WARNING: Only do this if you're sure!
python3 parser/snapshot_baseline.py
```

---

## Best Practices

1. **Always validate before committing** - Run `--validate` flag
2. **Review HTML report** - Check what changed visually
3. **Understand safe changes** - Know why hash differs
4. **Never force through regressions** - Fix parser instead
5. **Document improvements** - Note what was enhanced
6. **Update baseline consciously** - Don't auto-accept blindly
7. **Test in CI/CD** - Ensure validation runs in pipeline

---

## See Also

- [START_HERE.md](START_HERE.md) - Quick start guide
- [VALIDATION_QUICKSTART.md](VALIDATION_QUICKSTART.md) - One-page reference
- [README.md](README.md) - Full documentation
