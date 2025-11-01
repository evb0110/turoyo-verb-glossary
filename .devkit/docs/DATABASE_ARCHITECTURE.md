# Database Architecture - Verb Glossary

## Overview

The Turoyo Verb Glossary now uses a database adapter pattern to support multiple database backends (SQLite and Neon Postgres). This architecture enables easy switching between databases and prepares for future user-editable verbs.

## Problem Solved

**Original Issue**: 1,498 individual JSON files in `server/assets/verbs/` caused macOS kqueue exhaustion:
- Total watched files: 10,639 (1,498 verbs + 9,141 source files)
- macOS kqueue limit: ~8,000-12,000 files
- Result: `spawn EBADF` error crashing dev server

**Solution**: Consolidate 1,498 JSON files into single SQLite database:
- Reduces watched files from 10,639 to 9,142
- Below kqueue threshold
- Eliminates spawn EBADF error

## Architecture

### Three-Stage Pipeline

```
DOCX (source) → JSON (intermediate) → Database (runtime) → Application
```

1. **DOCX → JSON**: Parser converts source DOCX files to JSON
   - Source: `.devkit/new-source-docx/*.docx`
   - Parser: `parser/parse_docx_production.py`
   - Output: `server/assets/verbs/*.json`

2. **JSON → Database**: Migration script loads JSON into database
   - Script: `scripts/migrate_json_to_sqlite.py`
   - Output: `.data/db/verbs.db` (SQLite) or Neon Postgres

3. **Database → Application**: Adapters provide data to application
   - Adapters: `server/db/verbs/adapters/`
   - Factory: `server/db/verbs/VerbDatabaseFactory.ts`
   - Singleton: `server/db/verbs/index.ts`

### Adapter Pattern

The adapter pattern allows runtime switching between database backends:

```typescript
// Interface defines contract
export interface IVerbDatabase {
    findByRoot(root: string): Promise<IVerbRow | null>
    findAll(): Promise<IVerbRow[]>
    searchByRoot(query: string): Promise<IVerbRow[]>
    getRoots(): Promise<string[]>
    count(): Promise<number>
    upsertVerb(verb: Omit<IVerbRow, 'createdAt'>): Promise<void>
    upsertMany(verbs: Omit<IVerbRow, 'createdAt'>[]): Promise<void>
    deleteAll(): Promise<void>
    close(): Promise<void>
}

// Implementations
class SqliteVerbDatabase implements IVerbDatabase { ... }
class PostgresVerbDatabase implements IVerbDatabase { ... }

// Factory creates appropriate adapter
export class VerbDatabaseFactory {
    static create(type?: VerbDatabaseType): IVerbDatabase {
        const dbType = type || process.env.VERB_DATABASE || 'sqlite'
        // Returns SQLite or Postgres adapter
    }
}

// Singleton provides application-wide instance
let verbDatabase: IVerbDatabase | null = null

export function getVerbDatabase(): IVerbDatabase {
    if (!verbDatabase) {
        verbDatabase = VerbDatabaseFactory.create()
    }
    return verbDatabase
}
```

## File Structure

```
server/db/verbs/
├── types.ts                           # TypeScript type definitions
├── IVerbDatabase.ts                   # Interface contract
├── VerbDatabaseFactory.ts             # Factory for creating adapters
├── index.ts                           # Singleton access pattern
└── adapters/
    ├── SqliteVerbDatabase.ts          # SQLite implementation
    └── PostgresVerbDatabase.ts        # Postgres implementation

scripts/
├── migrate_json_to_sqlite.py          # JSON → SQLite migration
└── migrate_sqlite_to_postgres.py      # SQLite → Postgres migration

.data/db/
└── verbs.db                           # SQLite database (2.86 MB, 1,498 verbs)

server/assets/verbs/
└── *.json                             # 1,498 individual JSON files (kept for parser output)
```

## Database Schemas

### SQLite Schema

```sql
CREATE TABLE verbs (
    root TEXT PRIMARY KEY,
    etymology TEXT,              -- JSON serialized
    stems TEXT NOT NULL,         -- JSON serialized
    idioms TEXT,                 -- JSON serialized
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX idx_root ON verbs(root);
CREATE INDEX idx_root_search ON verbs(root COLLATE NOCASE);

PRAGMA journal_mode=WAL;  -- Better concurrency
```

### Postgres Schema

```sql
CREATE TABLE verbs (
    root TEXT PRIMARY KEY,
    etymology JSONB,             -- Native JSONB (no serialization)
    stems JSONB NOT NULL,
    idioms JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_root ON verbs(root);
CREATE INDEX idx_etymology_gin ON verbs USING GIN(etymology);  -- Fast JSONB queries
```

## Configuration

### Environment Variables

```bash
# Database type (sqlite or postgres)
VERB_DATABASE=sqlite

# SQLite path (default: .data/db/verbs.db)
VERB_DATABASE_PATH=.data/db/verbs.db

# Postgres connection string (required if VERB_DATABASE=postgres)
VERB_DATABASE_URL=postgresql://user:pass@host/db
```

### Switching Databases

**Development (SQLite)**:
```bash
# Default - uses local SQLite database
pnpm dev
```

