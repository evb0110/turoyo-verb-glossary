# Parser Validation - Quick Start

⚡ **One-page guide to the regression testing framework**

---

## 🚀 First Time Setup

```bash
# Create baseline of current parser output
python3 parser/snapshot_baseline.py
```

**Done!** Baseline saved to `data/baseline/baseline.json`

---

## 🔄 Daily Workflow

### Making Parser Changes

```bash
# 1. Make your changes to parse_verbs.py
vim parser/parse_verbs.py

# 2. Run parser with validation
python3 parser/parse_verbs.py --validate

# 3. View results
open data/validation/regression_report.html
```

### If Changes Look Good

```bash
# Update baseline to accept changes
python3 parser/snapshot_baseline.py
```

---

## 📋 Common Commands

| Task | Command |
|------|---------|
| **Create baseline** | `python3 parser/snapshot_baseline.py` |
| **View baseline info** | `python3 parser/snapshot_baseline.py --report` |
| **Validate output** | `python3 parser/regression_validator.py` |
| **Parse + validate** | `python3 parser/parse_verbs.py --validate` |
| **Run unit tests** | `python3 parser/test_parser.py` |
| **View HTML report** | `open data/validation/regression_report.html` |

---

## 🎯 What to Look For

### ✅ Good (Improvements)
- New stems added
- More examples extracted
- Etymology added
- Bug fixes

### ⚠️ Neutral (Review)
- Formatting changes
- Whitespace normalization

### ❌ Bad (Regressions)
- Verbs removed
- Stems lost
- Examples disappeared
- HTML tags in text
- Etymology missing

---

## 🔍 Reading the Report

**HTML Report:** `data/validation/regression_report.html`

```
🧪 Parser Regression Report
━━━━━━━━━━━━━━━━━━━━━━━

✅ NO REGRESSIONS  (or ❌ REGRESSIONS DETECTED)

Summary
├─ Unchanged: 1561
├─ Improvements: 0
├─ Neutral: 0
├─ Regressions: 0
├─ Added: 0
└─ Removed: 0

[Detailed changes listed by category]
```

**JSON Summary:** `data/validation/regression_summary.json`

```json
{
  "status": "pass",  // or "fail"
  "counts": { ... },
  "regressions": [],
  "improvements": []
}
```

---

## 🚨 Troubleshooting

### "No baseline found"
```bash
# Create one first
python3 parser/snapshot_baseline.py
```

### "Validation failed" but report shows improvements
```bash
# Review report, then update baseline
open data/validation/regression_report.html
python3 parser/snapshot_baseline.py
```

### Tests failing
```bash
# Run tests to see details
python3 parser/test_parser.py -v
```

---

## 📊 Exit Codes

- `0` = Pass (no regressions)
- `1` = Fail (regressions detected)

Perfect for CI/CD:

```bash
python3 parser/regression_validator.py
if [ $? -eq 0 ]; then
    echo "✅ Safe to deploy"
else
    echo "❌ Review required"
    exit 1
fi
```

---

## 📚 Full Documentation

See **[README_VALIDATION.md](README_VALIDATION.md)** for:
- Detailed validation rules
- Advanced workflows
- CI/CD integration
- Adding new tests
- Best practices

---

## 💡 Key Principles

1. **Always create baseline before changes**
2. **Run validation after every parser edit**
3. **Review HTML report carefully**
4. **Update baseline only after verifying changes are good**
5. **Never ignore regressions**

---

## ⏱️ Performance

- Baseline: ~5 seconds
- Validation: ~5 seconds
- Unit tests: ~1 second
- Full pipeline: ~2-3 minutes

---

## 🎓 Example Session

```bash
# Start
$ python3 parser/snapshot_baseline.py
✅ Baseline created: 1561 verbs

# Make changes
$ vim parser/parse_verbs.py
# ... improved etymology parsing ...

# Validate
$ python3 parser/parse_verbs.py --validate
✅ PARSING COMPLETE!
✅ Loaded baseline: 1561 verbs
✅ Loaded current output: 1561 verbs
🔍 Detecting changes...
   • Modified (improvements): 45
   • Modified (regressions): 0
✅ NO REGRESSIONS

# Review
$ open data/validation/regression_report.html
# [Shows 45 verbs now have etymology where they didn't before]

# Accept changes
$ python3 parser/snapshot_baseline.py
✅ Baseline updated successfully
```

---

**🎉 You're ready to make parser changes safely!**

For help: See [README_VALIDATION.md](README_VALIDATION.md)
