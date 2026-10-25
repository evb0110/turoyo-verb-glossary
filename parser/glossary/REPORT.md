# Stage 0 glossary parser

Round-1 record. See [REPORT-ROUND2.md](REPORT-ROUND2.md) for the corrected splitting,
complete gap classifications, regenerated counts and current verification results.

Verified on 2026-10-25 against the seven volumes in `source/glossary-docx/2026-10-21/`.
The package emits 1,541 `IEntry` files and `server/assets/glossary/index.json`.
No source documents or old parser files were changed. No commit or push was made.
The shared checkout's base commit was `7a9e3a995c4f989fc7e97f2a54407b51d2d707e9`;
the implementation and generated assets remain uncommitted as requested.

## Implementation

The parser uses Python's standard library: `zipfile` and XML, with inherited and direct
italic formatting retained per character. `docx.py` reads physical cells without merged-cell
aliases; `parse.py` follows root, stem, sense, Detransitive, box, and idiom sections;
`examples.py` separates numbered groups, examples, translations, references, and notes.
It handles separate and same-line glosses, missing colons, embedded stem headings,
unlabelled continuation cells, nested translation quotes, and unquoted roman translations.
All 21 substantive footnotes are attached as verbatim notes at their source anchors.

Strings are NFC. Source spelling, sense-number gaps, editorial question marks, Russian
notes, and punctuation remain intact. Literal structural headings are retained in notes,
so the numbered and punctuated source can be reconstructed without inventing delimiters.

## Round-trip result

**1,286,217 / 1,286,217 non-whitespace NFC characters, 100%; 15,126 non-empty source units.**
One source unit is an ordinary paragraph or a physical table cell, including footnote
paragraphs. Each table cell includes all its paragraphs. There are no non-empty endnotes
or comments in this snapshot.

| Volume                   | Source units | Covered characters | Coverage |
| ------------------------ | -----------: | -----------------: | -------: |
| 1. ʔ, ʕ, b, č.docx       |        2,090 |  183,063 / 183,063 |     100% |
| 2. d, f, g, ġ, ǧ.docx    |        2,458 |  189,901 / 189,901 |     100% |
| 3. h,ḥ,k.docx            |        2,063 |  194,149 / 194,149 |     100% |
| 4. l,m,n,p.docx          |        2,209 |  193,831 / 193,831 |     100% |
| 5. q,r,s,ṣ.docx          |        2,916 |  252,284 / 252,284 |     100% |
| 6. š,t,ṭ,ṯ.docx          |        2,083 |  168,381 / 168,381 |     100% |
| 7. v, w, x, y, z, ž.docx |        1,307 |  104,608 / 104,608 |     100% |

**Residue: `[]`.**

`roundtrip.py` independently reopens the OOXML and the saved JSON. The parser supplies
field addresses, not a separate archive of source text. The auditor concatenates those
actual JSON fields, strips whitespace, and compares every source unit. It rejects missing
or duplicate source attributions, duplicate IDs, stale/missing files, a mismatched index,
wrong contract keys, and invalid Ritter/Prym–Socin resolution. It also checks that parsed
example fields are substrings of their raw source. A regression deliberately corrupts
saved JSON and confirms the auditor detects the residue.

This proves text retention; it does not prove every linguistic or ambiguous typographic
interpretation. The uncertainty cases below remain available in raw text and notes.

## Summary

| Item                                                                        | Count |
| --------------------------------------------------------------------------- | ----: |
| Entries                                                                     | 1,541 |
| Stems, including repeated source sections                                   | 1,873 |
| Ordinary senses                                                             | 2,302 |
| Detransitive senses                                                         |   201 |
| Total senses                                                                | 2,503 |
| Boxes                                                                       | 4,285 |
| Examples                                                                    | 8,079 |
| Examples whose number is absent from the relevant stem/diathesis sense list |   224 |
| Examples without an extracted translation                                   |   513 |
| Idiom records                                                               |   290 |

The 224 mismatches are reported, not renumbered. The relevant list for a Detransitive
box is `detransitiveSenses`; an absent list therefore flags every numbered example there.
The complete mismatch IDs are in `summary.json`.

References in structured examples, counted once per `IRef` (ranges are not expanded):

| Kind         |  Count |
| ------------ | -----: |
| text         |  4,950 |
| grammar-page |  4,379 |
| prs          |    981 |
| jl           |    312 |
| lb           |    315 |
| mm           |     94 |
| luf          |     78 |
| other        |    831 |
| Total        | 11,940 |

