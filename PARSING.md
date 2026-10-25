# Parsing pipeline (DOCX → JSON → site)

The glossary data is generated; **never edit the JSON by hand**. Fix the parser and regenerate.

## Sources and outputs

- **Source**: the seven Word volumes in `source/glossary-docx/<snapshot>/` (catalogue: `source/README.md`).
- **Parser**: `parser/glossary/` (Python standard library only).
- **Output**: `server/assets/glossary/entries/<entryId>.json` and `server/assets/glossary/index.json`, in the
  format of `docs/data-contract.md` (`IEntry`): stems, numbered senses, boxes and examples split into
  Turoyo, translation, references and notes, with stable ids.

## Commands

```bash
python3 -m parser.glossary              # regenerate entries and index (--source DIR for another snapshot)
python3 -m parser.glossary.roundtrip    # prove every character of the DOCX is in the output (must be 100%)
python3 -m unittest parser.glossary.test_glossary -v
```

Run them from the repository root. A new snapshot of the Word files goes into a new dated folder under
`source/glossary-docx/`; update `SOURCE` in `parser/glossary/parse.py` and rerun all three.

## What the parser guarantees

- Every non-empty paragraph and table cell is accounted for (round trip 100%); text is kept verbatim
  (NFC). Nothing is corrected: errors in the glossary are reported by the proofreading stage as
  proposals, not silently fixed.
- Italic runs are Turoyo, roman runs translation; this splits examples whose quotes are missing.
- Sense numbers are kept as written, including gaps; examples numbered with a sense absent from the
  stem's list are listed in `parser/glossary/summary.json`.

Details, counts and design decisions: `parser/glossary/REPORT.md` and `REPORT-ROUND2.md`.

## Machine proposals and corpus texts

`server/assets/glossary/proposals/` and `texts/` are written by the agent pipeline in
`.devkit/analysis/corpus-run/` (`build_bundle.py`); see `docs/data-contract.md`.
