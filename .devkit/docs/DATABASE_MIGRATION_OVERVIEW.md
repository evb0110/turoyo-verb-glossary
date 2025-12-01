# Database Migration Overview: DOCX History → Neon Canonical Store

This document updates and complements `DATABASE_ARCHITECTURE.md` and `database-migration-plan.md`. It captures the high‑level direction for verbs data going forward.

## Goals and Constraints

- Use Neon Postgres as the **ultimate source of truth** for all verb data, not just at runtime.
- Treat DOCX files as **historical sources and ingestion inputs** that become obsolete for application logic once data is in the database.
- Treat parser JSON as **intermediate artifacts** that can be regenerated as needed.
- Avoid supporting arbitrary document structures: we define a schema, then extend it cautiously over time.

## Sources of Truth

- **Historical source material**: `.devkit/new-source-docx/*.docx`
  - Reflects the original editorial corpus.
  - Used by the parser to produce structured verb data.
  - After successful ingestion into Neon, DOCX is no longer consulted by the app or APIs.

- **Canonical store (long‑term)**: Neon Postgres (accessed via Drizzle / Neon client)
  - `verbs` table holds all verbs the application serves.
  - Nuxt app, search, stats, and future editing all operate on this table.
  - We only dump from Neon for backup/export purposes; imported data is considered authoritative.

- **Derived artifacts**:
  - Parser JSON output (per‑verb) during ingestion and validation.
  - On‑demand JSON exports from the database (admin tools / backups).

Neon is the **canonical store** for verbs after migration. DOCX and JSON are useful but non‑authoritative once data is in the database.

## Target Data Flow

The long‑term pipeline is:

```text
DOCX (historical) → parser → typed JSON (ephemeral) → Neon Postgres (canonical) → Nuxt app / API
```

- JSON files produced by the parser are **intermediate**:
  - Used for validation, inspection, and ingestion.
  - Safe to delete once the corresponding data is confirmed in Neon.
- The Nuxt application:
  - Reads verbs from Neon via the `IVerbDatabase` abstraction.
  - Writes edits back to Neon only, never directly to DOCX.

## Schema Strategy

- **Canonical TypeScript schema**:
  - Use the existing `IVerb`, `IStem`, `IExample`, `IEtymology`, etc. as the starting point.
  - Clean up inconsistencies so that every verb can be expressed in this shape.
  - Introduce `schema_version` if/when we need breaking changes.

- **Database representation** (target shape):
  - `verbs` table with columns along the lines of:
    - `root TEXT PRIMARY KEY`
    - `etymology JSONB`
    - `cross_reference TEXT`
    - `stems JSONB NOT NULL`
    - `idioms JSONB`
    - `created_at TIMESTAMP DEFAULT NOW()`
    - `updated_at TIMESTAMP DEFAULT NOW()`
  - Managed via Drizzle migrations so the schema is reproducible.
  - Accessed in runtime through the existing `IVerbDatabase` abstraction (which can evolve to use Drizzle under the hood).

- **Etymology uncertainty (no separate boolean)**:
  - The DOCX corpus marks a very small number of verbs (≪ 1%) with `???` in the root+etymology line to indicate that the **etymology or root analysis is provisional**.
  - Instead of a dedicated `uncertain` boolean column, this signal is captured as an **editorial note on the etymology**, e.g. in `etymology.notes` or a similar metadata field.
  - This keeps the schema simpler while still preserving the information needed for future editorial work or specialized UI hints.

- **No arbitrary documents**:
  - Every verb row conforms to the canonical `IVerb` schema.
  - We may keep a small `extras`/`metadata` JSONB column for rare fields, but do not attempt to store completely arbitrary shapes.

## Phased Roadmap (High‑Level)

- **Phase 0 – Design and Alignment**
  - Finalize the canonical `IVerb` schema and invariants.
  - Define the target `verbs` table in Drizzle and ensure Neon and the runtime adapters all agree on column names and types.
  - Decide on any `schema_version` or `extras` fields up‑front.

- **Phase 1 – Persist Verbs in Neon + Admin Export**
  - Load all existing parsed verbs into Neon’s `verbs` table.
  - Ensure the app reads verbs from Neon in all environments.
  - Add an admin‑only export that can dump all verbs to:
    - a single giant JSON file, and/or
    - a ZIP archive of per‑verb JSON files.

- **Phase 2 – Editing UI and API**
  - Add API endpoints for editing verbs (CRUD over `IVerb`).
  - Build admin UI for safe editing of the canonical fields (roots, stems, examples, etc.).
  - Add validation to guarantee stored verbs conform to the `IVerb` schema.

- **Phase 3 – Advanced Features**
  - Improve full‑text search and indexing in Postgres (e.g. tsvector or JSONB GIN indexes).
  - Introduce verb versioning / history if needed.
  - Explore automated or semi‑automated pathways from edited DB content back into DOCX (if desired), or document that editing is database‑only.

## Relationship to Existing Docs

- `DATABASE_ARCHITECTURE.md` describes the current adapter‑based database design; this document clarifies the long‑term split between DOCX (raw) and Neon (runtime).
- `database-migration-plan.md` assumed we might delete the DOCX and parser once JSON is in the database; this new overview clarifies that **Neon is the canonical store** and DOCX/JSON are historical or intermediate.
