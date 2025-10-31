# Parser Validation Enhancement

## Overview

Enhanced the parser validation workflow to intelligently handle regressions by distinguishing between:

- **Critical regressions** (data loss, missing stems, corrupted content) - blocks baseline update
- **Safe changes** (formatting, whitespace, hash differences) - prompts for baseline update
- **Unsafe neutral changes** (unexpected modifications) - requires investigation

## Key Features

### 1. Regression Analysis

The validator now includes `is_safe_change()` function that checks:

- ✅ Stem count unchanged
- ✅ Etymology presence unchanged
- ✅ Cross-reference status unchanged
- ✅ All stem names present
- ✅ Form counts unchanged
- ✅ Example counts unchanged
- ✅ Conjugation types unchanged

If all structural data is identical but hash differs, the change is considered "safe" (likely formatting/whitespace).

### 2. Interactive Baseline Updates

When only safe changes are detected:

```
⚠️  Neutral changes detected - analyzing...

✅ Found 18 safe changes (false positives):
   • frq: only hash differs (likely formatting/whitespace)
   • kfr: only hash differs (likely formatting/whitespace)
   ...

These changes don't affect data integrity:
   ✅ All stems present
   ✅ All examples preserved
   ✅ Etymology intact
   ✅ Conjugations unchanged

Update baseline to clear these warnings? (y/n): y

🔄 Updating baseline...
✅ Baseline updated successfully
✅ Validation will pass on next run
```

### 3. Critical Regression Detection

When real regressions are found:

```
❌ CRITICAL REGRESSIONS DETECTED

Validation Errors:
   • REGRESSION: frq - Lost 2 stems (was 5, now 3)
   • REGRESSION: kfr - Lost etymology

❌ DO NOT update baseline! Fix parser first.
```

### 4. CI/CD Safety

- Detects non-interactive environments (CI=true, no TTY)
- Skips prompts in automated pipelines
- Exits with proper error codes

## Usage

### Basic Validation

```bash
python3 parser/parse_verbs.py --validate
```

### Workflow

1. **Make parser changes**

   ```bash
   vim parser/parse_verbs.py
   ```

2. **Run parser with validation**

   ```bash
   python3 parser/parse_verbs.py --validate
   ```

3. **Three possible outcomes:**

   **A) No changes detected:**

   ```
   ✅ NO REGRESSIONS
   Exit code: 0
   ```

   **B) Safe changes (false positives):**

   ```
   ⚠️  Neutral changes detected - analyzing...
   ✅ Found N safe changes (false positives)
   Update baseline to clear these warnings? (y/n): y
   ✅ Baseline updated successfully
   Exit code: 0
   ```

   **C) Critical regressions:**

   ```
   ❌ CRITICAL REGRESSIONS DETECTED
   ❌ DO NOT update baseline! Fix parser first.
   Exit code: 1
   ```

### Manual Baseline Update

If you skip the prompt or run in non-interactive mode:

```bash
python3 parser/snapshot_baseline.py
```

## Exit Codes

- **0** = Success (no regressions, or safe changes accepted)
- **1** = Failure (critical regressions, unsafe changes, or prompt declined)

## Implementation Details

### Files Modified

**`parser/regression_validator.py`:**

- Added `is_safe_change()` - structural comparison
- Added `analyze_neutral_changes()` - classify neutral changes
- Added `is_interactive()` - detect terminal vs CI
- Added `prompt_user()` - interactive confirmation
- Added `update_baseline()` - automatic baseline update
- Enhanced `validate()` - new workflow logic

### Safety Checks

The `is_safe_change()` function validates:

```python
def is_safe_change(self, root, baseline_entry, current_data):
    baseline_struct = baseline_entry['structure']
    current_struct = self.extract_structure(current_data)

    # Check all structural components
    if baseline_struct['stem_count'] != current_struct['stem_count']:
        return (False, "stem_count differs")

    if baseline_struct['has_etymology'] != current_struct['has_etymology']:
        return (False, "etymology presence differs")

    # ... more checks ...

    return (True, "only hash differs (likely formatting/whitespace)")
```

## Testing

### Test Scenario 1: No Changes

```bash
# Run parser twice without changes
python3 parser/parse_verbs.py --validate
# Expected: ✅ NO REGRESSIONS (exit 0)
```

### Test Scenario 2: Safe Changes

```bash
# Make cosmetic parser change (add comment, reformat)
python3 parser/parse_verbs.py --validate
# Expected: Prompt for baseline update
# Select 'y' -> exit 0
# Select 'n' -> exit 1
```

### Test Scenario 3: Critical Regression

```bash
# Break parser (remove a stem extraction line)
python3 parser/parse_verbs.py --validate
# Expected: ❌ CRITICAL REGRESSIONS (exit 1, no prompt)
```

## Future Enhancements

1. **Diff visualization** - Show exact changes for safe modifications
2. **Whitelist patterns** - Configure acceptable safe change patterns
3. **Batch approval** - Review all safe changes before accepting
4. **Rollback support** - Undo baseline updates if needed

## Notes

- Always review HTML report in `data/validation/regression_report.html`
- Check JSON summary in `data/validation/regression_summary.json`
- Safe changes are only auto-updated with explicit user confirmation
- Non-interactive mode (CI/CD) never auto-updates baseline
