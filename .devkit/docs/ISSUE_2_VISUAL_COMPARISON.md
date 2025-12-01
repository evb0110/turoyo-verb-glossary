# Issue #2: Visual Comparison - Detransitive Label

## Source vs Current vs Expected

### DOCX Source Structure

```
str (< MEA str cf. SL 1052...)

I: satər/sotər
Schutz finden, Zuflucht finden;        ← Gloss for Stem I ✓
[TABLE: Conjugations]

II: msatər/misatər
Detransitive (???)                      ← Gloss for Stem II ✗ NOT CAPTURED!
[TABLE: Conjugations]

III: mastalle/mastər
bedecken, beschützen, bewahren, behüten; ← Gloss for Stem III ✓
[TABLE: Conjugations]

Detransitive                            ← Separate stem header ✓
[TABLE: Conjugations]
```

### Current JSON Output (WRONG)

```json
{
  "root": "str",
  "stems": [
    {
      "stem": "I",
      "forms": ["satər", "sotər"],
      "label_gloss_tokens": [
        {
          "italic": false,
          "text": "Schutz finden, Zuflucht finden;"
        }
      ]
      // ✓ Gloss captured correctly
    },
    {
      "stem": "II",
      "forms": ["msatər", "misatər"],
      "conjugations": { ... }
      // ✗ NO label_gloss_tokens field!
      // ✗ Missing: "Detransitive (???)"
    },
    {
      "stem": "III",
      "forms": ["mastalle", "mastər"],
      "label_gloss_tokens": [
        {
          "italic": false,
          "text": "bedecken, beschützen, bewahren, behüten;"
        }
      ]
      // ✓ Gloss captured correctly
    },
    {
      "stem": "Detransitive",
      "forms": [],
      "conjugations": { ... }
      // ✓ Separate stem captured correctly
    }
  ]
}
```

### Expected JSON Output (CORRECT)

```json
{
  "root": "str",
  "stems": [
    {
      "stem": "I",
      "forms": ["satər", "sotər"],
      "label_gloss_tokens": [
        {
          "italic": false,
          "text": "Schutz finden, Zuflucht finden;"
        }
      ]
    },
    {
      "stem": "II",
      "forms": ["msatər", "misatər"],
      "label_gloss_tokens": [
        {
          "italic": false,
          "text": "Detransitive (???)"
        }
      ],
      // ✓ Label captured!
      "conjugations": { ... }
    },
    {
      "stem": "III",
      "forms": ["mastalle", "mastər"],
      "label_gloss_tokens": [
        {
          "italic": false,
          "text": "bedecken, beschützen, bewahren, behüten;"
        }
      ]
    },
    {
      "stem": "Detransitive",
      "forms": [],
      "conjugations": { ... }
    }
  ]
}
```

## Website Display Comparison

### Current Display (WRONG)

```
Stem II
msatər, misatər

Preteri
nafəq msatər tamo
'er ging und fand dort Zuflucht'
BS

Infectum
uʕdo kle k-misatər tamo
'jetzt ist er dort in Sicherheit'
BS
```

**Problem:** No subcategory label shown! Users don't know Stem II is detransitive.

### Expected Display (CORRECT)

```
Stem II
msatər, misatər
Detransitive (???)                    ← Label should appear here!

Preteri
nafəq msatər tamo
'er ging und fand dort Zuflucht'
BS

Infectum
uʕdo kle k-misatər tamo
'jetzt ist er dort in Sicherheit'
BS
```

**Benefit:** Users can see the grammatical category/usage information for the stem.

## Code Flow Comparison

### Current Behavior (BUG)

```
Parser encounters: "II: msatər/misatər"
  ↓
Extract forms: ["msatər", "misatər"]
  ↓
No gloss on same line → Look ahead
  ↓
Skip empty paragraph
  ↓
Encounter: "Detransitive (???)"
  ↓
Call is_stem_header("Detransitive (???)")
  ↓
Line 152: text.startswith('Detransitive') → TRUE ✗
  ↓
BREAK (thinking it's a new stem header) ✗
  ↓
Result: Stem II has NO label_gloss_tokens ✗
```

### Fixed Behavior (CORRECT)

```
Parser encounters: "II: msatər/misatər"
  ↓
Extract forms: ["msatər", "misatər"]
  ↓
No gloss on same line → Look ahead
  ↓
Skip empty paragraph
  ↓
Encounter: "Detransitive (???)"
  ↓
Call is_stem_header("Detransitive (???)")
  ↓
Line 152: text == 'Detransitive' → FALSE ✓
  ↓
CONTINUE (it's not a stem header) ✓
  ↓
Capture as gloss: tokenize_paragraph_runs(...) ✓
  ↓
Result: Stem II has label_gloss_tokens ✓
```

## The One-Line Fix

**File:** `parser/parse_docx_production.py`
**Line:** 152

### Before (WRONG)

```python
if text.startswith('Detransitive'):
    return True
```

### After (CORRECT)

```python
if text == 'Detransitive':
    return True
```

**Change:** `startswith` → `==`

**Impact:**

- ✓ Standalone "Detransitive" → Still treated as stem header
- ✓ "Detransitive (...)" → Now treated as gloss text
- ✓ Fixes 2 verbs: str, zqf 2
- ✓ No side effects on 351 existing Detransitive stems
