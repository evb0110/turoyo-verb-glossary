# Turoyo Verb Glossary - Data Structure Reference

Quick reference for working with the extracted JSON data.

## File: `data/verbs_final.json`

### Top Level

```json
{
  "verbs": [...],      // Array of 1,197 verb entries
  "metadata": {...}    // Dataset statistics
}
```

### Metadata Object

```json
{
  "total_verbs": 1197,
  "total_stems": 1730,
  "total_examples": 4237,
  "cross_references": 0,
  "uncertain_entries": 47,
  "parser_version": "3.0.0-final"
}
```

## Verb Entry Structure

### Complete Example

```json
{
  "root": "ʕbr",
  "etymology": {
    "source": "MEA",
    "source_root": "ʕbr",
    "reference": "SL 1064-1065",
    "meaning": "to pass, cross over; to pass through;"
  },
  "cross_reference": null,
  "uncertain": false,
  "stems": [
    {
      "binyan": "I",
      "forms": ["ʕabər", "ʕobər"],
      "conjugations": {
        "Preterit Intransitive": [
          {
            "turoyo": "aṯi ʕabər, ḥzele at=tarte...",
            "translations": [
              "darauf trat er ein; als er die beiden erblickte..."
            ],
            "references": ["233", "prs 130/22"]
          }
        ],
        "Infectum": [...],
        "Imperative": [...]
      }
    },
    {
      "binyan": "III",
      "forms": ["maʕballe", "maʕbər"],
      "conjugations": {...}
    }
  ]
}
```

## Field Types

### Root String
```json
"root": "ʕbr"
```
- Type: `string`
- Pattern: 2-6 consonantal root characters
- Special chars: `ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzḏṯẓāēīūə`

### Etymology Object (Optional)

**Full structure:**
```json
{
  "source": "MEA",           // Etymology source
  "source_root": "ʕbr",      // Root in source language
  "reference": "SL 1064",    // Academic reference
  "meaning": "to pass..."    // English meaning
}
```

**Simple structure:**
```json
{
  "source": "Arab.",
  "notes": "ʕbd, Wehr 807: dienen..."
}
```

**Raw only:**
```json
{
  "raw": "denom. (< u=ḥărbo)"
}
```

**Missing:**
```json
null
```

### Cross-Reference String (Optional)
```json
"cross_reference": "ʕwd"
```
- Type: `string | null`
- Points to another root
- If present, no stems will be included

### Uncertain Boolean
```json
"uncertain": false
```
- Type: `boolean`
- `true` if marked with ??? in source
- Indicates uncertain/questionable data

### Stems Array
```json
"stems": [...]
```
- Type: `array` (0 to 11 items)
- Each stem represents a binyan or voice
- Empty if cross-reference verb

## Stem Object Structure

```json
{
  "binyan": "I",                    // or "II", "III", "Detransitive"
  "forms": ["ʕabər", "ʕobər"],      // Array of 0-4 forms
  "conjugations": {...}             // Conjugation tables
}
```

### Binyan Values
- `"I"` - Binyan I (basic stem)
- `"II"` - Binyan II (intensive)
- `"III"` - Binyan III (causative)
- `"Detransitive"` - Detransitive/passive

### Forms Array
```json
"forms": ["ʕabər", "ʕobər"]
```
- Type: `array<string>`
- Usually 2 forms (Preterit/Infinitive)
- Separated by `/` in source
- Can be 0-4 forms

### Conjugations Object

```json
{
  "Preterit": [...],
  "Preterit Intransitive": [...],
  "Infectum": [...],
  "Infectum-wa": [...],
  "Imperative": [...],
  "Infinitive": [...],
  "Participle_Active": [...],
  "Participle_Passive": [...],
  "ko-Preterit": [...],
  // ... and more
}
```