References inside raw idioms or unparsed notes are not fabricated as `IRef` objects.
Bare Ritter `N/V` references resolve to `R%03d` and verse V. Prefixed references remain
unresolved; specifically, `prs N/V` is page/line and has null textId and verse.

## Comparison with prior parsers

| Output / parser                                            | Entries | Stems | Boxes |         Examples |
| ---------------------------------------------------------- | ------: | ----: | ----: | ---------------: |
| Pilot `glossary_parsed.json`                               |   1,567 | 1,853 | 4,279 | unsplit box text |
| Pilot `glossary_full.json`                                 |   1,496 | 1,853 | 4,279 |            8,161 |
| Old production parser, run in memory against this snapshot |   1,505 | 2,360 | 4,309 |            8,348 |
| New structured parser                                      |   1,541 | 1,873 | 4,285 |            8,079 |

The production parser was imported and run without calling its save/split methods.
Its printed `stems_parsed` statistic is 2,303, but counting its actual stem objects gives
2,360; the table uses the actual objects. Its run matched the existing saved production
output's entry and example totals.

The full pilot has 1,487 distinct roots, nine repeated-root records, and a false `r`
entry that is a letter heading. The new output retains 55 additional source root labels,
removes that letter entry, and combines repeated root labels: 1,496 − 9 − 1 + 55 = 1,541.
The quick pilot also counts other letter headings and misses differently formatted roots.

Examples of recovered labels are `fyṭ`, `mǧq`, `qwy I`, `qwy II`, `trq I`, `trq II`,
`ḥyl`, `tks`, `yzd`, and the `šġl`/`žġl` cross-reference entries. The pilot put the two
`qwy` entries' stems and boxes inside `qwt`; they now belong to their literal root labels.
Some newly retained labels, such as `ksb`, are working entries with notes rather than a
complete paradigm.

Stem and box totals differ because explicit malformed/embedded headings are recovered,
Detransitive is a state of a stem rather than another stem, and repeated physical rows
remain identifiable. Example totals also reflect different splitting: citation ranges,
blank sense markers, equivalence annotations, and author initials are not examples;
nested quotes do not end translations early; unformatted material is kept conservatively.
The orphan leading section in volume 7 is retained in notes and is excluded from
structured example counts. The counts are structural counts, not a claim that one parser
found more or fewer underlying attestations. Full text retention is checked separately.

## Ten source spot-checks

These entries were compared with the DOCX text and run formatting, and checked with
explicit assertions plus the source-unit round trip. All ten checks passed for the
reported aspects.

1. **sym**: stems I and III; I has 14 ordinary senses numbered 1–10 and 12–15, with
   the missing 11 preserved, and three Detransitive senses. Fifteen boxes, 79 examples,
   50 raw idiom records. `səmle/soyəm` and the first example's German translation and
   `64/65` → R064:65 agree with the source.
2. **qym**: I has 11 senses, preserving the gap from 7 to 10; III has eight.
   Thirteen boxes, 66 examples, 18 idiom records. Alphabetic a)/b) subdivisions remain
   in their raw wording; numeric senses are not flattened or renumbered.
3. **ʔzl**: `azzé(azile)/əzzé`, eight senses, nine boxes, 49 examples, three idioms.
   The irregular `azzayo` example and its Russian query remain verbatim.
4. **hwy 2**: id `hwy-2`, homonym 2, `hwele(hawi)/howe`, nine senses, nine boxes,
   46 examples, eight idioms. Sense 2's first example resolves `37/17` to R037:17;
   Russian parenthetical comments in the senses remain intact.
5. **ḥwy 2**: id `ḥwy-2`; the inserted same-line stem II is retained separately
   from III. Forms are `mḥawele/mḥawe` and `maḥwele/maḥwe`; III has two senses,
   four boxes, 16 examples. The informal inline II illustration remains in the verbatim
   sense paragraph/header note rather than being given an invented box.
6. **mtš**: `mtīš/mitәš`, preserving the source's Cyrillic ә; `Infc.` canonicalizes
   to Infectum. The translated example's `= hič lo+kuzzí ...` stays a trailing note.
   The separate `*kazzí gmitәšno` line remains an untranslated example. Two examples.
7. **dʕdk**, a quadriliteral: the source labels its stem I, which is preserved.
   `mdaʕdakle/mdaʕdək` and `niedertreten, zertrampeln, zerknittern;` agree with the
   source. There is no following table for this root, so no boxes were invented.
