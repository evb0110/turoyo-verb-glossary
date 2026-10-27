# Editorial review storage

`proposal_decision` has one current team decision per proposal. Its primary key is the static proposal ID;
`id` identifies the active decision event. It stores the entry ID, verdict (`accept`, `reject`, `discuss`),
optional comment, optional structured wording edit, reviewer ID/name snapshot and decision date.

`proposal_review_event` holds every decision snapshot and undo event. Saves record the preceding active
review ID. Undo records the undone review ID and restores the preceding snapshot, or removes the current
row if none existed. Application writes never delete audit events. Reviewer deletion sets the user ID to
null and retains the name, wording, decisions and history. Session/activity deletion keeps its existing
cascade behavior; editorial audit is independent of activity logs.

The `save_proposal_decision` and `undo_proposal_decision` PostgreSQL functions each execute as one Neon HTTP
statement/transaction. Both acquire the same advisory transaction lock for their proposal, including when
no current row exists. Concurrent proposals proceed independently. Undo requires the current review ID and
its reviewer ID, so a stale or foreign undo returns HTTP 409 without changing either table. Restoring an old
decision restores its original ID, author, date, comment and structured edit, allowing successive undo.

`GET /api/glossary/reviews` reads only the current table, with no history reconstruction or user join.
The summary therefore reads at most one row per decided proposal rather than every historical decision.
The home personal count means current decisions attributed to that user. The review queue uses current team
decisions. A removed static proposal is ignored by summary counts but its decision remains exportable.
`GET /api/glossary/reviews/:proposalId` lazily returns the most recent 100 audit events for a single card;
the UI states that limit. History is not downloaded with the queue or summary.

## Edited accepts

`IProposalEdit` stores `{ text, translation?, headword? }`, preserving separate text fields for additions.
The original proposal remains immutable. An edited accept has verdict `accept` plus non-null `edited`;
plain acceptance has null `edited`. Clients submit `acceptWithChanges: true` and `edited` together.
The server rejects missing or unknown fields, edits on other verdicts, and edits on notes/questions.
Text must contain 1–20,000 UTF-16 code units after trimming. A translation may be empty but is capped at
20,000; an idiom heading is required when offered and capped at 5,000. Comments remain optional and capped
at 5,000. SQL checks additionally constrain comments, edited-accept verdicts, non-empty text and total edit
JSON size (200,000 bytes). The accepted wording and reviewer are shown separately from the machine suggestion.

| Proposal kind      | Editable wording                                                                                                |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| `add-example`      | Turoyo example and translation                                                                                  |
| `new-form`         | Turoyo example establishing the form and translation                                                            |
| `new-idiom`        | Idiom heading, Turoyo example and translation                                                                   |
| `new-sense`        | Gloss (`data.gloss`)                                                                                            |
| `gloss-change`     | Replacement gloss (`after`)                                                                                     |
| `new-stem`         | Stem forms (`data.forms`); stem identity stays attached to the proposal                                         |
| `new-root`         | Complete proposed wording shown in `after`; nested machine data remains evidence, not an editable JSON form     |
| `fix-text`         | Exact replacement span in `after`, not an expanded whole-paragraph diff                                         |
| `fix-citation`     | Replacement reference in `after`                                                                                |
| `fix-structure`    | `after` when present; otherwise proposed wording from `data.turoyo`, `data.forms`, `data.gloss`, or the summary |
| `move-example`     | `after` when present, otherwise editor instructions from the summary; stable target IDs stay attached           |
| `duplicate-entry`  | `after` when present, otherwise editor instructions from the summary; stable target IDs stay attached           |
| `note`, `question` | No glossary replacement wording; retain Noted, Dismiss, Discuss later and comments                              |

