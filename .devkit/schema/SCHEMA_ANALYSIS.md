# Schema Validation Analysis

**Date:** 2025-12-14
**Analyzed:** All 1,498 verb entries from 7 DOCX source files
**Reference:** [GitHub Issue #6](https://github.com/evb0110/turoyo-verb-glossary/issues/6)

---

## Executive Summary

The proposed `IEntry` schema in `/schema/IEntry.ts` requires modifications to capture all data variations found in the DOCX source files. This analysis identifies **7 major gaps** and proposes solutions that ensure **no content loss** by using `notes` fields as fallback.

---

## 1. Stem Type Expansion Required

### Problem

The schema defines:

```typescript
type TStemNumber = "I" | "II" | "III";
```

But the DOCX data contains **4 stem types**:

| Stem Type    | Count | Percentage |
| ------------ | ----- | ---------- |
| I            | 1,003 | 43.4%      |
| Detransitive | 502   | 21.7%      |
| II           | 494   | 21.4%      |
| III          | 311   | 13.5%      |

### Recommendation

```typescript
type TStemNumber = "I" | "II" | "III" | "Detransitive";
```

**Note:** The schema's `transitive`/`detransitive` distinction inside IStem is a different concept. In the DOCX data, "Detransitive" appears as a **separate stem entry**, not as a sub-section of another stem. The schema's IStem.detransitive field may still be useful for verbs that have both transitive and detransitive forms within a single stem.

---

## 2. Conjugation Shape Normalization Required

### Problem

The schema defines 11 TShape values:

```typescript
type TShape =
  | "Preterit"
  | "Preterit Intransitive"
  | "ko-Preterit"
  | "Preterit-wa"
  | "Infectum"
  | "Infectum-wa"
  | "Imperativ"
  | "Part act."
  | "Part. Pass."
  | "Infinitiv"
  | "Action noun";
```

The DOCX data contains **41 unique shape names**. Many are spelling/formatting variations:

### High-frequency shapes (in schema) - 3,762 occurrences (94%)

| Shape                 | Count | Status    |
| --------------------- | ----- | --------- |
| Infectum              | 1,300 | In schema |
| Preterit              | 1,201 | In schema |
| Imperativ             | 327   | In schema |
| Infectum-wa           | 324   | In schema |
| Preterit Intransitive | 215   | In schema |
| Part. Pass.           | 199   | In schema |
| Infinitiv             | 182   | In schema |
| Part act.             | 110   | In schema |
| Preterit-wa           | 88    | In schema |
| ko-Preterit           | 27    | In schema |

### Variant shapes requiring normalization (6%)

#### Spelling variations (normalize to canonical form):

| Found         | Count | Normalize To                       |
| ------------- | ----- | ---------------------------------- |
| Preterite     | 17    | Preterit                           |
| Infinitive    | 12    | Infinitiv                          |
| Imperative    | 11    | Imperativ                          |
| Part. act.    | 11    | Part act.                          |
| Part. Act.    | 9     | Part act.                          |
| Part. pass.   | 5     | Part. Pass.                        |
| Infectum - wa | 4     | Infectum-wa                        |
| Part pass.    | 2     | Part. Pass.                        |
| k-Preterit    | 1     | ko-Preterit                        |
| Infeсtum      | 1     | Infectum (Cyrillic 'с' corruption) |

#### Additional shapes (add to schema):

| Shape           | Count | Description               |
| --------------- | ----- | ------------------------- |
| Nomen Patiens   | 10    | Latin grammatical term    |
| Nomen Actionis  | 8     | Latin grammatical term    |
| Past Participle | 2     | Alternate participle form |
| Nomen agentis   | 1     | Latin grammatical term    |

#### Malformed entries (fix in parser):

| Found                               | Count | Issue                    |
| ----------------------------------- | ----- | ------------------------ |
| Preterit\nIntransitive              | 1     | Newline in shape name    |
| Preterite\nTransitive               | 1     | Newline in shape name    |
| Infectum + Infectum-wa              | 1     | Merged shapes            |
| Infectum and Infectum-wa            | 1     | Merged shapes            |
| Infectum (???)                      | 1     | Uncertainty marker       |
| Preterit Intransitive\n the rest... | 1     | Annotation in shape name |

### Recommendation

Update TShape and add normalization in parser:

```typescript
type TShape =
  | "Preterit"
  | "Preterit Intransitive"
  | "ko-Preterit"
  | "Preterit-wa"
  | "Preterit Transitive" // NEW
  | "Infectum"
  | "Infectum-wa"
  | "Imperativ"
  | "Part act."
  | "Part. Pass."
  | "Active participle"
  | "Passive Participle"
  | "Past Participle" // EXPANDED
  | "Infinitiv"
  | "Action noun"
  | "Nomen Actionis"
  | "Nomen Patiens"
  | "Nomen agentis"; // EXPANDED
```

---

## 3. Etymology Structure Mismatch

### Problem

The proposed schema:

```typescript
interface IEtymology {
  provenance: string; // Arab
  source: string; // qfz
  references: string[]; // Wehr 1046-1047
  meaning: string;
  notes: string;
}
```

The DOCX data has more complex patterns:

| Pattern          | Count | Description                                |
| ---------------- | ----- | ------------------------------------------ |
| Fully structured | 1,138 | source + source_root + reference + meaning |
| Notes-only       | 81    | Only notes/raw text, no structure          |
| Raw-only         | 105   | Unstructured etymology text                |
| No etymology     | 198   | No etymology at all                        |
| Multiple etymons | 24    | Array of 2+ etymologies with relationship  |

### Current parsed structure (from parser):

```json
{
  "etymology": {
    "etymons": [
      {
        "source": "Arab.",
        "source_root": "bdl",
        "reference": "Wehr 71-72",
        "meaning": "verändern, umändern"
      }
    ],
    "relationship": "also" // or "and"
  }
}
```

### Missing in proposed schema:

1. **`source_root`** field - The lexeme in the source language (e.g., "bdl" from Arabic)
2. **`etymons[]` array** - Support for multiple etymologies
3. **`relationship`** field - "also" or "and" connecting multiple etymons
4. **`raw`** field - Fallback for unstructured content

### Example problematic entries:

**Multi-etymon (šyk.json):**

```
(see DJBA 1118 šwk 'to attach, connect', also metaphorically)
```

Needs array + relationship.

**cf. references (byz.json):**

```
(< MEA bzz, SL 133: to plunder; cf. Barwar byz, Khan 2008 1115: pour; cf. Kinderib bzz...)
```

Multiple comparative references in single string.

**Denominal (šrqm):**

```
(denom. RW 502 šaqmo 'Feige, Ohrfeige'+r; cf. MEA SL 1598...)
```

Special etymology type.

### Recommendation

```typescript
interface IEtymology {
  provenance?: string; // Arab, Syr, Kurd, etc.
  sourceRoot?: string; // qfz (the actual root/lexeme)
  references?: string[]; // Wehr 1046-1047
  meaning?: string; // springen
  notes?: string; // Everything that doesn't fit above
  raw?: string; // Original unprocessed text (for debugging)
}

interface IEntry {
  // ...
  etymologies?: IEtymology[]; // Array to support multiple
  etymologyRelationship?: "also" | "and"; // Relationship between etymons
  // ...
}
```

---

## 4. Stem-Level Glosses/Meanings Missing

### Problem

The schema has `IStem.meanings?: IMeaning[]` but the DOCX data often has **free-text glosses** at stem level that aren't numbered meanings.

### Found in DOCX (80 examples):

```
II: mʔadəb/miʔadəb  to teach (by punushment)
Detransitive: (Kfarze)
I: (šġile)/šoġəl
Detransitive: begraben werden
```

These are stem-level annotations that don't fit `IMeaning`:

- Dialect annotations: `(Kfarze)`, `(Ilyas p.c.)`
- Uncertainty: `(???)`
- Form variants: `(It seems that the second stem...)`
- Free glosses without number: `begraben werden`

### Current parser output:

```json
{
  "stem": "II",
  "forms": ["mʔadəb", "miʔadəb"],
  "label_raw": "to teach (by punushment)"
}
```

### Recommendation

Add to IStem:

```typescript
interface IStem {
  stemNumber: TStemNumber;
  stemForms: string; // qayəm/qoyəm
  gloss?: string; // Free-text stem gloss (NEW)
  dialectNotes?: string; // (Kfarze), (Ilyas p.c.) (NEW)
  meanings?: IMeaning[]; // Numbered meanings
  // ...
}
```

---

## 5. Example/Token Structure Differences

### Problem

The proposed schema:

```typescript
interface IExample {
  text: string;
  translations?: string[];
  references?: string[];
  notes?: string;
}
```

The current parser produces richer structure with tokenized content:

```json
{
  "turoyo": "mamṭele barṯo d-u=malko...",
  "translations": ["er nahm die Königstochter..."],
  "references": ["307", "94/24"],
  "tokens": [
    { "kind": "ref", "value": "1" },
    { "kind": "turoyo", "value": " mamṭele barṯo..." },
    { "kind": "translation", "value": "'er nahm...'" },
    { "kind": "note", "value": "[MT]" }
  ],
  "text": "1) mamṭele barṯo d-u=malko..."
}
```

### Token kinds found:

| Kind        | Count  | Description                      |
| ----------- | ------ | -------------------------------- |
| turoyo      | 28,807 | Turoyo text spans                |
| punct       | 27,054 | Punctuation                      |
| ref         | 13,802 | Reference citations              |
| translation | 7,632  | German translations              |
| note        | 514    | Editorial notes like [MT], [LTN] |

### Notes found (261 verbs):

| Note  | Meaning                          |
| ----- | -------------------------------- |
| [MT]  | Maroẓ-Talay source               |
| [LTN] | Source annotation                |
| [ML]  | Source annotation                |
| [мой] | Editor's personal note (Russian) |

### Recommendation

The proposed schema is simpler but loses token structure. Options:

1. **Keep simple** - Lose token-level detail, use `text` + `notes`
2. **Add tokens** - Include optional tokens array for rich parsing

```typescript
interface IExample {
  text: string; // Full example text
  turoyo?: string; // Turoyo portions only (NEW)
  translations?: string[];
  references?: string[];
  notes?: string; // Editorial notes like [MT]
  tokens?: IToken[]; // Optional detailed tokenization (NEW)
}

interface IToken {
  kind: "turoyo" | "translation" | "ref" | "punct" | "note";
  value: string;
}
```

---

## 6. Idioms Location and Structure

### Problem

The proposed schema puts idioms inside `IStem`:

```typescript
interface IStem {
  idiomaticPhrases?: IExample[];
}
```

The current data has idioms at **entry level**:

```json
{
  "root": "bdl",
  "stems": [...],
  "idioms": [
    "1) (aus)wechseln, (aus)tauschen, (ver)ändern;",
    "2) sich verändern (mit ruḥo)"
  ]
}
```

### Statistics:

- **1,387 verbs** have idioms (93%)
- Idioms are stored as **string arrays**
- Average 1-3 idioms per verb

### Idiom content patterns:

```
"zementieren;"                              // Simple gloss
"III: mankatle/mankət (Hierher? Etymology?)" // Stem reference + uncertainty
"beissen; III: mankatle/mankət"             // Mixed content
"kmč 1) To wither, 2) notes: ..."           // Numbered with notes
```

### Issue from GitHub discussion:

The idioms currently contain **mixed content** - sometimes glosses, sometimes references to other stems. This needs clarification:

- Should idioms be at entry level or stem level?
- Are some "idioms" actually just stem glosses that were misparsed?

### Recommendation

Keep at entry level with structured format:

```typescript
interface IEntry {
  // ...
  idioms?: IIdiom[]; // Keep at entry level
}

interface IIdiom {
  text: string; // The idiom text
  translations?: string[]; // German translations
  stemReference?: TStemNumber; // If it refers to a specific stem
  notes?: string; // Annotations, uncertainty
}
```

---

## 7. Missing/Empty Fields

### Fields in data not in schema:

| Field                     | Description                  |
| ------------------------- | ---------------------------- |
| `uncertain`               | 8 verbs flagged as uncertain |
| `stem._awaiting_forms`    | Parser processing flag       |
| `stem.label_gloss_tokens` | Tokenized stem gloss         |
| `stem.label_raw`          | Raw stem label text          |

### Recommendation

Add to IEntry:

```typescript
interface IEntry {
  // ...
  uncertain?: boolean; // Flag for uncertain entries
}
```

---

## 8. Cross-References

### Status

The schema includes `crossReference?: string` but **0 entries** in current data have cross-references.

The DOCX sources may contain cross-references that the parser doesn't currently extract (e.g., "→ see qṭl", "cf. XYZ").

### Recommendation

Keep the field, ensure parser extracts cross-references from patterns like:

- `→ see [root]`
- `See [root] [stem]`
- `cf. [root]`

---

## Summary of Required Schema Changes

### Must Fix (data loss otherwise):

1. Add `'Detransitive'` to TStemNumber
2. Add `sourceRoot` field to IEtymology
3. Support etymology arrays with relationship
4. Add stem-level `gloss` and `dialectNotes`
5. Add `notes` fallback everywhere

### Should Fix (normalization):

1. Normalize 30+ TShape variants to canonical forms
2. Fix malformed shape names in parser

### Consider:

1. Token-level example structure (complexity vs. value)
2. Idiom placement (entry vs. stem level)
3. Cross-reference extraction

---

## Proposed Updated Schema

See [PROPOSED_SCHEMA.md](./PROPOSED_SCHEMA.md) for the complete updated interface definitions.
