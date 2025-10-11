# Turoyo Verb Glossary

A Nuxt 4 web application for browsing 1,197 Turoyo verbs with etymology, conjugations, and examples. Data extracted from HTML source into structured JSON.

## Package Manager

**This project uses pnpm:**
- ✓ Use `pnpm add`, `pnpm install`, `pnpm run`
- ✗ Never use `npm` or `yarn` commands

## Terminology

**Use "stem" not "binyan":**
- ✓ Correct: "Stem I", "Stem II", "Stem Pa.", "Stem Af."
- ✗ Wrong: "binyan I", "binyan II", `binyan` field
- Applies to: code, types, comments, docs, UI

## Data Management

**Fix at source, not output:**
- When you find data errors in verb JSON files, **don't edit the JSON directly**
- Instead: analyze the parser script and fix the extraction logic
- Then: reparse from `source/Turoyo_all_2024.html` to fix all instances
- Scripts: `parser/extract_final.py`, `parser/validate.py`

## Workflow Rules

**NEVER do these without explicit user request:**
- ❌ `git commit` - Only commit when user explicitly asks
- ❌ `git push` - Only push when user explicitly asks
- ❌ `pnpm run dev` / dev server - Dev server likely already running (port 3456)
  - Check if server is running before suggesting to start it
  - Starting duplicate servers causes port conflicts
  - Server is always running - after each code change, check with curl:
    - `curl http://localhost:3456` for homepage
    - `curl http://localhost:3456/verbs/[root]` for verb pages
  - Never rely on browser overlay errors - always verify with curl

## Testing Requirements

**MANDATORY: Test extensively before committing any major change**

Major changes include: API changes, search functionality, data loading, SSR/client differences

### Required Testing Process:

1. **Test Server-Side** (test with `curl` and compare with source data):
   ```bash
   # Test API endpoints
   curl "http://localhost:3456/api/verbs?q=form&type=all"

   # Compare with source HTML
   grep -i "form" source/Turoyo_all_2024.html | wc -l
   ```

2. **Test Client-Side** (test in browser console):
   - Open dev tools console
   - Search for test queries in all modes:
     - "Roots only" mode with various roots
     - "Everything" mode with translation matches
     - With/without regex enabled
     - With/without case sensitivity
   - Verify console logs show expected behavior
   - Check network tab for API calls

3. **Test SSR vs Client Rendering**:
   ```bash
   # Test SSR output
   curl "http://localhost:3456/?q=form&type=all" | grep "matches"

   # Then verify client-side hydration works in browser
   ```

4. **Compare Results with Source Data**:
   ```bash
   # Always verify against source HTML
   grep -io "search-term" source/Turoyo_all_2024.html | wc -l

   # Check specific verb files
   jq '.stems[].conjugations[][] | .translations[]' public/appdata/api/verbs/root.json | grep -i "term"
   ```

5. **Test Edge Cases**:
   - Empty results
   - Unicode characters in queries
   - Very long result sets
   - Network errors / timeout scenarios

**If tests fail or show unexpected results, FIX BEFORE COMMITTING**

## Development

**Tech stack:**
- Nuxt 4 (Vue 3, TypeScript, Tailwind 4)
- Dev server: `http://localhost:3456` (custom port, check if already running)
- SSR with Vercel preset for deployment

**Data loading:**
- Server: Use `/api/verbs`, `/api/stats` (Nitro routes)
- Client: Direct fetch from `/appdata/api/*.json` (static CDN)
- Use `useAsyncData()` for SSR hydration
- See: `app/composables/useVerbs.ts`

**Build process:**
1. `pnpm run prebuild` - Generates search index
2. `pnpm run build` - Nuxt build
3. `pnpm run validate` - Data validation