**Common conjugation types:**
- `Preterit` - Past tense
- `Preterit Intransitive` - Past intransitive
- `Infectum` - Present/imperfect
- `Infectum-wa` - Narrative present
- `Imperative` - Commands
- `Infinitive` - Infinitive form
- `Participle_Active` - Active participle
- `Participle_Passive` - Passive participle

Each value is an **array of example objects**.

## Example Object Structure

```json
{
  "turoyo": "aṯi ʕabər, ḥzele...",
  "translations": [
    "darauf trat er ein...",
    "dann schlüpft sie..."
  ],
  "references": ["233", "prs 130/22", "MM 27"]
}
```

### Fields

**turoyo** (string)
- Turoyo text with diacritics
- May contain multiple sentences
- Whitespace may include newlines/tabs

**translations** (array<string>)
- German, English, or Russian translations
- Extracted from quotes in source
- Can be empty array if no translation

**references** (array<string>)
- Page references (e.g., "233", "24/51")
- Source abbreviations (e.g., "MM 27", "JL 9.9.4")
- Can be empty array

## Common Patterns

### Find verb by root
```python
verbs = {v['root']: v for v in data['verbs']}
verb = verbs['ʕbr']
```

### Get all binyanim for a verb
```python
binyanim = [stem['binyan'] for stem in verb['stems']]
```

### Get all examples
```python
examples = [
    example
    for stem in verb['stems']
    for conj_type, examples in stem['conjugations'].items()
    for example in examples
]
```

### Filter by etymology source
```python
arab_verbs = [
    v for v in data['verbs']
    if v.get('etymology') and v['etymology'].get('source') == 'Arab.'
]
```

### Get verbs with most examples
```python
verbs_with_counts = [
    (v, sum(len(examples)
            for stem in v['stems']
            for examples in stem['conjugations'].values()))
    for v in data['verbs']
]
sorted_verbs = sorted(verbs_with_counts, key=lambda x: -x[1])
```

## Edge Cases to Handle

### 1. Missing Etymology
```json
"etymology": null
```
~18% of verbs

### 2. No Stems
```json
"stems": []
```
17 verbs (1.4%)

### 3. Empty Conjugations
```json
"conjugations": {}
```
83 stems (4.8%)

### 4. Empty Turoyo
```json
{
  "turoyo": "",
  "translations": ["some note"],
  "references": []
}
```
190 examples

### 5. No Translations
```json
{
  "turoyo": "some text",
  "translations": [],
  "references": []
}
```
Common - not all examples have translations

### 6. Duplicate Binyanim
Some verbs have same binyan multiple times:
```json
"stems": [
  {"binyan": "I", ...},
  {"binyan": "I", ...}
]
```
121 verbs - may indicate multiple senses

## TypeScript Interface

```typescript
interface VerbData {
  verbs: Verb[]
  metadata: Metadata
}

interface Metadata {
  total_verbs: number
  total_stems: number
  total_examples: number
  cross_references: number
  uncertain_entries: number
  parser_version: string
}

interface Verb {
  root: string
  etymology: Etymology | null
  cross_reference: string | null
  uncertain: boolean
  stems: Stem[]
}

interface Etymology {
  source: string
  source_root?: string
  reference?: string
  meaning?: string
  notes?: string
  raw?: string
}

interface Stem {
  binyan: 'I' | 'II' | 'III' | 'Detransitive'
  forms: string[]
  conjugations: Record<string, Example[]>
}

interface Example {
  turoyo: string
  translations: string[]
  references: string[]
}
```

## Validation Tips

1. **Always check for null**: Etymology can be null
2. **Check array lengths**: Stems, forms, examples can be empty
3. **Handle whitespace**: Turoyo text may have \n, \t
4. **Unicode**: Full UTF-8 with special chars
5. **Duplicates**: Same binyan may appear twice (review case-by-case)

---

For implementation examples, see:
- `parser/validate.py` - Data validation
- `parser/verify_against_source.py` - Usage examples