8. **hbṭ**, Detransitive only: `(Detrans.?) Schrecken bekommen;` remains qualified.
   Its sole Preterit box is Detransitive, with two examples. Nested direct speech in
   the German translation does not truncate it; `prs 223/30` remains unresolved.
9. **ʔḏʕ**, idiom shape: stems I and III, three ordinary I senses, 15 boxes,
   48 examples, and one raw idiom paragraph containing the two `ruḥi` illustrations.
   The opening example's `24/46` resolves to R024:46. Detransitive examples without
   a stated Detransitive sense list remain flagged rather than assigned a new list.
10. **ḥyz**, Russian notes: `aloho ḥayəz` / `es beliebte Gott`; `97/153` resolves
    to R097:153. `Пример отсутствует в указанном месте` is exactly the example's note.
    The second unnumbered root paragraph and `PrS 15/33` are retained in entry notes.

## Decisions and contract changes

`docs/data-contract.md` now documents the source-driven cases that its original ID rules
could not represent:

- Repeated stems and boxes get stable source-occurrence suffixes `~2`, `~3`, etc.
  Examples retain the documented positional numbering within each box.
- Identical literal root labels share one entry; subsequent heads stay in notes and
  stem sections stay separate. Eleven repeated-root sections are retained: hdd, hdf,
  hdm, ḥkm, ḥṣy, ḥyz, ngl, swy, šbḥ, tšhy, zʕf. No homonym numbers are invented.
- Notes retain headings, footnotes, and uncertain structure. The rootless leading
  volume-7 material stays in the first entry's notes. Idiom table rows keep their
  cells, joined by newlines, in idiom raw text.
- Source order is a 1-based OOXML body-block position. NFC/whitespace handling,
  inherited example numbers, range references, and null Prym–Socin verse values
  are explicit. There are no new interface fields.

I treated a leading `(Detrans.)` gloss as a Detransitive sense list even without a
separate heading, preserving any uncertainty marker. I recovered only explicitly
stated stems; slash-form lines without a marker use I, unless a trailing marker states
another stem. Generic `Participle` labels remain generic because act./pass. is uncertain.

## Retained uncertainty

- 513 structured examples have no confidently extracted translation. Some genuinely
  lack one, some are paradigmatic forms, and some have inconsistent or absent formatting.
  Unformatted unparseable material is also retained in `note`; nothing is translated
  or corrected by the parser. Unformatted speaker-plus-quotation blocks are ambiguous.
- The 224 unmatched sense-number examples are source/editorial issues to review, not
  automatically repaired. Full IDs are saved in `summary.json`.
- Cells under roots/sections without an explicit usable stem remain in notes. Affected
  entry-note hosts are dfn, dhn, grmz, ksb, kšr, qrš-4, qṣr-2, skt, ṣmm, and vrvn.
  For vrvn these are the rootless `mvazele/mvazal` section at the start of volume 7,
  not evidence that those forms belong to vrvn. Some other hosts contain working
  correspondence or a new section inserted after an idiom section.
- Inline illustrations without a stated box stay in the original paragraph. Idiom
  records preserve paragraphs/rows rather than guessing how many linguistic idioms
  each one represents; headwords are conservative prefixes and may be null.
- Only bare Ritter text/verse citations resolve to corpus IDs. Other source families
  and references buried in raw notes/idioms await later structured interpretation.

## Regeneration and checks

Run from the repository, using the task-owned ignored virtualenv. The new parser itself
has no third-party dependencies. `python-docx` was installed only to compare the old
production parser in memory.

```sh
cd /Users/evb/WebstormProjects/turoyo-verb-glossary
/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/glossary-parser-venv/bin/python -m parser.glossary
/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/glossary-parser-venv/bin/python -m parser.glossary.roundtrip
/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/glossary-parser-venv/bin/python -m unittest parser.glossary.test_glossary -v
```

All nine focused regression tests passed. `summary.json` contains the machine-readable
summary, mismatch IDs, coverage, and names of the ten checked entries. The CLI supports
`--source` and `--output` to regenerate a separate snapshot without changing code.
An unchanged-input rebuild was byte-for-byte identical. The aggregate SHA-256 over the
sorted entry filenames/contents followed by index filename/contents was
`6f0fa4ee676b6881bd40c44ff9b14f16faf6e60ef5d9e83650d0f6a131ca012c`.
