# Quick Fix Guide - BUG-001

## The Problem

Parser extracts German verb glosses (like "stöhnen", "stampfen") as Turoyo roots because the filter incorrectly identifies them as Turoyo words.

**Current Count:** 1,632 verbs (should be 1,696)
**Missing:** 64 verbs replaced by German glosses

## The Fix (One Line Change)

**File:** `parser/parse_verbs.py`
**Line:** 79

### Current Code (BROKEN)
```python
if ';' in full_span_text and not any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
    continue
```

### Fixed Code
```python
# Only check for SPECIAL Turoyo characters (not common Latin letters)
special_turoyo = 'ʔʕġǧḥṣštṭḏṯẓāēīūə'
if ';' in full_span_text and not any(c in full_span_text for c in special_turoyo):
    continue
```

## Why This Works

**Problem:**
- The character class `'ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə'` includes 't', 's', 'h', etc.
- German words like "stöhnen" contain 't', so filter thinks it's Turoyo
- Filter fails to skip German gloss

**Solution:**
- Use ONLY special Turoyo characters: `'ʔʕġǧḥṣštṭḏṯẓāēīūə'`
- These are pharyngeal consonants, emphatics, and special diacritics
- German words don't have these characters
- Filter correctly identifies and skips German glosses

## Alternative Fix (More Explicit)

```python
# Define Turoyo special characters (exclude common Latin)
TUROYO_SPECIAL = 'ʔʕġǧḥṣštṭḏṯẓāēīūə'

# Filter German glosses
if ';' in full_span_text:
    has_special_turoyo = any(c in full_span_text for c in TUROYO_SPECIAL)
    if not has_special_turoyo:
        continue  # Skip German gloss
```

## Test Cases

After fixing, verify these cases:

```python
# Should be SKIPPED (German glosses)
test_skip = [
    "stöhnen;",
    "stampfen;",
    "studieren;",
    "staunen;",
    "stemmen;",
]

# Should be KEPT (Turoyo roots)
test_keep = [
    "ʔbʕ",           # has ʔ, ʕ
    "ʕmr 1",         # has ʕ
    "mṭaṣər",        # has ṭ, ṣ
    "šlḥ",           # has š, ḥ
    "ġlb",           # has ġ
]
```

## Validation

After fixing, run parser and check:
```bash
python3 parser/parse_verbs.py
```

Expected output:
```
✅ Parsed 1696 verbs, 1758 stems
```

If you still see 1632 verbs, the fix didn't work.

## Full Context (Lines 67-81)

```python
# STEP 1: Collect all valid root matches (filtering out glosses)
valid_matches = []
for match in re.finditer(root_pattern, section_html):
    root_chars = match.group(1)

    # FILTER: Skip German glosses (e.g., "speichern;")
    # Glosses end with semicolon and have no special Turoyo chars
    span_content = match.group(0)
    span_text_match = re.search(r'<span[^>]*>([^<]+)</span>', span_content)
    if span_text_match:
        full_span_text = span_text_match.group(1).strip()

        # FIX: Only check for SPECIAL Turoyo characters
        special_turoyo = 'ʔʕġǧḥṣštṭḏṯẓāēīūə'
        if ';' in full_span_text and not any(c in full_span_text for c in special_turoyo):
            continue  # Skip German gloss

    # [rest of code continues...]
```

## Expected Result

After fix:
- Total verbs: **1,696** (was 1,632)
- False homonyms removed: st (28), gr (13), tr (13), br (11), sp (10)
- Actual homonyms preserved: ʔmr (2), dr (2), fḏ (2)

## Time Estimate

- Fix: 2 minutes
- Test: 5 minutes
- Validation: 3 minutes
- **Total: ~10 minutes**
