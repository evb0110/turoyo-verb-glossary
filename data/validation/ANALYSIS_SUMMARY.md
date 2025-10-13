# Turoyo Verb Glossary - Source HTML Analysis Report

**Analysis Date:** 2025-10-13
**Analyst:** Claude Code
**Source File:** `source/Turoyo_all_2024.html`
**Expected Total:** 1,696 verbs

---

## Executive Summary

### Status: CRITICAL BUG FOUND

The parser successfully identifies **ALL 1,696 root entry patterns** in the source HTML, but incorrectly extracts **~64 German verb glosses** as Turoyo roots due to a flawed filter, resulting in **1,632 actual verbs + 64 false positives**.

### Critical Finding

**BUG-001: German Glosses Mistaken for Roots**
- **Severity:** CRITICAL
- **Impact:** Parser gets 1632 verbs instead of 1696 (64 missing)
- **Root Cause:** Filter uses common Latin letters (t, s, h) present in both German and Turoyo
- **Examples:** "stöhnen", "stampfen", "studieren" are extracted as roots "st", "st", "st"

---

## 1. Pattern Catalog

### 1.1 Root Entry Patterns

The parser must recognize verb roots in two HTML variations:

#### Pattern 1: With `<font>` Tag (1,450 entries)
```html
<p class="western"><font color="#000000"><span>ROOT</span></font>
```
- **Status:** ✅ CORRECTLY HANDLED
- **Parser Solution:** Makes `<font>` optional with `(?:<font[^>]*>)?`
- **Note:** This was the fix for the 247-verb bug

#### Pattern 2: Without `<font>` Tag (246 entries)
```html
<p class="western"><span>ROOT</span>
```
- **Status:** ✅ CORRECTLY HANDLED
- **Parser Solution:** Same optional `<font>` pattern catches these

#### Parser Regex
```python
root_pattern = r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)?<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(?:\s*\d+)?[^<]*</span>'
```
- **Total Matches:** 1,696 ✅
- **Problem:** Also matches German glosses that appear in same structure

### 1.2 German Gloss Problem (BUG-001)

#### False Positive Pattern
```html
<p class="western"><span>stöhnen;</span></p>
```

This appears WITHIN verb entries as German translations for stem headers.

#### Why It Matches
1. Pattern `[ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6}` matches "st" (stops before 'ö')
2. Filter checks: `any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə')`
3. The letter 't' is in the Turoyo character set
4. "stöhnen" contains 't', so filter thinks it's Turoyo!

#### Current Filter Logic (FLAWED)
```python
# Line 79-80 in parser
if ';' in full_span_text and not any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
    continue  # Skip German gloss
```

**Problem:** Checks if ANY Turoyo character exists in text, but 't', 's', 'h' are common to both German and Turoyo.

#### Impact
- ~64 German glosses extracted as roots
- Most common false positives: st (28), gr (13), tr (13), br (11), sp (10)
- These inflate the homonym count and obscure real duplicates

#### Suggested Fix
```python
# Check for SPECIAL Turoyo characters only (pharyngeals, emphatics, etc.)
special_turoyo = 'ʔʕġǧḥṣštṭḏṯẓāēīūə'  # Exclude basic Latin: bcdfghjklmnpqrstuvwxyz

# Skip if: has semicolon AND (no special Turoyo chars OR has umlauts/German chars)
has_semicolon = ';' in full_span_text
has_special_turoyo = any(c in full_span_text for c in special_turoyo)
has_german_chars = any(c in full_span_text for c in 'äöüÄÖÜß')

if has_semicolon and (not has_special_turoyo or has_german_chars):
    continue  # Skip German gloss
```

---

## 2. Stem Header Patterns

### Pattern Coverage

| Pattern | Count | Status |
|---------|-------|--------|
| Main: Stem + Forms in separate spans | 1,753 | ✅ Captured |
| Alternative: Stem + Forms in same span | 1,796 | ✅ Captured |
| Fallback: Simple `<span>I:</span>` | 12 | ✅ Captured |

#### Pattern 1 (Main)
```html
<font size="4"><b><span>I: </span></b></font></font>
<font><font><i><b><span>abəʕ/obəʕ</span></b></i></font></font>
```

#### Pattern 2 (Alternative)
```html
<font size="4"><b><span>I: abəʕ/obəʕ</span></b></font>
```

#### Pattern 3 (Fallback)
```html
<p><span>I:</span></p>
<!-- Forms appear in lookahead -->
```

**Conclusion:** All stem header variations are successfully captured by the parser's 3-pattern approach.

---

## 3. Etymology Patterns

### Distribution

| Type | Count | Percentage |
|------|-------|------------|
| Total etymologies | 1,182 | 69.7% of verbs |
| With "also" relationship | 20 | 1.7% |
| With "or" relationship | 12 | 1.0% |
| With "and" relationship | 9 | 0.8% |
| Simple (single source) | 1,141 | 96.5% |

### Top Etymology Sources

1. **Arab.** - 584 (49.4%)
2. **MEA** - 459 (38.8%)
3. **Kurd.** - 73 (6.2%)
4. **Turk.** - 21 (1.8%)
5. **denom.** - 9 (0.8%)

### Pattern Format
```
(&lt; SOURCE ROOT cf. REFERENCE: MEANING)
```

Example:
```
(&lt; MEA ʔnn cf. SL 63: to groan; to mourn;)
```

**Status:** ✅ All etymology patterns correctly parsed, including complex relationships.

---

## 4. Edge Cases

