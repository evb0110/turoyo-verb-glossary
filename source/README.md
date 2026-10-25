# Primary sources

Everything the glossary data is derived from. Files here are never edited: a new version of a
source goes into a new dated folder next to the old one, and the parsers are pointed at it.

## In this repository

### `glossary-docx/` — the Turoyo Verb Glossary (Word, current)

The team's working files, 7 volumes split by initial letter. Each snapshot folder is named by the
date of its newest file. This is the authoritative source for `parser/parse_docx_production.py`
(see `PARSING.md`).

**Snapshot `2026-10-21/`** (received 2026-10-25 as `Alphabetized.zip`):

| File                       | Last edited | SHA-256                                                            |
| -------------------------- | ----------- | ------------------------------------------------------------------ |
| `1. ʔ, ʕ, b, č.docx`       | 2026-10-21  | `5eabfb40eee8e197d57341373f109c582b73fc62584cece3c89aad01b67e211a` |
| `2. d, f, g, ġ, ǧ.docx`    | 2026-08-07  | `4f862baffa2b0052bf4c45dcc53991830ab3c864a509bfa64fcd3c36d22e5412` |
| `3. h,ḥ,k.docx`            | 2026-02-12  | `3137a2084018e92a8e674f7424849aa5bd97c689e8f1276e76e42a3dfd05dfaf` |
| `4. l,m,n,p.docx`          | 2026-09-26  | `396b553f85089b42b221239f82d65f47c8ef1254f833d29394d0cfa9511f5a57` |
| `5. q,r,s,ṣ.docx`          | 2026-09-23  | `f3b5a2b7ee2228cc805ea9f0d71669353933d28ab0a06f5a2aff657988574b7f` |
| `6. š,t,ṭ,ṯ.docx`          | 2026-10-06  | `c7286c26dac6c62c8c5b20671710f3eaa8506e04f425af25425b0dba3b59dad8` |
| `7. v, w, x, y, z, ž.docx` | 2026-10-06  | `65039c586e7b4fcb29a8a7b4180a8d0fb7a88fa9eddd9521fa9c2e94f9323b8f` |

### `glossary-html/` — the glossary as one HTML export (2024, superseded)

`Turoyo_all_2024.html` (SHA-256 `b7103a070ded9d065d61de12afe96315af8e179551bed72fe19f10dc7e4efd5c`),
the single-file export the first parser (`parser/parse_verbs.py`) read. The DOCX volumes replaced
it in October 2025; it is kept as the record of the glossary's 2024 state.

## Elsewhere

| Source                                                                                                                             | Location                                                                                                                                           | Notes                                                |
| ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Text corpus (Ritter, Prym–Socin, Jastrow, Talay, Lahdo, Bilgiç, Hors, MAC, Jan Beṯ-Şawoce), Turoyo with the editions' translations | private repository `evb0110/aramaictexts`, `source/corpus_turoyo/` (`<collection>/` and `<collection> TRANS/`, one file per text, numbered verses) | Read by the agent pipeline under `.devkit/analysis/` |
| Ritter's Turoyo dictionary (nouns, particles), Jastrow's and Jan Beṯ-Şawoce's dictionaries                                         | `evb0110/aramaictexts`, `source/dictionaries_turoyo/` (`ritter.txt`, `jastrow.txt`, `jan.txt`)                                                     | Third-party works; kept in the private repository    |
| Earlier glossary snapshots, 2014–2016                                                                                              | `~/Desktop/Personal/Linguae/Turoyo/backup/` and `TUROYO_VERB_GLOSSARY_2016/` on the Mac                                                            | Historical only                                      |
