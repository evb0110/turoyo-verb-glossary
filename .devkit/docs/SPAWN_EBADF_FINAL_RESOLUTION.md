# spawn EBADF - Final Resolution

## Summary

**Problem:** Dev server crashed with `spawn EBADF` error after deploying 1,498 verb JSON files.

**Root Cause:** Build artifacts (.output, dist, .vercel) containing 8,692 files were being scanned by Vite, causing macOS kqueue exhaustion.

**Solution:** Deleted build artifacts - reduced total project files from 10,459 to 1,767.

## Timeline of Fixes

### Previous Session: SQLite Migration
- Moved 1,498 JSON files from `server/assets/verbs/` to `.devkit/analysis/docx_v2_verbs/`
- Created SQLite database at `.data/db/verbs.db` (2.7 MB, 1,498 verbs)
- Implemented adapter pattern for database switching
- **Result:** Reduced watched source files from ~10,000 to ~147

### This Session: Build Artifacts Cleanup

**Discovery:** Even with JSON files moved, spawn EBADF persisted because build artifacts were still being watched.

**File Count Analysis:**
```
Before cleanup:
- Source files (watched): 147 ✅
- Build artifacts: 8,692 ❌
  - .output: 3,878 files
  - dist: 3,126 files
  - .vercel: 1,688 files
- Total project files: 10,459 ❌

After cleanup:
- Source files (watched): 147 ✅
- Build artifacts: 0 ✅
- Total project files: 1,767 ✅
```

**Actions Taken:**

1. Deleted build artifacts:
   ```bash
   rm -rf .output dist .vercel
   ```

2. Built better-sqlite3 native bindings:
   ```bash
   cd node_modules/.pnpm/better-sqlite3@12.4.1/node_modules/better-sqlite3
   npm run build-release
   ```

3. Started dev server successfully:
   ```bash
   pnpm dev
   ```

## Results

✅ **NO spawn EBADF error!**
- Vite client built in 21ms
- Vite server built in 21ms
- Nuxt Nitro server built in 646ms

✅ **Frontend accessible:**
- HTTP 200 at https://turoyo-verb-glossary.lvh.me:3456/
- HTML rendering correctly
- Auth middleware handling guest users properly

✅ **Database ready:**
- better-sqlite3 native bindings compiled
- SQLite database contains 1,498 verbs
- Ready for API usage (requires auth)

## Key Lessons

1. **Source files vs total files:** Only 147 source files were watched, but 10,459 total files existed in project
2. **Build artifacts matter:** Vite scans entire project directory, including .output, dist, .vercel
3. **macOS kqueue limits:** ~8,000-12,000 file watches before EBADF errors
4. **Clean builds:** Always delete build artifacts when troubleshooting file watching issues

## Prevention

Add to .gitignore if not already present:
```
.output/
dist/
.vercel/
.backup/
```

Run periodic cleanup:
```bash
make clean  # or: rm -rf .output dist .vercel .nuxt node_modules/.vite
```

## Configuration Cleanup

After confirming the fix worked, reverted temporary config changes in `nuxt.config.ts`:

**Removed:**
- `optimizeDeps: { noDiscovery: true, include: [] }` (was temporary workaround)
- `typescript: { typeCheck: false }` (was temporary workaround)

**Result:** Server still runs perfectly with clean configuration.

## Status: RESOLVED ✅

The dev server is now running successfully without spawn EBADF errors. Frontend is accessible, database is ready, and the system is fully operational with clean configuration.

**Final verification:**
- Dev server: ✅ Running on https://turoyo-verb-glossary.lvh.me:3456/
- Frontend: ✅ HTTP 200, HTML rendering
- Build times: Vite client 26ms, Vite server 20ms, Nitro 477ms
- No spawn EBADF errors
- No temporary workarounds in config

Date: 2025-11-01