### 4.1 Cross-References (7 entries)
```html
<span>ʕwḏ → ʕwd</span>
```
- **Status:** ✅ Detected and handled
- Examples: ʕwḏ→ʕwd, ḥfy→ʕfy, mbl→ybl, rwġ→rwx, xrbš→xrmš

### 4.2 Uncertain Entries (58 entries)
- Marked with `???` in source
- **Status:** ✅ Flagged in JSON output with `"uncertain": true`

### 4.3 Detransitive Sections (525 entries)
- Pattern 1: `<font size="4" style="font-size: 16pt">Detransitive` (4)
- Pattern 2: `<p><span>Detransitive</span></p>` (521)
- **Status:** ✅ Both patterns recognized

### 4.4 Homonyms (130 roots, 253 total entries)

#### Legitimate Homonyms (Different Etymologies)
- **ʔmr**: 2 entries (MEA vs. Arab.)
- **dr**: 2 entries (MEA vs. none)
- **fḏ**: 2 entries (different Arab. sources)

#### False Homonyms (German Glosses)
- **st**: 28 entries (GERMAN GLOSSES!)
- **gr**: 13 entries (GERMAN GLOSSES!)
- **tr**: 13 entries (GERMAN GLOSSES!)

**Issue:** BUG-001 pollutes homonym statistics.

---

## 5. Parser Bugs

### BUG-001: German Glosses Mistaken for Roots
- **Severity:** 🔴 CRITICAL
- **Affected Entries:** ~64 false positives
- **Impact:** Parser gets 1632 verbs instead of 1696
- **Location:** Parser line 79-80 (German gloss filter)
- **Fix:** Update filter to check ONLY special Turoyo characters

### BUG-002: Homonym Numbering Without Etymology Differences
- **Severity:** 🟡 MEDIUM
- **Issue:** Parser numbers homonyms even when they have same/missing etymology
- **Example:** "str" entries numbered 1-6 despite all having `None` etymology
- **Fix:** Only number homonyms with genuinely different etymologies
- **Note:** This is partly caused by BUG-001 (German glosses with no etymology)

---

## 6. Recommendations

### Priority 1: CRITICAL
**Fix German Gloss Filter**
- Update filter to check ONLY special Turoyo characters (ʔʕġǧḥṣštṭḏṯẓāēīūə)
- Exclude common Latin letters that appear in both languages
- Expected outcome: Extract exactly 1,696 verbs

### Priority 2: HIGH
**Add Validation Test**
```python
assert len(verbs) == 1696, f'Expected 1696 verbs, got {len(verbs)}'
```
- Fail parsing if count doesn't match expected total
- Prevents silent regressions

### Priority 3: MEDIUM
**Improve Homonym Detection**
- Only number homonyms with DIFFERENT etymologies
- Current logic numbers all duplicates, including those with `None` etymology
- This obscures genuine homonyms

### Priority 4: LOW
**Add Pattern Documentation**
- Comment each pattern explaining why it exists
- Document the `<font>` optional fix (247-verb bug)
- Explain the 3 stem header patterns
- Document German gloss filter purpose

---

## 7. Validation Checklist

- ✅ Root patterns: All 1,696 entries matched
- ✅ Stem patterns: All variations covered (3 patterns)
- ✅ Etymology parsing: All formats handled correctly
- ✅ Cross-references: Detected and processed (7 entries)
- ✅ Uncertain entries: Flagged correctly (58 entries)
- ✅ Detransitive sections: Both patterns recognized (525 entries)
- ❌ German gloss filter: FAILING - causes 64 false positives
- ⚠️  Homonym numbering: WORKING but polluted by BUG-001

---

## 8. Test Cases for Fixes

### Test Case 1: German Gloss Filter
```python
test_cases = [
    ("stöhnen;", False),      # Should NOT match (German)
    ("stampfen;", False),     # Should NOT match (German)
    ("studieren;", False),    # Should NOT match (German)
    ("ʔbʕ", True),            # Should match (Turoyo)
    ("ʕmr 1", True),          # Should match (Turoyo with number)
    ("mṭaṣər", True),         # Should match (Turoyo with emphatic)
]
```

### Test Case 2: Total Count
```python
def test_total_verbs(parser):
    verbs = parser.parse_all()
    assert len(verbs) == 1696, f"Expected 1696, got {len(verbs)}"
```

### Test Case 3: Homonym Quality
```python
def test_homonym_numbering(parser):
    # ʔmr should be numbered (different etymologies)
    assert 'ʔmr 1' in [v['root'] for v in parser.verbs]
    assert 'ʔmr 2' in [v['root'] for v in parser.verbs]

    # st should NOT be numbered (German glosses)
    assert 'st 1' not in [v['root'] for v in parser.verbs]
```

---

## 9. Files Generated

1. **data/validation/source_analysis_report.json**
   - Complete technical analysis in JSON format
   - All pattern counts and statistics
   - Bug details and recommendations

2. **data/validation/pattern_samples.html**
   - Visual representation of all patterns
   - Side-by-side comparison of correct vs. buggy patterns
   - Color-coded status indicators

3. **data/validation/ANALYSIS_SUMMARY.md** (this file)
   - Executive summary and detailed findings
   - Implementation recommendations
   - Test cases for validation

---

## Conclusion

The parser successfully identifies ALL structural patterns in the source HTML (1,696 root entries, all stem variations, etymologies, etc.), but a critical bug in the German gloss filter causes 64 false positives.

**Action Required:** Fix the German gloss filter to check ONLY special Turoyo characters, which will result in the correct extraction of exactly 1,696 verbs.

**Estimated Fix Time:** 15 minutes
**Risk Level:** Low (filter is isolated, well-defined fix)
**Testing Required:** Verify total count = 1,696 after fix
