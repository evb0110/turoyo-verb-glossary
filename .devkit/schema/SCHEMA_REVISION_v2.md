# Schema Revision v2 - Based on Clarifications

**Date:** 2025-12-14

---

## Key Clarifications Applied

### 1. Detransitive is NOT a Separate Stem

**Clarification:** Each stem (I, II, III) can have an optional detransitive part. The proposed schema's structure is CORRECT:

```typescript
interface IStem {
  stemNumber: TStemNumber; // 'I' | 'II' | 'III' only
  transitive: IRow[]; // Main conjugations
  detransitive?: IRow[]; // Optional detransitive conjugations
}
```

**Current Parser Bug:** The parser incorrectly outputs "Detransitive" as a separate stem entry. This needs to be fixed - detransitive conjugations should be nested inside their parent stem.

**Example of CORRECT structure:**

```json
{
  "stems": [
    {
      "stemNumber": "II",
      "stemForms": "mbadele/mbadəl",
      "transitive": [
        { "shape": "Preterit", "examples": [...] },
        { "shape": "Infectum", "examples": [...] }
      ],
      "detransitive": [
        { "shape": "Preterit", "examples": [...] },
        { "shape": "Infectum", "examples": [...] }
      ]
    }
  ]
}
```

**Example of WRONG structure (current parser):**

```json
{
  "stems": [
    { "stem": "II", "conjugations": {...} },
    { "stem": "Detransitive", "conjugations": {...} }  // WRONG!
  ]
}
```

---

### 2. TShape Normalization - Confirmed

Parser should normalize all shape variants to canonical forms.

---

### 3. Etymology Simplified

**Clarification:** Keep etymology simple. Extract only `provenance` (source language) for filtering, keep everything else as plain text.

```typescript
interface IEtymology {
  provenance?: string; // Arab, Syr, MEA, Kurd, Turk, Pers, etc. (for filtering)
  text: string; // Full etymology text as-is
  notes?: string; // Additional notes if needed
}
```

**Provenance extraction patterns:**

- `< Arab.` → provenance: "Arab"
- `< MEA` → provenance: "MEA" (Middle Eastern Aramaic)
- `< Syr.` → provenance: "Syr" (Syriac)
- `< Kurd.` → provenance: "Kurd"
- `< Turk.` → provenance: "Turk"
- `< Pers.` → provenance: "Pers"
- `cf. Arab.` → provenance: "Arab" (comparative)
- `denom.` → provenance: "denom" (denominal)
- `unknown` → provenance: null

**No need to parse:** source_root, reference, meaning separately. These stay in `text`.

---

### 4. Stem-Level Glosses → Notes

Dialect annotations, glosses, and other stem-level content go to `IStem.notes`.

```typescript
interface IStem {
  // ...
  notes?: string; // Glosses, dialect notes (Kfarze), uncertainty, etc.
}
```

---

### 5. Cross-References - Separate Field

Already in schema as `crossReference`. Parser needs to extract `→` patterns.

```typescript
interface IEntry {
  crossReference?: string; // → see qṭl
}
```

---

### 6. Idioms - Needs Restructuring

Move from plain strings to structured format.

```typescript
interface IIdiom {
  text: string; // The idiom/phrase
  translation?: string; // German/English translation
  notes?: string; // Annotations, uncertainty
}

interface IEntry {
  idioms?: IIdiom[];
}
```

---

### 7. Notes at Every Level

**Principle:** Anything that doesn't fit structured fields goes to `notes`. No content loss.

```typescript
interface IExample {
  text: string;
  translations?: string[];
  references?: string[];
  notes?: string; // ← catch-all
}

interface IRow {
  shape: TShape;
  examples: IExamples[];
  notes?: string; // ← catch-all
}

interface IStem {
  stemNumber: TStemNumber;
  stemForms: string;
  meanings?: IMeaning[];
  transitive: IRow[];
  detransitive?: IRow[];
  idiomaticPhrases?: IExample[];
  notes?: string; // ← catch-all (glosses, dialect notes, etc.)
}

interface IEtymology {
  provenance?: string;
  text: string;
  notes?: string; // ← catch-all
}

interface IIdiom {
  text: string;
  translation?: string;
  notes?: string; // ← catch-all
}

interface IEntry {
  lemma: string;
  homonymNumber?: number;
  etymology?: IEtymology;
  stems?: IStem[];
  idioms?: IIdiom[];
  crossReference?: string;
  uncertain?: boolean;
  notes?: string; // ← catch-all
}
```

---

## Revised Complete Schema

