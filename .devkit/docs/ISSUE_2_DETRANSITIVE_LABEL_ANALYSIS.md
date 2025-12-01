# Issue #2: Detransitive Label Not Recognized - Complete Analysis

## Problem Summary

The "Detransitive (???)" label for Stem II in the verb "str" is not being captured and displayed on the website. This affects the presentation of stem subcategory information.

## Source Data Structure (DOCX)

File: `.devkit/new-source-docx/5. q,r,s,ṣ.docx`

```
[1936] II: msatər/misatər                    ← Stem II header with forms
[1937] (empty paragraph)
[1938] Detransitive (???)                     ← GLOSS/LABEL for Stem II (NOT CAPTURED!)
[1939] TABLE: Preterit | nafəq msatər tamo...
[1941] TABLE: Infectum | uʕdo kle k-misatər...
[1942] III: mastalle/mastər                   ← Stem III header
[1943] bedecken, beschützen, bewahren, behüten; ← Gloss for Stem III (CAPTURED!)
[1944] TABLE: Preterit | ...
...
[1952] Detransitive                           ← SEPARATE STEM header
[1953] TABLE: Preterit | mtastər aʕle...
[1955] TABLE: Infectum | k-lozəm mitastər...
```

### Key Observations

1. **Two Different "Detransitive" Uses:**
   - Line 1938: `Detransitive (???)` - Gloss/label/subcategory for Stem II
   - Line 1952: `Detransitive` - Standalone stem header (like I, II, III, Pa., Af.)

2. **Expected vs Actual Behavior:**
   - **Expected:** "Detransitive (???)" should be captured as `label_gloss_tokens` for Stem II
   - **Actual:** "Detransitive (???)" is treated as a stem header and skipped

## Current Parser Behavior

### Relevant Code Sections

#### 1. `is_stem_header()` Function (Line 144-175)

```python
def is_stem_header(self, para, next_elem_is_table=False):
    if not para.text.strip():
        return False

    text = para.text.strip()
    has_stem = re.match(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', text)

    if not has_stem:
        if text.startswith('Detransitive'):  # ← LINE 152: THE BUG!
            return True
        ...
    return True
```

**Problem:** This function returns `True` for ANY text starting with "Detransitive", including:

- `Detransitive` ✓ (correct - is a stem header)
- `Detransitive (???)` ✗ (incorrect - is a gloss, not a stem header)

#### 2. Gloss Extraction Logic (Lines 1904-1936)

```python
# BUGFIX V2.1.8: Check for separate paragraph gloss
if not gloss_text:
    for j in range(idx + 1, min(idx + 3, len(elements))):
        if elements[j][0] == 'para':
            next_p = elements[j][1]
            next_text = next_p.text.strip()

            # Skip empty paragraphs
            if not next_text:
                continue

            # Stop if next para is another stem header
            if self.is_stem_header(next_p, False):  # ← LINE 1917: BREAKS HERE!
                break

            # This paragraph is likely a separate gloss
            gloss_tokens = self.tokenize_paragraph_runs(next_p, next_text)
            if gloss_tokens:
                current_stem['label_gloss_tokens'] = gloss_tokens
                self.consumed_para_indices.add(j)
            break
```

**Problem Flow for "str" Stem II:**

1. Parser encounters `II: msatər/misatər` (no gloss on same line)
2. Looks ahead for separate gloss paragraph
3. Skips empty paragraph at index 1937
4. Encounters `Detransitive (???)` at index 1938
5. Calls `is_stem_header(para)` which returns `True` (because text starts with "Detransitive")
6. **Breaks out of loop** without capturing the gloss!

## Current Output (JSON)

```json
{
  "stem": "II",
  "forms": ["msatər", "misatər"],
  "conjugations": { ... }
  // ❌ NO label_gloss_tokens field!
}
```

**Expected Output:**

```json
{
  "stem": "II",
  "forms": ["msatər", "misatər"],
  "conjugations": { ... },
  "label_gloss_tokens": [
    {
      "italic": false,
      "text": "Detransitive (???)"
    }
  ]
}
```

## Scope of Issue

### Statistics

- **Total stems missing `label_gloss_tokens`:** 351 (out of ~1,844 stems)
- **Breakdown:**
  - Most are "Detransitive" stems (standalone stems like the one at line 1952)
  - Some are regular stems (I, II, III) with separate gloss paragraphs containing "Detransitive (...)" labels

### Affected Verbs

Sample of verbs with stems missing glosses:

