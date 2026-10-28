# Data contract: glossary, corpus, proposals

The site shows three layers. Each has one producer and is stored as JSON under `server/assets/glossary/`.

| Layer                                         | Producer                                                                           | Files                                                              |
| --------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| The glossary as the team wrote it             | `parser/glossary/` from `source/glossary-docx/<snapshot>/`                         | `entries/<entryId>.json` (`IEntry`), `index.json`                  |
| The text corpus                               | agent pipeline (`.devkit/analysis/corpus-run/build_corpus.py`) from `aramaictexts` | `texts/<textId>.json` (`IText`), `texts/index.json`                |
| Machine proposals (additions and corrections) | agent pipeline (reading, synthesis, citation check, proofreading)                  | `proposals/<entryId>.json` (`IProposal[]`), `proposals/index.json` |

Editorial decisions live in Postgres: `proposal_decision` contains one current team decision per proposal,
and `proposal_review_event` retains decision snapshots and undo events. See [review-storage.md](review-storage.md).
The site also writes authentication and activity data. Static glossary assets are never rewritten by a review.

`entries/`, `index.json` and `proposals/` are committed (the glossary and its quotations are public in this
repository). `texts/` is not: the editions are third-party works kept in the private `aramaictexts`
repository, so the pipeline writes them locally and the Vercel CLI deploys them from disk.

Identifiers are stable across rebuilds, so reviews stay attached:

- `entryId`: the root label with spaces as `-`, e.g. `ḥwy-2`, `sym` (Unicode NFC, kept as is in URLs).
- `stemId`: `<entryId>.<stem>` e.g. `sym.I`; `boxId`: `<stemId>.<d|t>.<box label slug>` (`d` = Detransitive).
- `exampleId`: `<boxId>.<n>` where n is the 1-based position of the example in the box as the DOCX has it.
- `textId`: `R024` (Ritter text 24), `PrS001`, `JL05.10`, `JTM1.3`, `LuF002`, `Hors001`, `Talay002`,
  `Lahdo_<title>`, `Bilgic_<title>`, `MAC_<title>`, `Jan01.02`; a verse is `<textId>:<n>`.
- `proposalId`: first 12 hex chars of SHA-1 over `kind|entryId|target|key text`.

Repeated source sections use occurrence suffixes: a second stem with the same label has
`stemId` `<entryId>.<stem>~2`, and a repeated box with the same label and diathesis has
`boxId` `<stemId>.<d|t>.<box label slug>~2` (then `~3`, etc.). Example positions still
start at 1 within each box. Identical root labels are combined into one entry; later
root paragraphs are retained in `notes`, and their stem sections remain separate.

## Glossary (`IEntry`)

```ts
interface IEntry {
  id: string; // entryId
  root: string; // label as in the DOCX, e.g. "ḥwy 2"
  homonym: number | null;
  head: string; // the head paragraph verbatim (etymology, cross-references)
  crossRefs: string[]; // entryIds named by "see also", "→", "cf."
  notes: string[]; // other paragraphs before the stems (verbatim)
  stems: IStem[];
  idioms: IIdiom[]; // "Idiomatic phrases"
  source: { volume: string; order: number }; // DOCX file, position in it
}
interface IStem {
  id: string; // stemId
  stem: string; // "I", "II", "III", "Q", "Pa.", ...
  forms: string; // base forms as written, e.g. "səmle/soyəm"
  senses: ISense[]; // parsed from the numbered list; one unnumbered gloss = sense "1"
  sensesRaw: string; // the sense paragraph verbatim
  detransitiveSenses: ISense[];
  detransitiveSensesRaw: string | null;
  boxes: IBox[];
  notes: string[];
}
interface ISense {
  n: string;
  gloss: string;
} // n: "1", "2", "12"; gloss verbatim incl. "(???)"
interface IBox {
  id: string; // boxId
  label: string; // canonical: Preterit, Preterit Intransitive, ko-Preterit, Preterit-wa, Infectum,
  // Infectum-wa, Imperativ, Infinitiv, Part act., Part. Pass., Nomen actionis, ...
  rawLabel: string; // as written in the table cell
  detransitive: boolean;
  examples: IExample[];
}
interface IExample {
  id: string; // exampleId
  sense: string | null; // "1", "2"... as numbered in the box; null if unnumbered
  turoyo: string; // the Turoyo part (italic runs in the DOCX)
  translation: string | null; // source translation, without enclosing quotes/parentheses; unquoted text uses formatting or clear English syntax
  refs: IRef[];
  note: string | null; // trailing remarks (e.g. Russian working notes), verbatim
  raw: string; // the full example text verbatim
}
interface IRef {
  raw: string; // "24/46", "731", "prs 143/1", "JL 19.6.19", "MM 27", "[MT]"
  kind: "text" | "grammar-page" | "prs" | "jl" | "lb" | "mm" | "luf" | "other";
  textId: string | null; // corpus text if resolvable (e.g. "24/46" -> R024)
  verse: number | null;
}
interface IIdiom {
  id: string;
  raw: string;
  headword: string | null;
}
```

