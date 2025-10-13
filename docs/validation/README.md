# Parser Validation Framework

This directory contains comprehensive validation documentation and tools for the Turoyo verb parser.

## Quick Navigation

- **[START_HERE.md](START_HERE.md)** - Quick start guide (begin here!)
- **[VALIDATION_QUICKSTART.md](VALIDATION_QUICKSTART.md)** - One-page reference
- **[VALIDATION_MASTER_REPORT.md](VALIDATION_MASTER_REPORT.md)** - Comprehensive findings
- **[VALIDATION_IMPLEMENTATION.md](VALIDATION_IMPLEMENTATION.md)** - Technical details

## For LLMs / Claude Code

If you're an AI assistant working on this parser, **read this first:**

### Critical Validation Rules

**BEFORE making ANY parser changes:**
1. Create baseline: `python3 parser/snapshot_baseline.py`
2. Make your changes to `parser/parse_verbs.py`
3. Validate: `python3 parser/parse_verbs.py --validate`
4. Check report: `open data/validation/regression_report.html`
5. Only proceed if NO regressions detected (exit code 0)

### What Validation Checks

✅ **Prevents:**
- Verbs being lost (count must not decrease)
- Stems disappearing (all baseline stems must exist)
- Examples vanishing (conjugation data must remain)
- HTML artifacts in output (clean text only)
- Character encoding corruption (valid UTF-8)
- Cross-reference breaks (all refs must resolve)

❌ **Blocks code if:**
- Verb count decreases
- Any baseline verb is missing
- Stems are lost from existing verbs
- HTML tags appear in text fields
- Data is truncated or corrupted

✅ **Allows:**
- More verbs (improvements)
- More stems (better extraction)
- More examples (better parsing)
- Bug fixes (cleaner data)
- New fields (enhancements)

### Commands Reference

```bash
# Create baseline (first time or after approved changes)
python3 parser/snapshot_baseline.py

# Parse with validation
python3 parser/parse_verbs.py --validate

# Parse, validate, and update baseline (if all good)
python3 parser/parse_verbs.py --validate --update-baseline

# Just validate (without re-parsing)
python3 parser/regression_validator.py

# Run unit tests
python3 parser/test_parser.py
```

### Exit Codes

- **0** = Success, no regressions
- **1** = Regressions detected, DO NOT MERGE

### Where to Find Things

- **Baseline data:** `data/baseline/`
- **Validation reports:** `data/validation/`
- **Unit tests:** `parser/test_parser.py`
- **Test fixtures:** `data/validation/parser_test_fixtures.json`
- **Pattern samples:** `data/validation/pattern_samples.html`

## Documentation Structure

```
docs/validation/
├── README.md                              ← You are here
├── START_HERE.md                          ← Quick start
├── VALIDATION_QUICKSTART.md               ← One-page ref
├── VALIDATION_MASTER_REPORT.md            ← Full findings
└── VALIDATION_IMPLEMENTATION.md           ← Technical details
```

## Current Status

- **Parser:** ✅ Working correctly (1,696 verbs)
- **Validation Framework:** ✅ Production ready
- **Unit Tests:** ✅ 17/20 passing
- **Documentation:** ✅ Complete

Last validated: 2025-10-13