If a proposal supplies `data.translation`, it is also editable as a separate field. For additions which
supply `after`, that visible wording takes precedence over `data.turoyo`. Re-editing an accepted card starts
with its accepted wording. Cancel discards only the draft. Unedited acceptance can still approve a machine
proposal whose `after` is empty (deletion). An edited accept requires explicit non-empty replacement wording.

## Other schema decisions

- All timestamps use `timestamptz`; migration interprets old timezone-free values as UTC explicitly.
- Session/account user indexes support auth lookups and foreign-key cleanup; provider/account and verification identifier indexes support auth identity lookups.
- Activity indexes cover recent events and user/session/type/host filters used by admin queries.
- Session activity indexes cover recent sessions and per-user recent sessions.
- Activity checks reject invalid HTTP status codes, negative result counts and negative counters.
- Review keys prevent duplicate current decisions; history indexes cover proposal/date lookup and reviewer foreign keys.
- Legacy `verbs` is retained, including its rows, to avoid an unnecessary destructive change; the site does not read it.
- Activity data retains existing session/user cascades; durable editorial decisions use `ON DELETE SET NULL` instead.
- No full-text database index or extension was added: glossary search uses static assets, and the small admin substring searches span several tables.

## Migration and runtime bootstrap

`drizzle/0006_editorial_decisions.sql` was generated with Drizzle Kit, then extended to copy all old reviews
and their predecessor links before dropping `proposal_review`, convert timestamps with an explicit UTC
`USING` expression, and install the atomic review functions. The snapshot and journal describe the new schema.
The complete migration is transactionally guarded by the `glossary_review_schema_v6()` marker, created last.
Thus a later Drizzle CLI migration safely records 0006 if runtime ensure already applied it.

`ensureDatabaseSchema()` (`server/db/`) replaces the old review-table-only ensure. The first server middleware,
`server/middleware/0.databaseSchema.ts`, awaits it on every request before authentication reads the user and
session tables, so a fresh database is usable from the first sign-in. Its bundled SQL bootstraps missing
0000–0005 tables and applies the exact 0006 block. It acquires a schema advisory transaction lock, checks
the version marker and commits the entire upgrade atomically. Concurrent instances cannot race table/type
creation. On an already migrated database it performs one guarded database statement per cold instance;
subsequent calls share a memoized promise. Failure clears that promise so the next request can retry.
Keep the bundled 0006 block in `server/db/databaseSchemaSql.ts` in sync with the migration file.
Production uses this runtime path because its connection string cannot be pulled locally.

The development database originally had the 0005 review table but no legacy `verbs` table or Drizzle
migration journal. Verification restored the missing 0004 table, verified/applied 0006, baselined existing
0000–0005 migration journal entries, and ran the actual Drizzle migrator for guarded 0006 twice. It does
not contain test review decisions after verification.

## Admin downloads

`GET /api/admin/decisions?format=csv|json` requires an approved admin. `/admin` has both download links.
Every current decision includes proposal ID, verb, kind, target IDs/field and evidence citations, machine
wording, edited wording, verdict, comment, reviewer ID/name and date. Each needed static entry's proposals
are read once per export. Missing static proposals are labeled `unavailable`, with their saved decision
preserved. JSON keeps structured edit fields. CSV quotes values, doubles embedded quotes, uses UTF-8 with
BOM and CRLF, and prefixes potential spreadsheet formulas with an apostrophe. JSON retains the exact values.
Review/history/export responses use `private, no-store`. The dev auth bypass uses an equivalent in-memory
current/event store and never writes reviews to Neon.

`GET /api/glossary/export/decisions?format=docx|pdf` writes the same rows (from `getProposalDecisionExport`, which
also carries each decision's entry ID) as a Word or PDF document for the editors, grouped by letter, root and stem,
with the suggestion, verdict, edited wording, comment, reviewer and date. Any approved user may download it: every
approved user already sees each decision, reviewer, comment and edit on the site and through
`/api/glossary/reviews`, and the document omits the reviewer IDs that the admin CSV/JSON carry. It is never cached.