`index.json`: `[{ id, root, homonym, stems: [{ stem, forms }], glossPreview, exampleCount, volume }]`.
`glossPreview` is the first sense; for an entry without senses it is "see …" for a cross-reference
(`ʔkl → ʔxl`), otherwise the rest of the heading after the root.

Source strings are Unicode NFC, with outer whitespace trimmed and internal text preserved.
`head`, `sensesRaw`, `detransitiveSensesRaw`, `rawLabel`, example/idiom `raw`, and `notes`
together retain every non-empty source paragraph and physical table cell, including footnotes.
`notes` also retain literal stem and section headings, letter headings, and material whose
structure is uncertain. A leading section without a root label is kept in the first entry's
`notes`, rather than assigned an inferred root. Table rows within an idiom section are retained
as idiom `raw` text, with cells separated by newlines.
`source.order` is the 1-based OOXML body-block position of the first root paragraph in its volume.
Missing sense numbers and spelling are preserved; examples inherit a number within a numbered
group, but unnumbered groups have `sense: null`. Reference ranges remain one `IRef`, with
`verse` set to their first verse when resolved. Prym–Socin page/line references have both
`textId` and `verse` set to null.

## Corpus (`IText`)

```ts
interface IText {
  id: string;
  cite: string;
  title: string;
  collection: string;
  file: string;
  lang: "GERMAN" | "ENGLISH" | null; // translation language; null = untranslated
  translationSource?: "edition" | "machine" | null; // "machine": this project's translation (Jan Beṯ-Şawoce)
  verses: { v: number; tur: string; tr: string | null; rangeEnd?: number }[];
  reading?: "unread" | "partial" | "read";
  occurrences?: IOccurrence[]; // present once the text has been read
  alignment?: {
    v: number;
    status: "mismatch" | "partial" | "unsure";
    note: string;
  }[];
}
interface IOccurrence {
  v: number;
  form: string;
  entryId: string | null;
  root: string;
  stem: string;
  detransitive: boolean;
  box: string;
  sense: string; // "1", "D1", "new", "unclear"
  senseFit: "exact" | "stretched" | "none";
  meaning: string;
  arguments: string;
  observations: string | null;
  rq: string[];
  note: string | null; // reader's translation note, questions, entry issues
  newSenseGloss: string | null;
  newSenseType: string | null; // when sense = "new"
  decision: "add" | "no-add";
  criterion: string;
  proposalIds: string[];
  glossaryTarget?: { entryId: string; stemId?: string; sense?: string } | null;
}
```

`rangeEnd` preserves a printed combined passage (e.g. 97–99) under its first verse number;
the builder does not invent boundaries or duplicate its text. Other verse numbers are unchanged.
`glossaryTarget` is the validated reader link: an existing meaning, otherwise its stem, otherwise
its entry. Unknown roots have no target. Analysis labels remain separate from link destinations.
Proposal association uses the canonical root even when the root is only proposed and `entryId` is null.
Detransitive proposal targets and occurrence meanings use `D<n>` keys; source sense numbers stay raw.
Corrections are omitted when their targeted field changed since the agent's input snapshot, or when
their nonempty `before` span is absent. Array-valued legacy reference snapshots are joined with `; `.

## Proposals (`IProposal`)

```ts
type TProposalKind =
  | "new-sense"
  | "gloss-change"
  | "add-example"
  | "new-idiom"
  | "new-stem"
  | "new-form"
  | "new-root"
  | "move-example" // to another sense or box
  | "fix-citation" // wrong or ambiguous reference
  | "fix-text" // typo or transcription error in Turoyo, translation, gloss or forms
  | "fix-structure" // numbering, box label, duplicate example, misplaced paragraph
  | "duplicate-entry" // two entries for one verb
  | "note" // extension notes, research notes (not a change to the entry)
  | "question"; // for the editors or a native speaker
interface IProposal {
  id: string;
  entryId: string;
  kind: TProposalKind;
  stage: "synthesis" | "citation-check" | "proofreading";
  target: {
    stemId?: string;
    boxId?: string;
    exampleId?: string;
    sense?: string;
    field?: string;
  };
  summary: string; // one line, English
  before: string | null; // exact current text, for corrections
  after: string | null; // proposed text
  data: Record<string, unknown>; // kind-specific: gloss, label, extends, type, turoyo, translation, ref...
  rationale: string;
  evidence: { textId: string; v: number; cite: string }[];
  priority: 1 | 2 | 3; // 1 = new senses, research findings, real errors; 3 = cosmetic
  provenance: {
    model: string;
    effort: string;
    protocol: string;
    run: string;
    date: string;
  };
}
```
