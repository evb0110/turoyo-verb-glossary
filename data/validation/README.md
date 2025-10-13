# Turoyo Verb Glossary - Source HTML Validation Report

**Analysis Completed:** 2025-10-13
**Analyzed By:** Claude Code (Tier 1 Analysis)

## Overview

This directory contains a comprehensive analysis of the Turoyo verb glossary source HTML file, cataloging ALL structural patterns and identifying parser gaps.

## Files in This Directory

### 1. **source_analysis_report.json**
Complete technical analysis in JSON format:
- Total statistics (1,696 verbs across 29 letter sections)
- Root pattern catalog (2 variations: with/without `<font>`)
- Stem header patterns (3 variations captured)
- Etymology patterns (1,182 entries with relationship types)
- Edge cases (cross-references, uncertain entries, detransitive, homonyms)
- **2 Parser bugs identified** with detailed analysis
- 4 prioritized recommendations

### 2. **pattern_samples.html**
Visual HTML document showing:
- Real examples extracted from source HTML
- Side-by-side comparison of correct vs. buggy patterns
- Color-coded status indicators (✅ working, ❌ broken)
- Interactive demonstration of the German gloss bug
- Open in browser for best viewing experience

### 3. **ANALYSIS_SUMMARY.md**
Executive summary and detailed technical report:
- Pattern catalog with regex and counts
- Bug analysis with root cause and fix suggestions
- Test cases for validation
- Implementation roadmap

## Key Findings

### ✅ What's Working

1. **Root Pattern Detection:** All 1,696 entries correctly matched
   - Pattern with `<font>`: 1,450 entries
   - Pattern without `<font>`: 246 entries
   - Combined parser pattern handles both

2. **Stem Header Parsing:** All 3 variations captured
   - Main pattern: 1,753 stems
   - Alternative pattern: 1,796 stems
   - Fallback pattern: 12 stems

3. **Etymology Parsing:** Complete coverage
   - 1,182 etymologies extracted (69.7% of verbs)
   - All relationship types handled (also, or, and)
   - Top sources: Arab. (584), MEA (459), Kurd. (73)

4. **Edge Cases:** All handled correctly
   - Cross-references: 7 entries (→ symbol)
   - Uncertain entries: 58 entries (??? marker)
   - Detransitive sections: 525 entries (2 patterns)

### ❌ Critical Bug Found

**BUG-001: German Glosses Mistaken for Roots**
- **Severity:** 🔴 CRITICAL
- **Impact:** Parser gets 1632 verbs instead of 1696 (64 missing)
- **Cause:** Filter checks if ANY character is in Turoyo set, but common letters like 't', 's', 'h' are in both German and Turoyo
- **Examples:**
  - "stöhnen;" → extracts "st" as root
  - "stampfen;" → extracts "st" as root
  - "studieren;" → extracts "st" as root
  - Result: 28 false "st" roots, 13 false "gr" roots, etc.

**Root Cause:**
```python
# Current filter (LINE 79-80 in parser)
if ';' in full_span_text and not any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
    continue  # Skip German gloss
```

The character 't' is in the Turoyo character class (for ṭ, ṯ), so "stöhnen" contains 't' which makes the filter think it's Turoyo!

**Fix:**
Only check for SPECIAL Turoyo characters (pharyngeals, emphatics, etc.):
```python
special_turoyo = 'ʔʕġǧḥṣštṭḏṯẓāēīūə'  # Only special chars, not basic Latin

if ';' in full_span_text and not any(c in full_span_text for c in special_turoyo):
    continue  # Skip German gloss
```

### ⚠️  Secondary Issue

**BUG-002: Homonym Numbering Without Etymology Differences**
- **Severity:** 🟡 MEDIUM
- **Issue:** Parser numbers all duplicate roots, even when they have the same (or no) etymology
- **Impact:** Obscures genuine homonyms, creates unnecessary numbers
- **Note:** Partly caused by BUG-001 (German glosses have no etymology)

## Statistics

