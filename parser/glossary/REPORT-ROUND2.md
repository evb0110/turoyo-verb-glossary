# Stage 0 glossary parser, round 2

Verified on 2026-10-25 against all seven DOCX volumes in
`source/glossary-docx/2026-10-21/`. This report supersedes the counts and open parser
gaps in `REPORT.md`, which remains the round-1 record.

The regenerated output contains 1,541 entries and 8,158 examples. All 23 tests pass.
Saved-output round trip remains **1,286,217 / 1,286,217 characters, 100%**, across
15,126 source units, with **no residue**. Every volume individually has 100% coverage.
No DOCX was changed, and no commit or push was made. Verification used the working
tree based on `7a9e3a995c4f989fc7e97f2a54407b51d2d707e9`.

## Changes

The existing `examples.py` splitter now judges a quoted translation by the formatting
of its content. An italic opening or closing quotation mark no longer hides a roman
translation. A following citation also identifies translations whose entire run was
accidentally italicized. Italic Turoyo remains the strongest boundary signal.

The reference scanner consumes trailing speaker/transcriber marks, personal
communications, dates, corpus locators and page references before starting the next
example. This includes `[MT]`, `[LTN]`, `[ML]`, `(Ilyas p.c.)`, `JL 19.6.19`,
`LB 212`, bare pages, `jl 17.6.10` and `lj 175`. Separate citation and translation
paragraphs rejoin their preceding Turoyo passage. A new passage's source label or verse
number remains with that passage.

Translation extraction also handles complete unquoted English after Turoyo, including
absent or inverted formatting, parentheses and numbers within the translation. The
fallback requires identifiable English syntax. Nested quotation marks, adjacent closing
marks and possessive apostrophes no longer create artificial examples. Turoyo direct
speech and editorial remarks remain distinct from translations.

Numeric sense splitting excludes quoted translations and parenthesized timestamps or
comments. A real number immediately followed by a bracket or quotation mark is accepted.
In `parse.py`, an unnumbered first gloss followed by an explicitly numbered continuation
is retained as sense 1; a slash-form-only prefix is excluded. Literal source gaps remain.

The sense audit also exposed standalone box headings whose following one-cell tables
were attached to the preceding box. The shared box-creation path now recognizes these
headings, including `Action Noun`. This recovers 17 box boundaries, with local glosses
retained in notes. There is no new parsing subsystem or new contract field. The contract's
translation comment now documents unquoted and parenthetical translations.

The reported `qbl.III.t.preterit.3` passage is now three examples at positions 3–5,
with separate translations beginning `Der Arme beriet sich mit`, `[Der König] freute
sich`, and `Bruder! Ich <…> erkenne`. The first two retain `23/16 [MT]` and
`24/97 [MT]` respectively. All three inherit the same sense number.
`U Sargey lo kmaqbal ʕal u+ʕantar` now has the extracted translation
`does not allow people to offend him`.

## Before and after

| Item                                                        | Round 1 | Round 2 |
| ----------------------------------------------------------- | ------: | ------: |
| Entries                                                     |   1,541 |   1,541 |
| Stems                                                       |   1,873 |   1,873 |
| Ordinary senses                                             |   2,302 |   2,316 |
| Detransitive senses                                         |     201 |     201 |
| Boxes                                                       |   4,285 |   4,302 |
| Examples                                                    |   8,079 |   8,158 |
| Embedded translation/citation heuristic matches in `turoyo` |     143 |       0 |
| Examples without an extracted translation                   |     513 |     329 |
| Examples with an absent sense number in the relevant list   |     224 |     202 |

The fusion measurement uses the parent's exact diagnostic regex:

```python
r'[ʻ‘][^ʼ’]{3,}[ʼ’]\s*;?\s*(\d|JL|prs|PrS|LB|MM)'
```

All 143 original matching records are mapped to their replacements in
`audit-round2.json`. Zero matches is a regression result for this symptom, rather than
a proof about every conceivable linguistic boundary. The net example increase also
includes reunified citation/translation fragments and corrected paragraph boundaries.
Example IDs use positions within boxes, so later IDs can change after a split or merge.

## Translation audit

All 513 original untranslated records have classifications and source locations in
`audit-round2.json`. Baseline and rebuilt records were aligned by overlapping NFC
character spans in the same physical DOCX unit and inspected with italic/roman runs.
The audit records every original ID, its class, source span and resulting example IDs.
Its remaining-record inventories use the regenerated IDs.