**Production (Neon Postgres)**:
```bash
# Set environment variable
export VERB_DATABASE=postgres
export VERB_DATABASE_URL="postgresql://..."

# Deploy
pnpm run build
```

## Migration Workflows

### Parser → SQLite (Common Workflow)

```bash
# Using Makefile
make deploy-verbs

# Manual steps
python3 parser/parse_docx_production.py        # DOCX → JSON
python3 scripts/migrate_json_to_sqlite.py      # JSON → SQLite
```

### SQLite → Postgres (Future Migration)

```bash
# Prerequisites
pip3 install psycopg2-binary

# Set environment
export VERB_DATABASE_URL="postgresql://..."

# Run migration
python3 scripts/migrate_sqlite_to_postgres.py

# Update production
export VERB_DATABASE=postgres
```

## Repository Updates

Five repository files were updated to use the adapter pattern:

### Before (Storage-based)

```typescript
// server/repositories/verbs/getVerbByRoot.ts
import type { IVerb } from '#shared/types/IVerb'

export async function getVerbByRoot(root: string) {
    const storage = useStorage('assets:server')
    return storage.getItem<IVerb>(`verbs/${root}.json`)
}
```

### After (Adapter-based)

```typescript
// server/repositories/verbs/getVerbByRoot.ts
import { getVerbDatabase } from '~~/server/db/verbs'

export async function getVerbByRoot(root: string) {
    const db = getVerbDatabase()
    return db.findByRoot(root)
}
```

### Updated Files

1. `server/repositories/verbs/getVerbByRoot.ts` - findByRoot()
2. `server/repositories/verbs/getAllVerbs.ts` - findAll()
3. `server/repositories/verbs/getVerbRoots.ts` - getRoots()
4. `server/repositories/verbs/getVerbFiles.ts` - getRoots() + map to file paths
5. `server/services/searchRoots.ts` - getRoots() + findByRoot() in batches

## Benefits

### Performance

- **SQLite**: Fast local queries, zero network latency
- **Postgres**: GIN indexes for JSONB, optimized for complex queries
- **Both**: Single database file vs 1,498 individual files (reduced I/O)

### Developer Experience

- **Easy switching**: Single environment variable
- **Type safety**: Interface contract enforced at compile time
- **Testing**: Swap in mock database adapter
- **Migration**: Idempotent scripts, safe to re-run

### Future-Ready

- **User-editable verbs**: Postgres ready for production use
- **Multi-user**: Neon Postgres supports concurrent writes
- **Scalability**: Serverless Postgres auto-scales
- **Consistency**: ACID transactions prevent data corruption

## Testing

### Verify Migration

```bash
# Check database was created
ls -lh .data/db/verbs.db

# Check verb count
sqlite3 .data/db/verbs.db "SELECT COUNT(*) FROM verbs;"
# Expected: 1498

# Check sample verb
sqlite3 .data/db/verbs.db "SELECT root FROM verbs WHERE root = 'hyw 1';"
```

### Test API Endpoints

```bash
# Start dev server
pnpm dev

# Test getVerbByRoot
curl "http://localhost:3456/api/verbs/hyw%201"

# Test verb count
curl "http://localhost:3456/api/stats/verbs"

# Test search
curl "http://localhost:3456/api/verbs?q=h&type=roots"
```

## Troubleshooting

### spawn EBADF Error

**Cause**: Too many files being watched by Vite/Nitro (macOS kqueue exhaustion)

**Solution**: Migration to SQLite reduces watched files below threshold

**Verify**:
```bash
# Count total files in project
find . -type f | wc -l

# Should be ~9,142 (below 10,000 threshold)
```

### better-sqlite3 Build Scripts

**Warning**: `pnpm` may show "Ignored build scripts" warning

**Solution**: Approve builds if needed:
```bash
pnpm approve-builds better-sqlite3
```

Or use pre-built binaries (usually works without approval)

### Database Locked Error (SQLite)

**Cause**: Multiple connections writing simultaneously

**Solution**: SQLite uses WAL mode for better concurrency
```bash
# Check WAL mode is enabled
sqlite3 .data/db/verbs.db "PRAGMA journal_mode;"
# Should output: wal
```

## Next Steps

### Immediate (Development)

1. ✅ Migrate JSON to SQLite
2. ✅ Configure environment variables
3. ⏳ Test dev server with SQLite
4. ⏳ Verify spawn EBADF is fixed

### Future (Production)

1. Migrate SQLite to Neon Postgres
2. Update Vercel environment variables
3. Test user-editable verbs functionality
4. Add optimistic UI updates for edits

## Related Documentation

- **Parser Documentation**: `.devkit/analysis/FINAL_PRODUCTION_SUMMARY.md`
- **Etymology Extraction**: `.devkit/analysis/ETYMOLOGY_100_PERCENT.md`
- **Parser Development**: `.devkit/analysis/BREAKTHROUGH_REPORT_V3.md`
- **Makefile Workflows**: `Makefile`
- **Migration Scripts**: `scripts/migrate_json_to_sqlite.py`, `scripts/migrate_sqlite_to_postgres.py`
