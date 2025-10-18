# Parser Validation Quick Reference Card

## One-Page Cheat Sheet

### Daily Workflow

```bash
# 1. Make parser changes
vim parser/parse_verbs.py

# 2. Run with validation
python3 parser/parse_verbs.py --validate

# 3. Three outcomes:

# ✅ NO REGRESSIONS
#    → Continue working

# ⚠️  Safe changes detected
#    → Prompt: "Update baseline? (y/n):"
#    → Answer 'y' to auto-update

# ❌ CRITICAL REGRESSIONS
#    → Fix parser and re-run
```

### Commands

| Command                                        | Purpose          | When to Use              |
| ---------------------------------------------- | ---------------- | ------------------------ |
| `python3 parser/parse_verbs.py --validate`     | Parse + validate | After parser changes     |
| `python3 parser/regression_validator.py`       | Just validate    | Check without re-parsing |
| `python3 parser/snapshot_baseline.py`          | Update baseline  | Manually update baseline |
| `python3 parser/snapshot_baseline.py --report` | View baseline    | Check current baseline   |

### Exit Codes

| Code | Meaning    | Action             |
| ---- | ---------- | ------------------ |
| 0    | ✅ Success | Continue           |
| 1    | ❌ Failure | Fix or investigate |

### Decision Tree

```
Parser Change
    ↓
Run --validate
    ↓
    ├─→ Critical Regression? → ❌ Fix parser (exit 1)
    ├─→ Safe Changes? → ⚠️  Prompt for update (exit 0 or 1)
    └─→ No Changes? → ✅ Pass (exit 0)
```

### Validation Checks

✅ **Ensures:**

- Verb count maintained
- All stems present
- Examples preserved
- Etymology intact
- No HTML artifacts

❌ **Blocks:**

- Data loss
- Missing stems
- Lost examples
- Removed etymology
- HTML in output

### Safe vs Critical

| Safe Changes           | Critical Regressions |
| ---------------------- | -------------------- |
| Formatting differences | Verb count decreased |
| Whitespace changes     | Stems lost           |
| Field ordering         | Examples removed     |
| Hash differences       | Etymology deleted    |
| _Prompts for update_   | _Blocks immediately_ |

### Interactive Prompts

**When shown:**

- Safe changes detected
- Running in terminal (not CI/CD)

**Response:**

- `y` or `yes` → Auto-update baseline (exit 0)
- `n` or `no` → Keep warnings (exit 1)

**When NOT shown:**

- Critical regressions (always blocks)
- CI/CD mode (always exits 1)
- No changes (always exits 0)

### Files to Know

| Path                                      | Purpose             |
| ----------------------------------------- | ------------------- |
| `parser/parse_verbs.py`                   | Main parser script  |
| `parser/regression_validator.py`          | Validation logic    |
| `parser/snapshot_baseline.py`             | Baseline creator    |
| `data/baseline/baseline.json`             | Known good snapshot |
| `data/validation/regression_report.html`  | Validation report   |
| `data/validation/regression_summary.json` | JSON summary        |

### Common Scenarios

#### Scenario 1: First Time Setup

```bash
python3 parser/parse_verbs.py
python3 parser/snapshot_baseline.py
```

#### Scenario 2: After Parser Change

```bash
python3 parser/parse_verbs.py --validate
# If safe changes detected, answer 'y' to prompt
```

#### Scenario 3: Manual Baseline Update

```bash
python3 parser/snapshot_baseline.py
```

#### Scenario 4: Check Current Status

```bash
python3 parser/regression_validator.py
open data/validation/regression_report.html
```

#### Scenario 5: CI/CD Pipeline

```yaml
- name: Validate Parser
  run: python3 parser/parse_verbs.py --validate
  # Exits 1 if issues found, pipeline fails
```

### Troubleshooting

| Problem                 | Solution                                   |
| ----------------------- | ------------------------------------------ |
| "No baseline found"     | Run `python3 parser/snapshot_baseline.py`  |
| Prompt not showing      | Check `$CI` env var, verify TTY            |
| Validation always fails | Check `regression_report.html` for details |
| Can't update baseline   | Check permissions on `data/baseline/`      |

### Pro Tips

1. **Always validate** before committing
2. **Review reports** in HTML format
3. **Understand changes** before accepting
4. **Never skip** critical regressions
5. **Keep baseline current** after approved changes

### Quick Checks

```bash
# How many verbs in baseline?
cat data/baseline/summary.json | python3 -c "import sys, json; print(json.load(sys.stdin)['total_files'])"

# How many verbs currently?
ls server/assets/verbs/*.json | wc -l

# View specific verb
cat server/assets/verbs/frq.json | python3 -m json.tool

# Compare counts
echo "Baseline: $(cat data/baseline/summary.json | python3 -c 'import sys, json; print(json.load(sys.stdin)[\"total_files\"])')"
echo "Current: $(ls server/assets/verbs/*.json | wc -l | tr -d ' ')"
```

### Expected Numbers

| Metric           | Expected |
| ---------------- | -------- |
| Total verbs      | 1,518    |
| Total stems      | ~2,249   |
| Total examples   | ~4,916   |
| Homonyms         | ~225     |
| Cross-references | ~7       |

### Help & Documentation

| Resource         | Location                                  |
| ---------------- | ----------------------------------------- |
| Quick Start      | `docs/validation/START_HERE.md`           |
| Scenarios        | `docs/validation/VALIDATION_SCENARIOS.md` |
| Workflow Diagram | `docs/validation/WORKFLOW_DIAGRAM.md`     |
| Full README      | `docs/validation/README.md`               |
| Implementation   | `.devkit/docs/IMPLEMENTATION_SUMMARY.md`  |

---

## Copy-Paste Commands

### Daily Use

```bash
python3 parser/parse_verbs.py --validate
```

### First Time

```bash
python3 parser/snapshot_baseline.py
```

### Manual Update

```bash
python3 parser/snapshot_baseline.py
```

### Check Status

```bash
python3 parser/regression_validator.py && echo "✅ Valid" || echo "❌ Issues"
```

### View Report

```bash
open data/validation/regression_report.html
```

---

**Last Updated:** 2025-10-18
**Version:** Enhanced Validation 2.0