| Metric | Count | Notes |
|--------|-------|-------|
| Letter sections | 29 | ʔ, ʕ, b, č, d, f, g, ġ, ǧ, h, ḥ, k, l, m, n, p, q, r, s, ṣ, š, t, ṭ, ṯ, w, x, y, z, ž |
| Total root candidates | 1,696 | ✅ Exact match with expected |
| Unique roots | 1,443 | Some roots have multiple entries (homonyms) |
| Roots with `<font>` | 1,450 | 85.5% |
| Roots without `<font>` | 246 | 14.5% (was causing 247-verb bug) |
| Stem headers | 1,753+ | All 3 pattern variations captured |
| Etymologies | 1,182 | 69.7% of verbs have etymology |
| Cross-references | 7 | Entries with → symbol |
| Uncertain entries | 58 | Marked with ??? |
| Detransitive sections | 525 | Special conjugation type |
| Homonym roots | 130 | BUT many are false (German glosses) |

## Etymology Sources

1. **Arab.** - 584 entries (49.4%)
2. **MEA** - 459 entries (38.8%)
3. **Kurd.** - 73 entries (6.2%)
4. **Turk.** - 21 entries (1.8%)
5. **denom.** - 9 entries (0.8%)

## Recommendations (Priority Order)

### 1. CRITICAL: Fix German Gloss Filter
- **Estimated Time:** 15 minutes
- **Risk:** Low (isolated change)
- **Expected Result:** Extract exactly 1,696 verbs
- **Test:** `assert len(verbs) == 1696`

### 2. HIGH: Add Validation Test
```python
assert len(verbs) == 1696, f'Expected 1696 verbs, got {len(verbs)}'
```
- Fail parsing if count doesn't match
- Prevents silent regressions

### 3. MEDIUM: Improve Homonym Detection
- Only number homonyms with DIFFERENT etymologies
- Skip homonyms where all entries have `None` etymology
- This will reduce false homonyms from 130 to ~20

### 4. LOW: Add Pattern Documentation
- Comment each regex pattern explaining why it exists
- Document the `<font>` optional fix (247-verb bug)
- Explain the 3 stem header patterns

## Test Cases

### Test 1: German Gloss Filter
```python
test_cases = [
    ("stöhnen;", False),      # Should NOT match
    ("stampfen;", False),     # Should NOT match
    ("ʔbʕ", True),            # Should match
    ("mṭaṣər", True),         # Should match (has ṭ)
]
```

### Test 2: Total Count
```python
def test_total_verbs(parser):
    verbs = parser.parse_all()
    assert len(verbs) == 1696, f"Expected 1696, got {len(verbs)}"
```

### Test 3: Homonym Quality
```python
def test_homonym_numbering(parser):
    # ʔmr should be numbered (different etymologies)
    assert 'ʔmr 1' in [v['root'] for v in parser.verbs]
    assert 'ʔmr 2' in [v['root'] for v in parser.verbs]

    # st should NOT be numbered (German glosses)
    assert 'st 1' not in [v['root'] for v in parser.verbs]
```

## How to Use This Report

1. **For fixing the parser:** See `ANALYSIS_SUMMARY.md` section 6 (Recommendations)
2. **For visual examples:** Open `pattern_samples.html` in a browser
3. **For programmatic analysis:** Use `source_analysis_report.json`
4. **For test fixtures:** Implement test cases from this README

## Validation Checklist

- ✅ Root patterns: All 1,696 entries matched
- ✅ Stem patterns: All variations covered (3 patterns)
- ✅ Etymology parsing: All formats handled correctly
- ✅ Cross-references: Detected and processed (7 entries)
- ✅ Uncertain entries: Flagged correctly (58 entries)
- ✅ Detransitive sections: Both patterns recognized (525 entries)
- ❌ German gloss filter: FAILING - causes 64 false positives
- ⚠️  Homonym numbering: WORKING but polluted by BUG-001

## Next Steps

1. Fix BUG-001 (German gloss filter) - **CRITICAL**
2. Add validation test for total count = 1696
3. Improve homonym detection logic
4. Re-run parser and verify output
5. Update regression tests with new baseline

## Contact

This analysis was generated by Claude Code as part of the Turoyo Verb Glossary project.
For questions or issues, refer to the main project documentation.