| Class                                                              | Original untranslated records | Final untranslated records |
| ------------------------------------------------------------------ | ----------------------------: | -------------------------: |
| Parser: citation, speaker mark or source-label fragment            |                            59 |                          0 |
| Parser: quoted translation/closing-mark fragment                   |                            11 |                          0 |
| Parser: translation in a following paragraph                       |                            26 |                          0 |
| Parser: unquoted translation, including absent/inverted formatting |                            97 |                          0 |
| Source: form or passage without a complete translation             |                           292 |                        305 |
| Source: editorial remark, metadata or heading                      |                            19 |                         15 |
| Source: partial or irregular gloss/working annotation              |                             9 |                          9 |
| Total                                                              |                           513 |                        329 |

**193 original records were parser errors; 320 were source cases.** All identified
parser errors were corrected. These are counts of records, not independent sentences:
some old records were fragments of one example and some contained multiple examples.
Splitting also exposes untranslated passages previously hidden inside compound records,
and removing false translations exposes direct speech or citation text. Therefore
subtracting 193 from 513 does not predict the final untranslated count.

The remaining 329 records preserve source material that cannot supply a complete
translation: 305 forms or untranslated passages, 15 editorial/metadata records and nine
partial or irregular glosses. Examples include a bare paradigmatic form, correspondence
about adding examples, a heading without a form, a gloss-only row, and fragmentary
English/Russian annotations. Their original wording remains available for proofreading;
the parser supplies no invented translation.

## Sense-number audit

All 224 original mismatches are classified and mapped in `audit-round2.json`.

| Class                                                        | Original mismatches | Final mismatches |
| ------------------------------------------------------------ | ------------------: | ---------------: |
| Parser: citation-only artificial example                     |                   1 |                0 |
| Parser: implicit first gloss folded into a later sense       |                  13 |                0 |
| Parser: timestamp, locator or quotation/comment number       |                  11 |                0 |
| Source: no separate Detransitive sense list                  |                 173 |              176 |
| Source: no ordinary sense list for the stem                  |                   1 |                1 |
| Source/contract scope: box-local Action Noun numbering       |                   5 |                5 |
| Source: literal example number absent from the supplied list |                  20 |               20 |
| Total                                                        |                 224 |              202 |

**25 original mismatches were parser misreads; 199 were source or scope cases.** The
final 202 cases retain the source numbers. Correct splitting exposes additional
Detransitive examples without a separate list, and the citation fragment merges into
an already mismatched example, so the numerical decrease is 22 rather than 25.

Ordinary senses were not copied into Detransitive lists. The ordinary list missing
from `hyw-1.III` remains absent. Five Action Noun examples use local source numbering;
their explicit box headings and local gloss notes survive, while `IEntry` stores sense
lists at stem/diathesis level. Twenty numbers are literally present in examples but
absent from the applicable source list. None was renumbered to conceal the mismatch.

## Verification and regeneration

The original nine regressions remain. Fourteen additional tests cover the new quotation,
formatting, citation, paragraph, unquoted-translation, heading and sense-number cases,
including a full-corpus fusion scan and the two reported `qbl` examples.

```sh
cd /Users/evb/WebstormProjects/turoyo-verb-glossary
export TMPDIR="$(agent-tmpdir glossary-round2)"
agent-env run --mem 4G -- .devkit/glossary-parser-venv/bin/python -m parser.glossary
agent-env run --mem 4G -- .devkit/glossary-parser-venv/bin/python -m unittest parser.glossary.test_glossary -v
agent-env run --mem 4G -- .devkit/glossary-parser-venv/bin/python -m parser.glossary.roundtrip
```

Results: **23/23 tests passed**, saved JSON passed the contract/index/reference checks,
and round trip covered all 1,286,217 characters with `residue: []`. The auditor compares
the actual saved fields with independently reopened DOCX source units. This verifies
text retention as well as the structural checks; the focused regressions verify the
reported parsing behavior.

An unchanged-input rebuild was byte-for-byte identical. The aggregate SHA-256 is saved
in `summary.json` under `verification.assetsSha256`; it hashes sorted entry filenames
and contents, then the index filename and contents. `summary.json` contains current
counts, mismatch IDs, coverage, diagnostics and the audit pointer.

Changes are limited to `parser/glossary/`, generated glossary entries/index, and the
translation comment in `docs/data-contract.md`. Unrelated shared-checkout work was
preserved. The remaining classified source irregularities require proofreading rather
than further splitting or extraction heuristics.