```typescript
// ============================================================
// SHAPES (normalized)
// ============================================================

type TShape =
  | "Preterit"
  | "Preterit Intransitive"
  | "Preterit Transitive"
  | "ko-Preterit"
  | "Preterit-wa"
  | "Infectum"
  | "Infectum-wa"
  | "Imperativ"
  | "Part act."
  | "Part. Pass."
  | "Infinitiv"
  | "Action noun"
  | "Nomen Actionis"
  | "Nomen Patiens"
  | "Nomen agentis";

// Parser normalizes variants:
// Preterite → Preterit
// Infinitive → Infinitiv
// Imperative → Imperativ
// etc.

// ============================================================
// STEM NUMBER
// ============================================================

type TStemNumber = "I" | "II" | "III";
// Note: "Detransitive" is NOT a stem number!
// It's an optional part of each stem (IStem.detransitive)

// ============================================================
// EXAMPLES
// ============================================================

interface IExample {
  text: string; // Full example text
  translations?: string[]; // German/English translations
  references?: string[]; // Reference citations
  notes?: string; // Editorial notes [MT], [LTN], etc.
}

interface IExamples {
  meaningNumber?: number;
  items: IExample[];
}

// ============================================================
// CONJUGATION ROWS
// ============================================================

interface IRow {
  shape: TShape;
  examples: IExamples[];
  notes?: string;
}

// ============================================================
// MEANINGS
// ============================================================

interface IMeaning {
  meaningNumber: number;
  meaning: string;
  notes?: string;
}

// ============================================================
// STEMS
// ============================================================

interface IStem {
  stemNumber: TStemNumber; // 'I' | 'II' | 'III'
  stemForms: string; // qayəm/qoyəm

  meanings?: IMeaning[]; // Numbered meanings

  transitive: IRow[]; // Main conjugations
  detransitive?: IRow[]; // Optional detransitive conjugations

  idiomaticPhrases?: IExample[];

  notes?: string; // Glosses, dialect notes, etc.
}

// ============================================================
// ETYMOLOGY (simplified)
// ============================================================

interface IEtymology {
  provenance?: string; // Arab, Syr, MEA, Kurd, etc. (for filtering)
  text: string; // Full etymology as plain text
  notes?: string;
}

// ============================================================
// IDIOMS
// ============================================================

interface IIdiom {
  text: string;
  translation?: string;
  notes?: string;
}

// ============================================================
// ENTRY
// ============================================================

export interface IEntry {
  lemma: string; // qbz, bdl, ʔḏʕ
  homonymNumber?: number; // 1, 2 for homonyms

  etymology?: IEtymology; // Single etymology object

  stems?: IStem[]; // Array of stems (I, II, III)

  idioms?: IIdiom[]; // Idiomatic expressions

  crossReference?: string; // → see qṭl

  uncertain?: boolean; // Flag for uncertain entries

  notes?: string; // Entry-level notes
}
```

---

## Parser Changes Required

### Critical Fix: Detransitive Handling

Current parser outputs:

```json
{ "stems": [{ "stem": "II" }, { "stem": "Detransitive" }] } // WRONG
```

Must change to:

```json
{"stems": [{"stemNumber": "II", "transitive": [...], "detransitive": [...]}]}  // CORRECT
```

**Logic:**

1. When encountering "Detransitive" header in DOCX, don't create new stem
2. Instead, append conjugations to previous stem's `detransitive` array
3. Track current stem context while parsing

### Etymology Extraction

```python
def extract_provenance(text: str) -> str | None:
    patterns = [
        (r'<\s*(Arab\.?)', 'Arab'),
        (r'<\s*(Syr\.?)', 'Syr'),
        (r'<\s*(MEA)', 'MEA'),
        (r'<\s*(Kurd\.?)', 'Kurd'),
        (r'<\s*(Turk\.?)', 'Turk'),
        (r'<\s*(Pers\.?)', 'Pers'),
        (r'cf\.\s*(Arab\.?)', 'Arab'),
        (r'cf\.\s*(Syr\.?)', 'Syr'),
        (r'cf\.\s*(MEA)', 'MEA'),
        (r'denom\.', 'denom'),
    ]
    for pattern, provenance in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return provenance
    if 'unknown' in text.lower():
        return None
    return None
```

### Shape Normalization

```python
SHAPE_MAP = {
    'Preterite': 'Preterit',
    'Infinitive': 'Infinitiv',
    'Imperative': 'Imperativ',
    'Part. act.': 'Part act.',
    'Part. Act.': 'Part act.',
    'Part pass.': 'Part. Pass.',
    'k-Preterit': 'ko-Preterit',
    'Infectum - wa': 'Infectum-wa',
}

def normalize_shape(shape: str) -> str:
    shape = shape.replace('\n', ' ').strip()
    return SHAPE_MAP.get(shape, shape)
```

### Cross-Reference Extraction

```python
def extract_cross_reference(text: str) -> str | None:
    match = re.search(r'→\s*([^\s,;]+)', text)
    if match:
        return match.group(1)
    return None
```

---

## Validation After Parser Update

1. **No stems with stemNumber='Detransitive'** - All detransitive content should be in parent stem
2. **All shapes normalized** - No variant spellings
3. **Etymology has provenance extracted** - For filtering capability
4. **Cross-references populated** - 7+ entries should have values
5. **Notes fields used** - No content loss from complex structures
