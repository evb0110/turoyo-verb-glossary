# Database Quick Start Guide

## What Changed?

**Before**: 1,498 individual JSON files in `server/assets/verbs/` causing `spawn EBADF` error

**After**:
- JSON files moved to `.devkit/analysis/docx_v2_verbs/` (not watched by Nitro)
- Single SQLite database at `.data/db/verbs.db` (2.7 MB)
- Server/assets/verbs/ directory empty (no files watched)

## Quick Commands

### Development Workflow

```bash
# Run parser + migrate to SQLite
make deploy-verbs

# Or step by step:
python3 parser/parse_docx_production.py    # Parse DOCX → JSON
python3 scripts/migrate_json_to_sqlite.py  # Migrate JSON → SQLite

# Start dev server
pnpm dev

# Test API
curl "http://localhost:3456/api/verbs/hyw%201"
```

### Configuration

```bash
# .env file
VERB_DATABASE=sqlite
VERB_DATABASE_PATH=.data/db/verbs.db
```

### Database Info

```bash
# Check database size
ls -lh .data/db/verbs.db

# Check verb count
sqlite3 .data/db/verbs.db "SELECT COUNT(*) FROM verbs;"

# View sample verb
sqlite3 .data/db/verbs.db "SELECT root, json_extract(etymology, '$.language') FROM verbs LIMIT 5;"
```

## Future Migration to Postgres

```bash
# Install dependency
pip3 install psycopg2-binary

# Set environment
export VERB_DATABASE_URL="postgresql://user:pass@host/db"

# Run migration
python3 scripts/migrate_sqlite_to_postgres.py

# Update production
export VERB_DATABASE=postgres
```

## Architecture

```
┌─────────────┐
│ DOCX Files  │ (source)
└──────┬──────┘
       │ parser/parse_docx_production.py
       ↓
┌─────────────┐
│ JSON Files  │ (intermediate)
└──────┬──────┘
       │ scripts/migrate_json_to_sqlite.py
       ↓
┌─────────────┐
│  SQLite DB  │ (runtime)
└──────┬──────┘
       │ server/db/verbs/adapters/SqliteVerbDatabase.ts
       ↓
┌─────────────┐
│ Application │
└─────────────┘
```

## Files Created/Modified

### Created
- `server/db/verbs/types.ts` - Type definitions
- `server/db/verbs/IVerbDatabase.ts` - Interface contract
- `server/db/verbs/VerbDatabaseFactory.ts` - Factory pattern
- `server/db/verbs/index.ts` - Singleton access
- `server/db/verbs/adapters/SqliteVerbDatabase.ts` - SQLite adapter
- `server/db/verbs/adapters/PostgresVerbDatabase.ts` - Postgres adapter
- `scripts/migrate_json_to_sqlite.py` - JSON → SQLite migration
- `scripts/migrate_sqlite_to_postgres.py` - SQLite → Postgres migration
- `Makefile` - Workflow automation
- `.data/db/verbs.db` - SQLite database (2.86 MB, 1,498 verbs)
- `.env.example` - Environment variable template

### Modified
- `server/repositories/verbs/getVerbByRoot.ts` - Use adapter
- `server/repositories/verbs/getAllVerbs.ts` - Use adapter
- `server/repositories/verbs/getVerbRoots.ts` - Use adapter
- `server/repositories/verbs/getVerbFiles.ts` - Use adapter
- `server/services/searchRoots.ts` - Use adapter
- `.env` - Added VERB_DATABASE config
- `package.json` - Added better-sqlite3 dependency

## Testing Checklist

- [ ] Dev server starts without `spawn EBADF` error
- [ ] Verb API returns data: `curl http://localhost:3456/api/verbs/hyw%201`
- [ ] Stats API works: `curl http://localhost:3456/api/stats/verbs`
- [ ] Search works: `curl "http://localhost:3456/api/verbs?q=h&type=roots"`
- [ ] Database has 1,498 verbs: `sqlite3 .data/db/verbs.db "SELECT COUNT(*) FROM verbs;"`

## Troubleshooting

**Server won't start?**
- Check file count: `find . -type f | wc -l` (should be < 10,000)
- Check database exists: `ls -la .data/db/verbs.db`

**Database errors?**
- Re-run migration: `python3 scripts/migrate_json_to_sqlite.py`
- Check WAL mode: `sqlite3 .data/db/verbs.db "PRAGMA journal_mode;"`

**Missing verbs?**
- Check count: `sqlite3 .data/db/verbs.db "SELECT COUNT(*) FROM verbs;"`
- Re-run parser + migration: `make deploy-verbs`

## Next Steps

1. **Test**: Start dev server and verify endpoints work
2. **Commit**: `git add .data/db/verbs.db && git commit -m "Add SQLite verb database"`
3. **Deploy**: `git push` (Vercel will use SQLite database)
4. **Future**: Migrate to Postgres when ready for user-editable verbs

## Documentation

- Full architecture: `.devkit/docs/DATABASE_ARCHITECTURE.md`
- Parser details: `.devkit/analysis/FINAL_PRODUCTION_SUMMARY.md`
