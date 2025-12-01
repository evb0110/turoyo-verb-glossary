# Phase 1 Plan: Persist Verbs in Neon + Admin Export

This document describes the concrete steps for the first migration phase, assuming Neon Postgres and Drizzle are already configured for the project.

## Objectives

- All verbs currently available in the app are persisted in Neon Postgres in a well‑defined `verbs` table.
- The application reads verbs from Neon in all environments (dev and production).
- As an admin, you can:
  - trigger an export of **all verbs** from the database to local disk as:
    - one giant JSON file, and/or
    - a ZIP file containing per‑verb JSON files.
- Neon is the canonical store for verbs; DOCX and JSON are treated as historical/intermediate artifacts used only for ingestion and validation.

## Preconditions

- Neon database reachable via `NUXT_DATABASE_URL`.
- Drizzle is generating migrations via `server/db/schema.ts` and `drizzle.config.ts`.
- Parser pipeline (`parser/parse_docx_production.py` + JSON output) and the existing migration scripts are known to succeed on the current corpus.

## Step 1 – Align the `verbs` Schema

Goal: have a single, agreed‑upon schema for verbs across:

- Drizzle (`server/db/schema.ts` and `drizzle` migration files),
- `PostgresVerbDatabase` (Neon adapter),
- any one‑off migration scripts used to seed Neon.

Actions:

- Decide on the canonical Postgres schema, e.g.:
  - `root TEXT PRIMARY KEY`
  - `etymology JSONB`
  - `cross_reference TEXT`
  - `stems JSONB NOT NULL`
  - `idioms JSONB`
  - `created_at TIMESTAMP DEFAULT NOW()`
  - `updated_at TIMESTAMP DEFAULT NOW()`

- Update any existing migration scripts so they create the same `verbs` table signature as above (including `cross_reference` and `uncertain`) when seeding Neon directly.
- Update `PostgresVerbDatabase.ensureSchema()` to match the target schema exactly (or plan to remove runtime table creation once Drizzle migrations cover verbs).
- Add a `verbs` table definition to `server/db/schema.ts` and generate a Drizzle migration so the Neon schema is reproducible.

Handling etymology uncertainty:

- During migration from the existing JSON corpus:
  - For verbs where the original JSON has `uncertain: true`, add a short editorial note to the etymology (e.g. `etymology.notes` or similar) indicating that the etymology/root analysis was explicitly marked as tentative in the DOCX source.
  - After this one‑time migration, the standalone `uncertain` boolean can be dropped from the runtime schema and data model; all relevant information is preserved in the etymology notes.

Deliverables:

- A single documented schema for `verbs` in this repo.
- Drizzle migrations that create the `verbs` table in Neon.

## Step 2 – Load Current Verbs into Neon

Goal: Neon’s `verbs` table contains all verbs that the app currently serves from the parsed JSON corpus.

Actions:

- Choose the migration path:
  - Recommended: add a TypeScript/Node (or Python) migration that:
    - reads the parser JSON output,
    - validates it against the canonical `IVerb` schema,
    - inserts/upserts into Neon via Drizzle or the `PostgresVerbDatabase` adapter.
  - Existing SQLite‑based scripts may still be used once as a transitional mechanism, but the long‑term direction is to write directly to Postgres.

- Verify:
  - `COUNT(*)` in Neon’s `verbs` table matches the expected verb count.
  - Spot‑check a handful of roots against the JSON files or the UI for consistency.

Deliverables:

- Neon `verbs` table fully populated and verified.

## Step 3 – Ensure the App Uses Neon Everywhere

Goal: all app code that reads verbs does so via the Neon‑backed database, not `useStorage` or static JSON files.

Actions:

- Confirm that repositories under `server/repositories/verbs/` (`getVerbByRoot`, `getAllVerbs`, `getVerbRoots`, etc.) all use `getVerbDatabase()` with the Postgres adapter in production.
- Set environment variables appropriately:
  - `VERB_DATABASE=postgres`
  - `VERB_DATABASE_URL` (or `NUXT_DATABASE_URL`) pointing at Neon.
- For local development:
  - Decide whether to use Neon directly or a local Postgres instance.
  - Document recommended dev workflows in `.devkit/docs/DATABASE_QUICK_START.md`.

Deliverables:

- A single code path for reading verbs (via `IVerbDatabase`) backed by Neon in production.

## Step 4 – Admin Export Endpoint

Goal: provide a simple, safe way for an admin to dump all verb data from the database to disk as JSON.

API design:

- New route: `server/api/admin/verbs/export.get.ts`
- Behavior:
  - Requires admin via `requireAdmin(event)`.
  - Reads all verbs using the existing repository / `IVerbDatabase` abstraction.
  - Supports one or more formats via query params:
    - `format=single-json` → return a single JSON object containing all verbs (e.g. `{ verbs: [...] }`).
    - `format=zip-multi` → return a ZIP archive where each entry is `<root>.json`.
    - Default may be `single-json` or both, depending on convenience.
  - Sets `Content-Disposition: attachment; filename="verbs-YYYYMMDD.json"` (or `.zip`) so the browser downloads the file.

Implementation notes:

- For the ZIP format, use a Node‑compatible ZIP library or stream (e.g. `archiver`) in the API route.
- Ensure the export uses the canonical `IVerb` representation (what the app already expects), not raw DB rows with internal metadata.
- Keep the endpoint read‑only and side‑effect free.

Deliverables:

- Working admin‑only export endpoint returning:
  - a single JSON file of all verbs, and/or
  - a ZIP file of per‑verb JSON files.

## Step 5 – Admin UI Button

Goal: make the export flow one click for an admin user.

Actions:

- Choose placement:
  - Option A: Add an “Export verbs” button to the `AdminPageShell` header (`app/components/AdminPageShell.vue`) using the `header-actions` slot when on `/admin`.
  - Option B: Add a new “Tools” tab under `/admin` with a small panel for exports and other maintenance actions.

- Button behavior:
  - Calls the export API endpoint with the desired format, e.g.:
    - `GET /api/admin/verbs/export?format=single-json`
  - Uses a normal browser navigation / link (`<a href>`), not `fetch`, so the response is downloaded directly.
  - Optionally shows a brief explanation (e.g. “Exports the current Neon verbs as JSON. This is a snapshot, not a canonical source.”).

Deliverables:

- Visible “Export verbs” control in the admin UI for authorized users.

## Step 6 – Validation and Rollout

Goal: ensure Phase 1 doesn’t introduce regressions and that exports are trustworthy.

Actions:

- After migration, run:
  - Root search, full‑text search, and stats APIs against Neon and compare with pre‑migration behavior.
  - Spot‑check several verb pages in the UI.
- Test the export:
  - Download the single JSON export, count verbs, and compare with Neon `COUNT(*)`.
  - Optionally, feed the export back into a local dev environment as a sanity check (e.g. import into a temporary Postgres instance or use for offline analysis).
- Document in `.devkit/docs`:
  - How to re‑run the migration.
  - How to use the admin export.

Deliverables:

- Confidence that all verbs are in Neon, the app is reading from Neon, and admins can safely export the current dataset to JSON/ZIP.
