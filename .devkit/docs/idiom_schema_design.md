# Idiomatic Expression Schema Design

## Problem

The current parser only extracts conjugation data from **tables**, losing idiomatic expressions that appear as standalone paragraphs. Example: hyw 1 has **33 idiomatic expressions** that are completely missing from the parsed output.

## Example Lost Data (hyw 1)

```
obe/hule ʕafu 'begnadigen': w-hule-ste ʕafu l-a=tre=aḥunon-ayḏe d-kət-wayye b-u=ḥabis
'Er gewährte auch den beiden Brüdern, die im Gefängnis waren, Vergebung'

obe/hule ʕumro 'sterben': ḥa=yawmo i=sawt-aṯe kayula w húla-lxu ʕumro
'eines Tages wurde die Alte krank und gab euch das Leben' [=starb]

obe/hule baxt 'Ehrenwort geben': an=noš-ani lo=ku-mʔamnən-xu ábadan d-l=obénan-ne ono baxti
'Diese Leute haben gar kein Vertrauen zu euch, wenn ich ihnen nicht mein Ehrenwort gebe'
```

## Current Schema

```typescript
interface IVerb {
  root: string
  etymology: IEtymology
  cross_reference: string | null
  stems: IStem[]
  uncertain: boolean
}
```

## Proposed Schema Addition

Add a new top-level field `idioms` to capture idiomatic expressions:

```typescript
interface IVerb {
  root: string
  etymology: IEtymology
  cross_reference: string | null
  stems: IStem[]
  idioms?: IIdiom[]  // NEW: Optional array of idiomatic expressions
  uncertain: boolean
}

interface IIdiom {
  phrase: string           // Turoyo phrase (e.g., "obe/hule ʕafu")
  meaning: string          // Translation/gloss (e.g., "begnadigen", "to pardon")
  examples: IIdiomExample[]  // Usage examples with translations
}

interface IIdiomExample {
  turoyo: string           // Turoyo example sentence
  translation: string      // German/English translation
  reference?: string       // Optional page/line reference
}
```

## Example JSON Output

```json
{
  "root": "hyw 1",
  "etymology": {
    "etymons": [{
      "source": "MEA",
      "source_root": "yhb",
      "reference": "SL 565-566",
      "meaning": "to give"
    }]
  },
  "cross_reference": null,
  "stems": [
    {
      "stem": "I",
      "forms": ["hule", "obe"],
      "conjugations": { ... }
    },
    {
      "stem": "III",
      "forms": ["mahwele", "mahwe"],
      "conjugations": { ... }
    }
  ],
  "idioms": [
    {
      "phrase": "obe/hule ʕafu",
      "meaning": "begnadigen (to pardon)",
      "examples": [{
        "turoyo": "w-hule-ste ʕafu l-a=tre=aḥunon-ayḏe d-kət-wayye b-u=ḥabis",
        "translation": "Er gewährte auch den beiden Brüdern, die im Gefängnis waren, Vergebung",
        "reference": null
      }]
    },
    {
      "phrase": "obe/hule ʕumro",
      "meaning": "sterben (to die, lit. 'give life')",
      "examples": [{
        "turoyo": "ḥa=yawmo i=sawt-aṯe kayula w húla-lxu ʕumro",
        "translation": "eines Tages wurde die Alte krank und gab euch das Leben",
        "reference": null
      }]
    },
    {
      "phrase": "obe/hule baxt",
      "meaning": "Ehrenwort geben (to give word of honor)",
      "examples": [{
        "turoyo": "an=noš-ani lo=ku-mʔamnən-xu ábadan d-l=obénan-ne ono baxti",
        "translation": "Diese Leute haben gar kein Vertrauen zu euch, wenn ich ihnen nicht mein Ehrenwort gebe",
        "reference": null
      }]
    }
  ],
  "uncertain": false
}
```

## Parser Changes Required

### 1. Detection Logic

When parsing a verb, after extracting the root and before hitting the first stem header:

- Collect all non-table paragraphs
- Use pattern matching to detect idiomatic expressions:
  - Contains verb forms (obe, hule, mahwele, etc.) + Turoyo words
  - Has quotation marks (ʻʼ"") indicating translation
  - Follows pattern: `PHRASE 'TRANSLATION': EXAMPLE`

### 2. Parsing Logic

For each detected idiom paragraph:

```python
# Pattern: "obe/hule PHRASE 'MEANING': EXAMPLE 'TRANSLATION'"
idiom_pattern = r"^(.+?)\s+[ʻʼ""]([^ʻʼ""]+)[ʻʼ""]:?\s*(.*)$"

match = re.match(idiom_pattern, paragraph_text)
if match:
    phrase = match.group(1).strip()      # "obe/hule ʕafu"
    meaning = match.group(2).strip()     # "begnadigen"
    example_text = match.group(3).strip() # Rest of the paragraph

    # Extract Turoyo and German from example_text
    # (may contain embedded translations in quotes)
```

### 3. Extraction Algorithm

```python
def extract_idioms(self, paragraphs_before_first_stem):
    """
    Extract idiomatic expressions from paragraphs between root and first stem.

    Args:
        paragraphs_before_first_stem: List of paragraph objects

    Returns:
        List of idiom dicts
    """
    idioms = []

    for para in paragraphs_before_first_stem:
        # Skip if in table
        if self.is_in_table(para):
            continue

        text = para.text.strip()

        # Skip empty or very short paragraphs
        if len(text) < 10:
            continue

        # Try to parse as idiom
        idiom = self.parse_idiom_paragraph(text)
        if idiom:
            idioms.append(idiom)

    return idioms if idioms else None
```

## Benefits

1. **Preserves linguistic data** - 33 idioms for hyw 1 alone, potentially hundreds across all verbs
2. **Searchable** - Users can search for specific idiomatic expressions
3. **Structured** - Clean separation between conjugation data and idiomatic usage
4. **Extensible** - Easy to add more idiom metadata (register, frequency, etc.)

## Implementation Priority

**CRITICAL** - This is systematic data loss affecting core linguistic content. Should be implemented immediately.

## Validation

After implementation:
- Verify hyw 1 has 33 idioms extracted
- Check other high-frequency verbs (ʔzl, ʔmr, etc.) for idioms
- Ensure no idioms from conjugation tables are duplicated
- Validate JSON schema matches TypeScript interface
