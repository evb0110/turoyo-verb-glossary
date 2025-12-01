# Issue #2: Detransitive Label Not Recognized - Executive Summary

## Problem

The parser fails to capture stem labels/glosses that start with "Detransitive" and contain parenthetical text (e.g., "Detransitive (???)"). These labels are incorrectly treated as stem headers instead of being captured as `label_gloss_tokens`.

## Affected Verbs

**Only 2 verbs affected:**

1. **str** (Stem II)
   - File: `5. q,r,s,ṣ.docx`, line 1938
   - Label: `Detransitive (???)`
   - Structure:
     ```
     II: msatər/misatər
     Detransitive (???)           ← Should be label for Stem II
     [TABLE: Preterit examples]
     ```

2. **zqf 2** (Stem II)
   - File: `7. v, w, x, y, z, ž.docx`, line 667
   - Label: `Detransitive (it must belong to the previous root - SL)`
   - Structure:
     ```
     II: mzaqafle/mzaqəf
     beklatschen;
     Detransitive (it must belong to the previous root - SL)  ← Should be additional label
     ```

## Root Cause

**File:** `parser/parse_docx_production.py`
**Line:** 152

```python
if text.startswith('Detransitive'):
    return True
```

This code treats ANY text starting with "Detransitive" as a stem header, including:

- ✓ `Detransitive` - Correct (is a stem header for standalone Detransitive stems)
- ✗ `Detransitive (???)` - Wrong (is a label/gloss, not a stem header)

**Impact on gloss extraction:**
When the parser looks ahead for a gloss after "II: msatər/misatər", it encounters "Detransitive (???)", calls `is_stem_header()`, gets `True`, and **breaks** without capturing the label.

## Solution

**Change line 152 from:**

```python
if text.startswith('Detransitive'):
    return True
```

**To:**

```python
if text == 'Detransitive':
    return True
```

## Rationale

- **Precise matching:** Only standalone "Detransitive" is a stem header
- **Consistent pattern:** Matches existing code for "Action Noun" and "Infinitiv" (line 156)
- **Minimal risk:** Only 2 verbs affected, both will be fixed correctly
- **No side effects:** 351 existing "Detransitive" stems will continue to work

## Testing

### Before Fix

```bash
python3 -c "import json; \
data = json.load(open('server/assets/verbs/str.json')); \
stem2 = [s for s in data['stems'] if s['stem'] == 'II'][0]; \
print('label_gloss_tokens' in stem2)"
```

Output: `False`

### After Fix

```bash
python3 parser/parse_docx_production.py
cp .devkit/analysis/docx_v2_verbs/str.json server/assets/verbs/

python3 -c "import json; \
data = json.load(open('server/assets/verbs/str.json')); \
stem2 = [s for s in data['stems'] if s['stem'] == 'II'][0]; \
print(stem2.get('label_gloss_tokens'))"
```

Expected: `[{'italic': False, 'text': 'Detransitive (???)'}]`

## Expected Results

- **str** Stem II: Will have `label_gloss_tokens: [{'italic': False, 'text': 'Detransitive (???)'}]`
- **zqf 2** Stem II: Will capture the note as additional label text
- **All other verbs:** No changes (351 "Detransitive" stems remain correct)
- **Parser stats:** `separate_glosses_captured` counter will increase by 2

## Verification Checklist

- [ ] Change line 152 in `parser/parse_docx_production.py`
- [ ] Run parser: `python3 parser/parse_docx_production.py`
- [ ] Check str.json has label for Stem II
- [ ] Check zqf_2.json (or similar filename) has label
- [ ] Deploy to production: `cp .devkit/analysis/docx_v2_verbs/*.json server/assets/verbs/`
- [ ] Verify on website: str Stem II shows "Detransitive (???)" label
