# Data Pipeline Summary

## Current Status ✅

**All verb data is in SQLite database and ready for use!**

- **Database:** `.data/db/verbs.db` (2.7 MB)
- **Verb count:** 1,498 verbs
- **Source files:** 7 DOCX files in `.devkit/new-source-docx/`
- **Intermediate JSON:** 1,498 files in `.devkit/analysis/docx_v2_verbs/`

## Complete Pipeline

```
┌─────────────────────────────────────────────┐
│  DOCX Source Files (7 files)                │
│  .devkit/new-source-docx/*.docx             │
│  - Organized by letter                      │
│  - Proprietary source (not in Git)          │
└──────────────────┬──────────────────────────┘
                   │
                   │ python3 parser/parse_docx_production.py
                   ↓
┌─────────────────────────────────────────────┐
│  JSON Files (1,498 files)                   │
│  .devkit/analysis/docx_v2_verbs/*.json      │
│  - One file per verb                        │
│  - Includes etymology, stems, examples      │
│  - NOT watched by Vite (in .devkit)         │
└──────────────────┬──────────────────────────┘
                   │
                   │ python3 scripts/validate_parsing_completeness.py
                   │ ✅ 99.21% word coverage
                   ↓
┌─────────────────────────────────────────────┐
│  Validation Report                          │
│  .devkit/analysis/parsing_validation_report.json│
│  - Ensures no data loss                     │
│  - Compares ALL DOCX text vs JSON text     │
│  - Reports missing words and coverage       │
└──────────────────┬──────────────────────────┘
                   │
                   │ python3 scripts/migrate_json_to_sqlite.py
                   ↓
┌─────────────────────────────────────────────┐
│  SQLite Database (1 file, 2.7 MB)           │
│  .data/db/verbs.db                          │
│  - 1,498 verbs                              │
│  - Indexed for fast queries                 │
│  - NOT watched by Vite (in .data)           │
└──────────────────┬──────────────────────────┘
                   │
                   │ server/db/verbs/adapters/SqliteVerbDatabase.ts
                   ↓
┌─────────────────────────────────────────────┐
│  Application (Nuxt API routes)              │
│  - GET /api/verbs/:root                     │
│  - GET /api/verbs (search)                  │
│  - GET /api/stats/verbs                     │
└─────────────────────────────────────────────┘
```

## Running the Pipeline

### Step 1: Parse DOCX to JSON

```bash
# Parse all 7 DOCX files into individual JSON files
python3 parser/parse_docx_production.py

# Output:
# - .devkit/analysis/docx_v2_parsed.json (combined)
# - .devkit/analysis/docx_v2_verbs/*.json (1,498 individual files)
```

**Parser features:**
- 100% etymology extraction
- 101% translation extraction (better than HTML parser)
- Automated homonym numbering
- Contextual root detection
- Handles combining diacritics (e.g., ḏ̣)

### Step 2: Migrate JSON to SQLite

```bash
# Convert JSON files to SQLite database
python3 scripts/migrate_json_to_sqlite.py

# Output:
# - .data/db/verbs.db (2.7 MB, 1,498 verbs)
# - WAL journal mode enabled for concurrency
# - Indexes created for fast queries
```

**Migration features:**
- Idempotent (safe to re-run)
- Upserts existing verbs
- Progress reporting (every 100 verbs)
- Validates all data before commit

### Step 3: Use in Application

```bash
# Start dev server
pnpm dev

# Database automatically loaded via adapter pattern
# No manual deployment needed
```

## Quick Commands

```bash
# Full pipeline (parse + validate + migrate)
python3 parser/parse_docx_production.py && \
python3 scripts/validate_parsing_completeness.py && \
python3 scripts/migrate_json_to_sqlite.py

# Check database status
sqlite3 .data/db/verbs.db "SELECT COUNT(*) FROM verbs;"

# Sample random verbs
sqlite3 .data/db/verbs.db "SELECT root, etymology FROM verbs ORDER BY RANDOM() LIMIT 5;"

# Check database size
ls -lh .data/db/verbs.db

# Verify JSON files
ls .devkit/analysis/docx_v2_verbs/*.json | wc -l

# Run validation only
python3 scripts/validate_parsing_completeness.py
```

## Database Schema

