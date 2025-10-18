# Parser Validation Workflow Diagram

## Complete Workflow Flowchart

```
┌─────────────────────────────────────┐
│  Make Parser Changes                │
│  (edit parser/parse_verbs.py)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Run Parser with Validation         │
│  python3 parser/parse_verbs.py      │
│  --validate                          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Parser Executes                    │
│  • Parse HTML source                │
│  • Extract verbs, stems, examples   │
│  • Generate JSON files              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Validation Starts                  │
│  • Load baseline                    │
│  • Load current output              │
│  • Detect changes                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Classify Changes                   │
│  • Added verbs                      │
│  • Removed verbs                    │
│  • Modified verbs:                  │
│    - Improvements                   │
│    - Neutral                        │
│    - Regressions                    │
│  • Unchanged verbs                  │
└──────────────┬──────────────────────┘
               │
               ▼
        ╔═════════════════╗
        ║ Critical        ║
        ║ Regressions?    ║
        ║ (data loss)     ║
        ╚════╤═══════╤════╝
             │       │
         YES │       │ NO
             │       │
             ▼       ▼
    ┌────────────┐  ┌────────────────────┐
    │ ❌ FAIL    │  │ Check Neutral      │
    │            │  │ Changes            │
    │ DO NOT     │  └────────┬───────────┘
    │ update     │           │
    │ baseline!  │           ▼
    │            │    ╔══════════════╗
    │ Exit: 1    │    ║ Neutral      ║
    └────────────┘    ║ Changes?     ║
                      ╚═══╤════╤═════╝
                          │    │
                      YES │    │ NO
                          │    │
                          ▼    ▼
                 ┌────────────┐ ┌────────────┐
                 │ Analyze    │ │ ✅ PASS    │
                 │ Neutral    │ │            │
                 │ Changes    │ │ No         │
                 └──────┬─────┘ │ Regressions│
                        │       │            │
                        ▼       │ Exit: 0    │
                 ╔══════════════╗ └────────────┘
                 ║ Safe         ║
                 ║ Changes?     ║
                 ║ (hash only)  ║
                 ╚═══╤════╤═════╝
                     │    │
                 YES │    │ NO (unsafe)
                     │    │
                     ▼    ▼
            ┌────────────┐ ┌────────────┐
            │ Safe       │ │ ❌ FAIL    │
            │ Changes    │ │            │
            │ Detected   │ │ Investigate│
            └──────┬─────┘ │ Changes    │
                   │       │            │
                   ▼       │ Exit: 1    │
            ╔══════════════╗ └────────────┘
            ║ Interactive  ║
            ║ Terminal?    ║
            ╚═══╤════╤═════╝
                │    │
            YES │    │ NO (CI/CD)
                │    │
                ▼    ▼
       ┌────────────┐ ┌────────────┐
       │ Prompt     │ │ ⚠️  SKIP   │
       │ User:      │ │            │
       │            │ │ Manual     │
       │ "Update    │ │ update     │
       │ baseline?" │ │ needed     │
       └──────┬─────┘ │            │
              │       │ Exit: 1    │
              ▼       └────────────┘
       ╔══════════════╗
       ║ User         ║
       ║ Response?    ║
       ╚═══╤════╤═════╝
           │    │
       YES │    │ NO
           │    │
           ▼    ▼
  ┌────────────┐ ┌────────────┐
  │ Update     │ │ ⚠️  SKIP   │
  │ Baseline   │ │            │
  │            │ │ Warnings   │
  │ Auto-run:  │ │ Persist    │
  │ snapshot_  │ │            │
  │ baseline.  │ │ Exit: 1    │
  │ py         │ └────────────┘
  └──────┬─────┘
         │
         ▼
  ┌────────────┐
  │ ✅ SUCCESS │
  │            │
  │ Baseline   │
  │ Updated    │
  │            │
  │ Exit: 0    │
  └────────────┘
```

## Decision Points Explained

### 1. Critical Regressions Check

**Tests for:**

- Verb count decreased
- Verbs removed from baseline
- Stems lost from existing verbs
- Examples disappeared
- Etymology removed
- Conjugations lost

**If detected:**

- No prompt shown
- Exit code: 1
- Message: "❌ DO NOT update baseline! Fix parser first."

### 2. Neutral Changes Analysis

**Tests for:**

- Hash differences only
- Structural data unchanged:
  - Same stem count
  - Same example count
  - Same conjugation types
  - Same etymology presence
  - Same form count

**Classification:**

- **Safe:** Only formatting/whitespace differs
- **Unsafe:** Unexpected structural differences

### 3. Interactive Mode Check

**Detects:**

