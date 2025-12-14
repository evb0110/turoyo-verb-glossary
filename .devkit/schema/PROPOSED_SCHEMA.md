# Proposed Updated Schema

Based on comprehensive analysis of all 1,498 verbs from DOCX source files.

**Principle:** Everything that doesn't fit structured fields goes to `notes`. No content loss.

---

## Complete TypeScript Interfaces

```typescript
// ============================================================
// EXAMPLE STRUCTURE
// ============================================================

interface IToken {
  kind: "turoyo" | "translation" | "ref" | "punct" | "note";
  value: string;
}

interface IExample {
  text: string; // Full example text (required)
  turoyo?: string; // Turoyo portions concatenated
  translations?: string[]; // German/English translations
  references?: string[]; // Reference citations (307, 24/35, SL 1138, etc.)
  notes?: string; // Editorial notes like [MT], [LTN], comments
  tokens?: IToken[]; // Optional: detailed tokenization for rich display
}

interface IExamples {
  meaningNumber?: number; // If examples are for a specific meaning
  items: IExample[];
}

// ============================================================
// CONJUGATION SHAPES
// ============================================================

type TShape =
  // Preterit family
  | "Preterit"
  | "Preterit Intransitive"
  | "Preterit Transitive"
  | "ko-Preterit"
  | "Preterit-wa"
  // Infectum family
  | "Infectum"
  | "Infectum-wa"
  // Imperativ
  | "Imperativ"
  // Participles (normalized canonical forms)
  | "Part act."
  | "Part. Pass."
  | "Active participle"
  | "Passive Participle"
  | "Past Participle"
  // Infinitiv
  | "Infinitiv"
  // Nouns
  | "Action noun"
  | "Nomen Actionis"
  | "Nomen Patiens"
  | "Nomen agentis";

// Parser should normalize variants:
// - "Preterite" → "Preterit"
// - "Infinitive" → "Infinitiv"
// - "Imperative" → "Imperativ"
// - "Part. act." / "Part. Act." / "Part Act." → "Part act."
// - "Part. pass." / "Part pass." → "Part. Pass."
// - "k-Preterit" → "ko-Preterit"
// - "Infectum - wa" → "Infectum-wa"
// - Remove newlines and other malformed content

interface IRow {
  shape: TShape;
  examples: IExamples[];
  notes?: string; // For uncertainty markers, annotations
}

// ============================================================
// MEANINGS
// ============================================================

interface IMeaning {
  meaningNumber: number; // 1, 2, 3...
  meaning: string; // The German/English gloss
  notes?: string; // Dialect annotations, uncertainty
}

// ============================================================
// STEM STRUCTURE
// ============================================================

type TStemNumber = "I" | "II" | "III" | "Detransitive";
// Note: Some sources use Roman numerals up to IV, V
// Pa., Af., Št., Šaf. are Aramaic stem notation - currently NOT in data
// but might be added for compatibility

interface IStem {
  stemNumber: TStemNumber;
  stemForms: string; // qayəm/qoyəm - the conjugation forms

  // Stem-level information
  gloss?: string; // Free-text stem gloss (not numbered)
  dialectNotes?: string; // (Kfarze), (Ilyas p.c.), etc.
  meanings?: IMeaning[]; // Numbered meanings: 1) wollen; 2) nötig sein

  // Conjugation tables
  transitive: IRow[]; // Main (transitive) conjugations
  detransitive?: IRow[]; // Detransitive variant conjugations

  // Idiomatic phrases associated with this stem
  idiomaticPhrases?: IExample[];

  // Catch-all for anything else
  notes?: string;
}

// ============================================================
// ETYMOLOGY STRUCTURE
// ============================================================

interface IEtymology {
  // Source language/variety
  provenance?: string; // Arab., Syr., MEA, Kurd., Turk., Pers., etc.

  // The source word/root
  sourceRoot?: string; // bdl, qfz, ydʕ (the lexeme in source language)

  // References
  references?: string[]; // ["Wehr 71-72", "SL 133", "DJBA 1118"]

  // Meaning in source language
  meaning?: string; // German/English gloss of source word

  // Special etymology types
  type?: "loan" | "cognate" | "denominal" | "unknown" | "see";

  // Catch-all for unstructured content
  notes?: string; // cf. references, uncertainty, comments
  raw?: string; // Original unprocessed text (for validation)
}

// ============================================================
// IDIOM STRUCTURE (at entry level)
// ============================================================

interface IIdiom {
  text: string; // The idiom or phrase
  translations?: string[]; // Translations
  meaningNumber?: number; // If numbered (1), (2)...
  stemReference?: TStemNumber; // If it references a specific stem
  notes?: string; // Annotations, comments
}

// ============================================================
// MAIN ENTRY STRUCTURE
// ============================================================

export interface IEntry {
  // Root/lemma
  lemma: string; // qbz, bdl, ʔḏʕ
  homonymNumber?: number; // 1, 2 for homonyms like bdy 1, bdy 2

  // Etymology (can be multiple with relationship)
  etymologies?: IEtymology[];
  etymologyRelationship?: "also" | "and"; // Relationship between multiple etymologies

  // Stems and conjugations
  stems?: IStem[];

  // Idiomatic expressions (at entry level)
  idioms?: IIdiom[];

  // Cross-references
  crossReference?: string; // → see qṭl

  // Metadata
  uncertain?: boolean; // Flag for entries needing review
  notes?: string; // Entry-level annotations
}
```

