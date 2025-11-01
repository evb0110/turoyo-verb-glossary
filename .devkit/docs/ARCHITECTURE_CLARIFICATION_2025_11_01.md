# Architecture Clarification: SQLite Database vs JSON Files

**Date:** 2025-11-01
**Issue:** Misleading `server/assets/verbs/` directory suggested JSON files were served as Nitro assets

## Problem

The project structure was confusing:

1. **JSON files in `server/assets/verbs/`** - Suggested they were Nitro assets being served
2. **Documentation referenced `server/assets/`** - Implied JSON files were the production data source
3. **Actual behavior:** Application reads from SQLite database (`.data/db/verbs.db`), NOT JSON files

This caused the Detransitive bug fix to appear ineffective because:
- ✅ Parser was fixed correctly
- ✅ JSON files were regenerated with Detransitive stems
- ❌ **SQLite database was NOT updated** (migration step forgotten)
- Result: Frontend still showed old data from database

## Root Cause

**Architectural confusion:** The data pipeline was:

```
DOCX → Parser → JSON (.devkit/analysis/) → Migration → SQLite (.data/db/) → API → Frontend
                            ↓
                  WRONG: Also copied to server/assets/verbs/
                         (misleading location, never used)
```

## Solution

### 1. Removed Misleading Directory

```bash
rm -rf server/assets/verbs/
```

All 1,498 JSON files removed from `server/assets/verbs/` (they were git-tracked but unused).

### 2. Updated .gitignore

```gitignore
# Verb JSON files (intermediate - use SQLite database instead)
server/assets/verbs/
```

Prevents accidental recreation and commit.

### 3. Updated Documentation

**CLAUDE.md - Data Pipeline section:**

```markdown
### Current Production Pipeline (DOCX → SQLite)

- **Source:** `.devkit/new-source-docx/*.docx` (7 DOCX files)
- **Parser:** `parser/parse_docx_production.py` (Generates JSON files)
- **Intermediate:** `.devkit/analysis/docx_v2_verbs/*.json` (1,502 files)
- **Migration:** `scripts/migrate_json_to_sqlite.py` (JSON → SQLite)
- **Storage:** `.data/db/verbs.db` (SQLite database - 2.7 MB)
- **API routes:** Query SQLite via `server/db/verbs/` adapters
- **Repository pattern:** `server/repositories/verbs/`
```

**CLAUDE.md - New Rules:**

```markdown
- 🚨 RULE: After parser changes, MUST run migration: `python3 scripts/migrate_json_to_sqlite.py`
- 🚨 RULE: JSON files in `.devkit/analysis/docx_v2_verbs/` are intermediate only
```

### 4. Correct Deployment Workflow

```bash
# 1. Run parser
python3 parser/parse_docx_production.py
# → Generates: .devkit/analysis/docx_v2_verbs/*.json

# 2. Validate
python3 .devkit/scripts/comprehensive_validation.py .devkit/analysis/docx_v2_verbs

# 3. CRITICAL: Migrate to SQLite
python3 scripts/migrate_json_to_sqlite.py
# → Updates: .data/db/verbs.db

# Frontend now reads from updated database ✅
```

## Actual Data Flow (Corrected)

```
┌─────────────────────────────────────────┐
│ DOCX Source Files                       │
│ .devkit/new-source-docx/*.docx          │
└──────────────┬──────────────────────────┘
               │
               │ parse_docx_production.py
               ↓
┌─────────────────────────────────────────┐
│ Intermediate JSON Files                 │
│ .devkit/analysis/docx_v2_verbs/*.json   │
│ (1,498 files - for validation only)     │
└──────────────┬──────────────────────────┘
               │
               │ migrate_json_to_sqlite.py
               ↓
┌─────────────────────────────────────────┐
│ Production SQLite Database              │
│ .data/db/verbs.db (2.7 MB)             │
│ ✓ Single source of truth                │
│ ✓ Fast queries, indexed                 │
└──────────────┬──────────────────────────┘
               │
               │ getVerbDatabase() → SqliteVerbDatabase
               │ server/repositories/verbs/*
               ↓
┌─────────────────────────────────────────┐
│ API Endpoints                           │
│ GET /api/verb/:root                     │
│ GET /api/verbs (search)                 │
│ GET /api/stats                          │
└──────────────┬──────────────────────────┘
               │
               │ useFetch composable
               ↓
┌─────────────────────────────────────────┐
│ Frontend Components                     │
│ VerbStemCard, VerbExample, etc.         │
└─────────────────────────────────────────┘
```

**Key Point:** `server/assets/verbs/` is NOT in this flow!

## Impact

### Before Clarification
- ❌ Confusing structure suggested JSON files were served
- ❌ Documentation referenced wrong data source
- ❌ Easy to forget migration step after parser changes
- ❌ 1,498 unnecessary JSON files tracked in git

### After Clarification
- ✅ Clear data pipeline: DOCX → JSON (intermediate) → SQLite (production)
- ✅ Documentation accurately reflects architecture
- ✅ Migration step documented as MANDATORY
- ✅ Removed 1,498 unused files from git tracking
- ✅ Added .gitignore to prevent recreation

## Files Changed

1. **Removed:** `server/assets/verbs/` directory (all 1,498 JSON files)
2. **Updated:** `.gitignore` - Added `server/assets/verbs/`
3. **Updated:** `.claude/CLAUDE.md` - Corrected data pipeline documentation
4. **Updated:** `.devkit/docs/DEPLOYMENT_SUMMARY_2025_11_01.md` - Added migration step

## Lessons Learned

1. **Directory naming matters:** `server/assets/` strongly implies Nitro static assets
2. **Documentation must match reality:** Outdated docs cause confusion and bugs
3. **Migration steps are critical:** Parser fixes require database updates to take effect
4. **Intermediate files should live in `.devkit/`:** Not in production directories

## Verification

```bash
# Check database has Detransitive stems
sqlite3 .data/db/verbs.db "
  SELECT COUNT(*) FROM verbs
  WHERE stems LIKE '%\"stem\":\"Detransitive\"%'
"
# Output: 502 ✅

# Verify server/assets/verbs/ removed
ls server/assets/verbs/ 2>/dev/null
# Output: No such file or directory ✅

# Check .gitignore
grep "server/assets/verbs" .gitignore
# Output: server/assets/verbs/ ✅
```

---

**Status:** ✅ **FIXED**
**Complexity:** Medium (architectural confusion, not code bug)
**Impact:** High (affected deployment workflow understanding)
**Resolution:** Directory cleanup + documentation updates

This clarification prevents future confusion and ensures the correct deployment workflow is always followed.
