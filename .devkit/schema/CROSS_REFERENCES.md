# Cross-References in DOCX Source

## Cross-Reference Patterns Found

The DOCX source files contain cross-references using the arrow symbol (→):

### Direct Cross-References:

| Entry        | Cross-Reference |
| ------------ | --------------- |
| ʔkl          | → ʔxl           |
| (standalone) | → ḥfy           |
| (standalone) | → ʕžl           |
| (standalone) | → ḥṣy           |
| (standalone) | → ʕwḏ           |
| ʕwḏ          | → ʕwd           |
| ʕžl          | → ʕǧl           |

## Current Parser Status

The parser has `cross_reference` field but found **0 entries** with cross-references in the parsed JSON. This means the parser is **not extracting** cross-references.

### Recommendation

Update parser to detect patterns:

1. `→ [root]` - Direct cross-reference
2. `[root] → [other_root]` - Root pointing to variant
3. `see [root]` - Reference pattern
4. `See [root] [stem]` - Reference with stem

---

## Uncertainty Markers

The DOCX contains entries with uncertainty markers (???, ?):

### Examples:

```
brd 2 (??) (<unknown)
bġṭ (unknown) see also bʕṭ - м.б. один глагол?
1) sprechen, sagen, erzählen, denken, fordern ???
oṯe/aṯi ʕal ?????: ...
```

### Types:

1. **Etymology uncertainty:** `(??)`, `(<unknown)`
2. **Meaning uncertainty:** `fordern ???`
3. **Relationship uncertainty:** `м.б. один глагол?` (Russian: "maybe same verb?")
4. **Placeholder:** `?????` in example text

### Recommendation

Extract uncertainty markers to `notes` field and optionally set `uncertain: true` flag.

---

## Editor Notes (Multilingual)

The source contains notes in multiple languages:

| Language | Example                                                                            |
| -------- | ---------------------------------------------------------------------------------- |
| German   | Standard glosses and translations                                                  |
| English  | Some modern additions                                                              |
| Russian  | `м.б. один глагол?`, `Не уверен в правильности формы`, `М.Б БОЛЕЕ УЗКОЕ ЗНАЧЕНИЕ?` |

These should be preserved in `notes` fields without modification.