---

## Field Mapping: Current Parser → New Schema

| Current Field                     | New Field                    | Notes                   |
| --------------------------------- | ---------------------------- | ----------------------- |
| `root`                            | `lemma`                      | Rename                  |
| `root` (with number)              | `lemma` + `homonymNumber`    | Split                   |
| `etymology.etymons`               | `etymologies`                | Move array to top level |
| `etymology.etymons[].source`      | `etymologies[].provenance`   | Rename                  |
| `etymology.etymons[].source_root` | `etymologies[].sourceRoot`   | Rename                  |
| `etymology.etymons[].reference`   | `etymologies[].references[]` | Make array              |
| `etymology.etymons[].meaning`     | `etymologies[].meaning`      | Keep                    |
| `etymology.etymons[].notes`       | `etymologies[].notes`        | Keep                    |
| `etymology.etymons[].raw`         | `etymologies[].raw`          | Keep                    |
| `etymology.relationship`          | `etymologyRelationship`      | Move to top level       |
| `stems[].stem`                    | `stems[].stemNumber`         | Rename                  |
| `stems[].forms`                   | `stems[].stemForms`          | Join array to string    |
| `stems[].label_raw`               | `stems[].gloss`              | Rename                  |
| `stems[].conjugations`            | `stems[].transitive`         | Restructure             |
| `idioms`                          | `idioms`                     | Restructure to IIdiom[] |
| `cross_reference`                 | `crossReference`             | Rename (camelCase)      |
| `uncertain`                       | `uncertain`                  | Keep                    |

---

## Parser Normalization Rules

### Shape Normalization

```python
SHAPE_NORMALIZATION = {
    'Preterite': 'Preterit',
    'Infinitive': 'Infinitiv',
    'Imperative': 'Imperativ',
    'Part. act.': 'Part act.',
    'Part. Act.': 'Part act.',
    'Part Act.': 'Part act.',
    'Part. pass.': 'Part. Pass.',
    'Part pass.': 'Part. Pass.',
    'Pass. Part.': 'Part. Pass.',
    'k-Preterit': 'ko-Preterit',
    'Infectum - wa': 'Infectum-wa',
    'Infeсtum': 'Infectum',  # Cyrillic с → Latin c
}

# Remove malformed content
def normalize_shape(shape: str) -> str:
    shape = shape.replace('\n', ' ').strip()
    shape = re.sub(r'\s+', ' ', shape)
    return SHAPE_NORMALIZATION.get(shape, shape)
```

### Etymology Type Detection

```python
def detect_etymology_type(text: str) -> str:
    if text.startswith('<') or '< ' in text:
        return 'loan'
    if 'cf.' in text.lower():
        return 'cognate'
    if 'denom.' in text.lower():
        return 'denominal'
    if 'unknown' in text.lower():
        return 'unknown'
    if text.lower().startswith('see '):
        return 'see'
    return None
```

---

## Migration Strategy

1. **Phase 1:** Update parser to output new schema format
2. **Phase 2:** Add normalization for shapes and etymology types
3. **Phase 3:** Validate all 1,498 entries against new schema
4. **Phase 4:** Update frontend to consume new format

---

## Validation Checklist

After migration, verify:

- [ ] All 4 stem types represented (I, II, III, Detransitive)
- [ ] All shapes normalized to canonical forms
- [ ] Etymology arrays with relationships preserved
- [ ] Stem glosses captured in `gloss` field
- [ ] Editorial notes ([MT], [LTN]) in `notes` fields
- [ ] Idioms structured with translations
- [ ] No content loss (compare token counts)
