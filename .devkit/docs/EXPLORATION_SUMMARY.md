# Turoyo Verb Glossary - Project Exploration Summary

**Date:** 2025-11-14  
**Project Location:** /Users/evb/WebstormProjects/turoyo-verb-glossary

## Exploration Completed

Comprehensive exploration of the turoyo-verb-glossary project completed with documentation created in `.devkit/docs/`:

### Documentation Created

1. **README.md** - Documentation index and navigation guide
2. **PROJECT_OVERVIEW.md** - Complete 15-section project structure document (21KB)
3. **QUICK_REFERENCE.md** - Quick lookup guide for developers (5.6KB)
4. **EXPLORATION_SUMMARY.md** - This file

## Project At a Glance

### Technology Stack

- **Frontend:** Nuxt 4.1.2, Vue 3.5.22, TypeScript 5.9.3
- **Backend:** Nitro (built-in Nuxt server)
- **Database:** PostgreSQL (Neon serverless) + SQLite (verb data)
- **ORM:** Drizzle 0.44.6
- **Auth:** Better Auth 1.3.27 with Google OAuth
- **Styling:** Tailwind CSS 4.1.14
- **UI Components:** @nuxt/ui 4.0.0
- **Utilities:** VueUse 11.1.0
- **Linting:** ESLint 9.36.0, Prettier 3.6.2

### Project Purpose

Comprehensive web application for browsing and searching Turoyo verbs with etymology and conjugations.

### Data Size

- 1,696 Turoyo verbs
- 3,553 stems
- 4,685 conjugation examples
- 10+ etymology source languages

## Architecture Overview

### Frontend (app/)

- 28 Vue components (auto-imported)
- 4 composables (composition API)
- 17 type definitions
- File-based routing (6 pages)
- Middleware-based authentication
- HTTPS dev server on port 3456

### Backend (server/)

- 12 API endpoints across 6 route groups
- Authentication & authorization
- Search services (fulltext, roots)
- Admin panel (users, sessions, activity)
- Activity logging & tracking
- User statistics

### Database

**PostgreSQL (Production)**

- user, session, account, verification
- userSessionActivity, userActivityLog
- Managed by Drizzle ORM

**SQLite (Development)**

- Verb data storage (`.data/db/verbs.db`)
- JSON source files (`data/verbs_final.json`)

### Shared Code (shared/)

- 14 shared type definitions
- Activity event type enumeration
- Slug-to-root utility function

## Key Findings

### Strict Code Standards (Enforced by ESLint)

#### Type Naming

- **Interfaces:** MUST start with `I` (e.g., `IUser`, `IVerbIndex`)
- **Type Aliases:** MUST start with `T` (e.g., `TUserRole`)
- Non-compliant names fail ESLint

#### Import Rules

- **Required:** Absolute imports with `~/` or `~~/`
- **Forbidden:** Relative imports like `../` or `./`
- ESLint rule: `no-restricted-imports` prevents relative paths

#### Code Style (Stylistic Rules)

- **Indentation:** 4 spaces (enforced)
- **Quotes:** Single quotes only
- **Semicolons:** None
- **Comma Dangle:** Never on functions, always-multiline on arrays/objects
- **Max Line Length:** 120 characters
- **HTML Indent:** 4 spaces
- **HTML Quotes:** Double quotes

### Configuration Files

#### nuxt.config.ts

- Source directory: `app/`
- Public directory: `public/`
- Dev server: https://turoyo-verb-glossary.lvh.me:3456
- Modules: @nuxt/eslint, @nuxt/ui
- HTTPS auto-generated via mkcert plugin
- Deployment presets: Vercel or Cloudflare Pages

#### eslint.config.mjs

- 6 Vue formatting rules
- Import ordering rules
- 14 custom Vue rules
- 2 custom ESLint rules (in eslint-rules/)
- Type naming conventions
- Import pattern restrictions

#### tsconfig.json

- Nuxt-managed TypeScript
- 4 generated tsconfig references (.nuxt/)
- Full type support for app, server, shared, and node

### Database Schema (Drizzle ORM)

**Authentication Tables**

- user (id, name, email, role, timestamps)
- session (id, token, userId, expiresAt)
- account (OAuth provider accounts)
- verification (email/2FA verification)

**Tracking Tables**

- userSessionActivity (session tracking, request counting)
- userActivityLog (event logging, filtered results, metadata)

**Enums**

- userRoleEnum: admin | user | pending | blocked
- activityEventTypeEnum: activity event types

### API Structure

**File-based routing pattern:** `server/api/[feature]/[endpoint].[method].ts`

**Endpoints:**

- Auth: /api/auth/[...all] (Better Auth proxy)
- Verbs: /api/verb/[root]
- Search: /api/search/{fulltext, roots}
- User: /api/user/me
- Admin: /api/admin/{users, sessions, activity, pending-count}
- Stats: /api/stats

### Services Architecture

**Location:** `server/services/`

**Core Services:**

- searchFullText.ts - Full-text search
- searchRoots.ts - Root-based search
- calculateStats.ts - Statistics
- generateVerbMetadata.ts - Metadata creation
- extractMetadata.ts, extractVerbPreview.ts
- checkAdminRole.ts, requireAdmin.ts
- activity/ folder for session tracking

## Development Setup

### Environment Variables Required