```
bdl         Stem Detransitive    forms=[]
blbl        Stem Detransitive    forms=[]
bšbš        Stem I               forms=['mbašbəš', 'mibašbəš']
str         Stem II              forms=['msatər', 'misatər']  ← Our example!
```

## Root Cause Analysis

The bug is in the `is_stem_header()` function at **line 152**:

```python
if text.startswith('Detransitive'):
    return True
```

**Why this is wrong:**

- It treats both `Detransitive` AND `Detransitive (???)` as stem headers
- In reality:
  - `Detransitive` alone = stem header ✓
  - `Detransitive (...)` = gloss/label for a regular stem (I, II, III) ✗

## Proposed Solution

### Option 1: Strict Matching (Recommended)

Only treat standalone "Detransitive" as a stem header:

```python
# Line 152 - Replace this:
if text.startswith('Detransitive'):
    return True

# With this:
if text == 'Detransitive':
    return True
```

**Pros:**

- Simple, clear, precise
- Matches pattern for "Action Noun" and "Infinitiv" (line 156)
- Prevents false positives

**Cons:**

- None identified

### Option 2: Exclude Parenthetical Text

Check for parentheses after "Detransitive":

```python
# Line 152 - Replace with:
if text.startswith('Detransitive') and '(' not in text:
    return True
```

**Pros:**

- More flexible if there are other variations

**Cons:**

- Less precise than Option 1
- Could miss edge cases

### Option 3: Extract Label from Parenthetical

Recognize "Detransitive (...)" as a special gloss pattern:

```python
# In gloss extraction logic (before line 1917):
# Check if this is a detransitive label (not header)
if next_text.startswith('Detransitive') and '(' in next_text:
    # This is a label, not a header - capture it!
    gloss_tokens = self.tokenize_paragraph_runs(next_p, next_text)
    if gloss_tokens:
        current_stem['label_gloss_tokens'] = gloss_tokens
        self.consumed_para_indices.add(j)
    break
```

**Pros:**

- Explicitly handles the detransitive label case
- Most robust solution

**Cons:**

- More complex
- Adds special-case logic

## Recommended Solution

**Use Option 1 (strict matching)** at line 152:

```python
if text == 'Detransitive':
    return True
```

This is the simplest, clearest fix that:

- Correctly identifies standalone "Detransitive" stems
- Allows "Detransitive (???)" to be captured as gloss text
- Matches the existing pattern for "Action Noun" and "Infinitiv"

## Similar Labels in Source

Other potential subcategory labels that might exist:

- "Transitive"
- "Reflexive"
- "Passive"
- "Middle Voice"
- Any label in the pattern: `<Category> (...)`

The strict matching solution will handle all of these correctly:

- Standalone labels → treated as stem headers
- Labels with parenthetical text → treated as glosses

## Testing Plan

After implementing the fix:

1. **Run the parser:**

   ```bash
   python3 parser/parse_docx_production.py
   ```

2. **Check str.json output:**

   ```bash
   python3 -c "import json; data = json.load(open('.devkit/analysis/docx_v2_verbs/str.json')); \
   stem2 = [s for s in data['stems'] if s['stem'] == 'II'][0]; \
   print(f\"Stem II gloss: {stem2.get('label_gloss_tokens', 'MISSING')}\")"
   ```

   Expected output:

   ```
   Stem II gloss: [{'italic': False, 'text': 'Detransitive (???)'}]
   ```

3. **Count fixed stems:**

   ```bash
   python3 -c "import json; from pathlib import Path; \
   missing = sum(1 for f in Path('.devkit/analysis/docx_v2_verbs').glob('*.json') \
   for s in json.load(open(f)).get('stems', []) if not s.get('label_gloss_tokens')); \
   print(f'Stems missing glosses: {missing}')"
   ```

   Expected: Should drop from 351 to fewer (exact number depends on how many have this pattern)

4. **Deploy to production:**

   ```bash
   cp .devkit/analysis/docx_v2_verbs/*.json server/assets/verbs/
   ```

5. **Verify on website:**
   - Navigate to str verb page
   - Check that Stem II displays "Detransitive (???)" label

## Files to Modify

1. **Parser:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/parser/parse_docx_production.py`
   - Line 152: Change `if text.startswith('Detransitive'):` to `if text == 'Detransitive':`

## Expected Impact

- **Verbs affected:** Unknown (need to analyze how many have "Detransitive (...)" pattern)
- **Data quality improvement:** Capture previously missing stem subcategory labels
- **User experience:** Better documentation of stem types and usage patterns