```sql
CREATE TABLE verbs (
    root TEXT PRIMARY KEY,
    etymology TEXT,           -- JSON: IEtymology
    cross_reference TEXT,     -- Cross-references
    stems TEXT NOT NULL,      -- JSON: IStem[]
    uncertain INTEGER DEFAULT 0  -- Boolean flag
);

CREATE INDEX idx_root ON verbs(root);
CREATE INDEX idx_root_search ON verbs(root COLLATE NOCASE);
```

## Sample Data

```bash
$ sqlite3 .data/db/verbs.db "SELECT root, etymology FROM verbs LIMIT 3;"

čmt|{"etymons": [{"source": "Turk.", "source_root": "çimento", ...}]}
nkt|{"etymons": [{"source": "MEA", "source_root": "nkt", ...}]}
fḏ̣l|{"etymons": [{"source": "Arab.", "source_root": "fḏ̣l", ...}]}
```

## File Locations

### Source Files (Private)
```
.devkit/new-source-docx/
├── 1. ʔ, ʕ, b, č.docx
├── 2. d, f, g, ġ, ǧ.docx
├── 3. h,ḥ,k.docx
├── 4. l, m, n.docx
├── 5. p, q, r.docx
├── 6. s, ṣ, š, t, ṭ, v.docx
└── 7. w, x, y, z, ʕ̇.docx
```

### Intermediate Files (Ignored by Vite)
```
.devkit/analysis/docx_v2_verbs/
├── ʔbl.json
├── ʔbr.json
├── ...
└── zḥm.json
(1,498 files total)
```

### Production Database (Ignored by Vite)
```
.data/db/
└── verbs.db (2.7 MB)
```

### Scripts
```
parser/
└── parse_docx_production.py

scripts/
└── migrate_json_to_sqlite.py
```

## Adapter Pattern

The application uses an adapter pattern to abstract database access:

```typescript
// server/db/verbs/index.ts
export const verbDatabase = VerbDatabaseFactory.create()

// Automatically uses SqliteVerbDatabase based on env
// Future: Can switch to PostgresVerbDatabase for production
```

## Important Notes

### 1. DOCX Files are Source of Truth
- **Never edit JSON or SQLite directly**
- Always edit DOCX source, then re-run pipeline
- JSON and SQLite are generated artifacts

### 2. File Watching Optimization
- `.devkit/analysis/` excluded from Vite watching
- `.data/` excluded from Vite watching
- Prevents spawn EBADF errors
- See: `.devkit/docs/FILE_WATCHING_PERMANENT_FIX.md`

### 3. Git Ignore
- DOCX source files: Not committed (proprietary)
- JSON files: Not committed (generated)
- SQLite database: **IS committed** (production data)

### 4. Deployment
- Vercel reads from Git repository
- SQLite database deployed with code
- No build step needed for database
- Database is read-only in production

## Troubleshooting

### Database not found
```bash
# Check if database exists
ls -la .data/db/verbs.db

# If missing, run migration
python3 scripts/migrate_json_to_sqlite.py
```

### Wrong verb count
```bash
# Expected: 1,498 verbs
sqlite3 .data/db/verbs.db "SELECT COUNT(*) FROM verbs;"

# If wrong, re-run full pipeline
python3 parser/parse_docx_production.py
python3 scripts/migrate_json_to_sqlite.py
```

### Parser errors
```bash
# Check DOCX files exist
ls .devkit/new-source-docx/*.docx

# Run with verbose output
python3 parser/parse_docx_production.py 2>&1 | tee parser_log.txt
```

## Documentation

- **Parser development:** `.devkit/analysis/FINAL_PRODUCTION_SUMMARY.md`
- **Etymology extraction:** `.devkit/analysis/ETYMOLOGY_100_PERCENT.md`
- **Parsing validation:** `.devkit/docs/PARSING_VALIDATION.md` (99.21% coverage ✅)
- **Database architecture:** `.devkit/docs/DATABASE_ARCHITECTURE.md`
- **Database quick start:** `.devkit/docs/DATABASE_QUICK_START.md`
- **Spawn EBADF fix:** `.devkit/docs/SPAWN_EBADF_FINAL_RESOLUTION.md`
- **File watching fix:** `.devkit/docs/FILE_WATCHING_PERMANENT_FIX.md`

---

**Status:** ✅ All systems operational
**Parsing validation:** ✅ 99.21% word coverage (PASS)
**Last updated:** 2025-11-01
