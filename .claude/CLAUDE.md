# Turoyo Verb Glossary

A Nuxt 4 web application for browsing 1,197 Turoyo verbs with etymology, conjugations, and examples. Data extracted from HTML source into structured JSON.

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
- ❌ `npm run dev` / dev server - Dev server likely already running (port 3456)
  - Check if server is running before suggesting to start it
  - Starting duplicate servers causes port conflicts
  - If you need to test SSR, use `curl http://localhost:3456` on existing server

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
1. `npm run prebuild` - Generates search index
2. `npm run build` - Nuxt build
3. `npm run validate` - Data validation