- `sys.stdin.isatty()` - Has terminal?
- `CI != 'true'` - Not in CI/CD?

**Behavior:**

- **Interactive:** Show prompt, get user input
- **Non-interactive:** Skip prompt, exit with code 1

### 4. User Response

**Accepts:**

- 'y', 'yes' → Update baseline
- 'n', 'no' → Keep warnings

**Validation:**

- Re-prompts on invalid input
- Case-insensitive

## Example Outputs by Path

### Path A: Critical Regression

```
❌ CRITICAL REGRESSIONS DETECTED

Validation Errors:
   • REGRESSION: frq - Lost stems: 5 → 3
   • REGRESSION: kfr - Lost etymology

❌ DO NOT update baseline! Fix parser first.
Exit code: 1
```

### Path B: Safe Changes (User Accepts)

```
⚠️  Neutral changes detected - analyzing...

✅ Found 18 safe changes (false positives):
   • frq: only hash differs (likely formatting/whitespace)
   ... and 17 more

These changes don't affect data integrity:
   ✅ All stems present
   ✅ All examples preserved
   ✅ Etymology intact
   ✅ Conjugations unchanged

Update baseline to clear these warnings? (y/n): y

🔄 Updating baseline...
✅ Baseline updated successfully
✅ Validation will pass on next run
Exit code: 0
```

### Path C: Safe Changes (User Declines)

```
⚠️  Neutral changes detected - analyzing...

✅ Found 18 safe changes (false positives):
   ... [same as above] ...

Update baseline to clear these warnings? (y/n): n

⚠️  Baseline not updated - warnings will persist
Exit code: 1
```

### Path D: Safe Changes (CI/CD)

```
⚠️  Neutral changes detected - analyzing...

✅ Found 18 safe changes (false positives):
   ... [same as above] ...

⚠️  Running in non-interactive mode - skipping baseline update
⚠️  Run manually: python3 parser/snapshot_baseline.py
Exit code: 1
```

### Path E: No Changes

```
✅ NO REGRESSIONS
Exit code: 0
```

### Path F: Unsafe Neutral Changes

```
⚠️  Neutral changes detected - analyzing...

❌ Found 5 neutral changes that appear unsafe:
   • frq: stem name differs (I vs II)
   • kfr: form count differs
   • qbl: example count differs
   ... and 2 more

❌ These changes need investigation. Do not update baseline.
Exit code: 1
```

## Exit Code Summary

| Scenario                     | Exit Code | Next Action                |
| ---------------------------- | --------- | -------------------------- |
| No changes                   | 0         | Continue working           |
| Improvements only            | 0         | Optionally update baseline |
| Safe changes + user accepts  | 0         | Continue working           |
| Safe changes + user declines | 1         | Re-run or update manually  |
| Safe changes + CI/CD         | 1         | Update baseline manually   |
| Unsafe neutral changes       | 1         | Investigate changes        |
| Critical regressions         | 1         | Fix parser                 |

## Quick Command Reference

```bash
# Full workflow (parse + validate)
python3 parser/parse_verbs.py --validate

# Just validate (no re-parsing)
python3 parser/regression_validator.py

# Manual baseline update
python3 parser/snapshot_baseline.py

# View baseline info
python3 parser/snapshot_baseline.py --report

# Check validation report
open data/validation/regression_report.html

# Check JSON summary
cat data/validation/regression_summary.json | python3 -m json.tool
```

## Color Legend

```
✅ = Success / Pass
❌ = Error / Fail
⚠️  = Warning / Attention Needed
🔄 = Processing / Working
📝 = Report / Documentation
📊 = Statistics / Metrics
```

## Best Practices

1. **Always validate** before committing parser changes
2. **Review the report** in `data/validation/regression_report.html`
3. **Understand safe changes** before accepting baseline update
4. **Never force through** critical regressions
5. **Test locally** before pushing to CI/CD
6. **Document improvements** when baseline is updated
7. **Keep baseline current** after approved changes

## Troubleshooting

### "No baseline found"

```bash
python3 parser/snapshot_baseline.py
```

### "Validation failed but I made no changes"

```bash
# Check what changed
open data/validation/regression_report.html

# If truly safe, update baseline
python3 parser/snapshot_baseline.py
```

### "Prompt not showing in terminal"

```bash
# Check if running in CI mode
echo $CI

# Check if stdin is TTY
python3 -c "import sys; print(sys.stdin.isatty())"
```

### "Baseline update failed"

```bash
# Check error message
python3 parser/snapshot_baseline.py

# Verify verbs directory exists
ls -la server/assets/verbs/

# Check permissions
ls -ld data/baseline/
```