```
NUXT_GOOGLE_CLIENT_ID
NUXT_GOOGLE_CLIENT_SECRET
NUXT_DATABASE_URL (PostgreSQL)
NUXT_BETTER_AUTH_SECRET
VERB_DATABASE (sqlite)
VERB_DATABASE_PATH
```

### Development Workflow

```bash
pnpm dev            # Start dev server
pnpm lint           # Lint & auto-fix
pnpm typecheck      # Type checking
pnpm build          # Production build
pnpm build:c        # Cloudflare build
```

### Pre-commit Hooks

- Husky + lint-staged configured
- ESLint runs on \*.{js,ts,vue}
- Prettier runs on \*.{json,md}

## Unique Project Features

### Type Safety

- Full TypeScript throughout
- Enforced type naming conventions (I/T prefixes)
- No `any` types allowed (must use `unknown`)
- No type assertions (use type guards)

### Code Organization

- Auto-imported components
- Composable-based composition API
- Service layer for business logic
- Repository pattern for data access
- Strict import ordering

### Data Pipeline

- Python DOCX parser (parse_docx_production.py)
- JSON intermediate format (verbs_final.json)
- SQLite local database
- PostgreSQL production database
- Drizzle migrations for schema versioning

### Deployment

- Vercel support (default)
- Cloudflare Pages support
- Custom Nitro server support
- 1-year immutable cache for static assets

## File Statistics

- **Total Directories:** 42 major directories
- **Configuration Files:** 6 main config files
- **Type Definitions:** 31+ total (frontend, server, shared)
- **API Endpoints:** 12 endpoints
- **Components:** 28 Vue SFCs
- **Services:** 8+ server services
- **Database Tables:** 6 tables + enums
- **Python Scripts:** 8 scripts for parsing/migration

## Important Rules Summary

1. **Types:** Interface = `I` prefix, Type alias = `T` prefix
2. **Imports:** Absolute (`~/`) only, never relative (`../`)
3. **Style:** 4 spaces, single quotes, no semicolons
4. **Code:** No comments, self-documenting code required
5. **Types:** No assertions, no `any`, use type guards
6. **Quality:** Lint & typecheck before committing

## Previous Documentation

The `.devkit/docs/` folder contains extensive historical documentation:

- Architecture clarifications
- Database design documents
- Data pipeline summaries
- Deployment strategies
- Bug fix documentation
- Implementation notes
- Session summaries

## Exploration Thoroughness

### Covered

- Complete directory structure
- All configuration files (6 main configs)
- Package.json and dependencies (15+ key packages)
- TypeScript setup and conventions
- ESLint and code style rules (26 custom rules + patterns)
- Nuxt configuration (modules, plugins, dev server, caching)
- Database schema (6 tables, 2 enums)
- Environment variables
- API endpoints and structure (12 endpoints)
- Server services (8+ services)
- Type system organization
- Build and deployment targets
- Development tools and Makefile

### Access Points

- Project root: `/Users/evb/WebstormProjects/turoyo-verb-glossary`
- Documentation: `.devkit/docs/`
- Frontend: `app/`
- Backend: `server/`
- Config: `nuxt.config.ts`, `eslint.config.mjs`, `tsconfig.json`

## Documentation Files Created

1. **README.md** (4.2 KB)
   - Navigation guide
   - Getting started instructions
   - Key configuration reference
   - Common tasks

2. **PROJECT_OVERVIEW.md** (21 KB)
   - 15 comprehensive sections
   - Complete structure breakdown
   - All configuration details
   - Database schema documentation
   - API endpoint reference

3. **QUICK_REFERENCE.md** (5.6 KB)
   - Quick lookup guide
   - Code patterns
   - Common commands
   - Naming conventions
   - File organization

4. **EXPLORATION_SUMMARY.md** (This file)
   - High-level overview
   - Key findings
   - Statistics
   - Rules summary

## Next Steps for Development

1. Review QUICK_REFERENCE.md for code patterns
2. Read PROJECT_OVERVIEW.md for detailed information
3. Follow naming conventions strictly (I/T prefixes)
4. Use absolute imports only
5. Run lint/typecheck before commits
6. Review existing code for patterns

## Key File Locations

| File                 | Purpose         | Location               |
| -------------------- | --------------- | ---------------------- |
| TypeScript Config    | References      | `/tsconfig.json`       |
| ESLint Config        | Linting rules   | `/eslint.config.mjs`   |
| Nuxt Config          | Framework setup | `/nuxt.config.ts`      |
| App Config           | UI config       | `/app.config.ts`       |
| Drizzle Config       | Database        | `/drizzle.config.ts`   |
| DB Schema            | All tables      | `/server/db/schema.ts` |
| Package.json         | Dependencies    | `/package.json`        |
| Environment Template | Variables       | `/.env.example`        |

## Summary

This is a **production-ready, enterprise-grade** Nuxt 4 application with:

- Strict type safety and code standards
- Comprehensive authentication and authorization
- Full-featured API with search and analytics
- Database-backed user management
- SSR with modern Vue 3 composition API
- Clean architecture with separated concerns
- Automated linting and type checking

All exploration has been documented in `.devkit/docs/` for easy reference and navigation.

---

**Project Base:** `/Users/evb/WebstormProjects/turoyo-verb-glossary`
**Documentation:** `.devkit/docs/README.md` (start here)
**Quick Reference:** `.devkit/docs/QUICK_REFERENCE.md` (daily use)
**Full Details:** `.devkit/docs/PROJECT_OVERVIEW.md` (comprehensive)
