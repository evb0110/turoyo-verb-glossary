# Project Documentation Index

## Getting Started

Start here if you're new to the project:

1. **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)** (Primary)
   - Complete project structure and configuration
   - All key files explained
   - Database schema details
   - Deployment information

2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** (Daily Use)
   - Naming conventions (critical!)
   - Code patterns
   - Common commands
   - Import rules
   - File organization

## Documentation Location

Location: `/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/docs/`

Files are organized in this directory for easy access and version control.

## Key Information At a Glance

### Project Type

- **Framework:** Nuxt 4 (Vue 3 + TypeScript)
- **Database:** PostgreSQL (production), SQLite (verbs data)
- **Authentication:** Better Auth + Google OAuth
- **Deployment:** Vercel or Cloudflare Pages

### Critical Rules (MUST FOLLOW)

1. **Type Naming:** Interfaces use `I` prefix, Type aliases use `T` prefix
   - Good: `IUser`, `TUserRole`
   - Bad: `User`, `UserRole`
2. **Imports:** Use absolute imports with `~/` or `~~/`
   - Good: `import { useAuth } from '~/composables/useAuth'`
   - Bad: `import { useAuth } from '../composables/useAuth'`
3. **Code Style:** 4 spaces, single quotes, no semicolons

### Quick Commands

```bash
pnpm dev        # Start dev server (https://turoyo-verb-glossary.lvh.me:3456)
pnpm lint       # Lint & auto-fix
pnpm typecheck  # Type checking
pnpm build      # Production build
```

### Project Statistics

- 1,696 Turoyo verbs
- 3,553 stems
- 4,685 conjugation examples
- 10+ etymology source languages

## Architecture Overview

```
Frontend (app/)          Backend (server/)       Database
├── components/          ├── api/                 PostgreSQL
├── composables/         ├── services/            (Neon)
├── pages/               ├── repositories/
├── types/               └── db/schema.ts
└── utils/
        ↓
    Shared (shared/)
    ├── types/
    └── config/
```

## Directory Structure Quick Reference

| Directory  | Purpose                            |
| ---------- | ---------------------------------- |
| `app/`     | Frontend application (Nuxt srcDir) |
| `server/`  | Backend API & services (Nitro)     |
| `shared/`  | Shared types & utilities           |
| `data/`    | Verb data files (JSON)             |
| `parser/`  | Python DOCX parser                 |
| `scripts/` | Utility scripts                    |
| `drizzle/` | Database migrations                |
| `public/`  | Static assets                      |
| `.devkit/` | Development tools & analysis       |

## Configuration Files

| File                | Purpose                        |
| ------------------- | ------------------------------ |
| `package.json`      | Dependencies & npm scripts     |
| `nuxt.config.ts`    | Nuxt framework configuration   |
| `tsconfig.json`     | TypeScript references          |
| `eslint.config.mjs` | Linting rules (strict!)        |
| `drizzle.config.ts` | Database migration config      |
| `.env.example`      | Environment variables template |

## Type System

**Frontend Types:** `app/types/I*.ts`

- IVerbIndex, IFilterableVerb, IExample, etc.

**Server Types:** `server/types/I*.ts`

- Backend-specific types

**Shared Types:** `shared/types/I*.ts` or `shared/types/T*.ts`

- IVerb, IStem, IEtymology, IAuthUser, TUserRole, etc.

## API Endpoints Reference

### Verbs

- `GET /api/verb/[root]` - Get verb by root

### Search

- `POST /api/search/fulltext` - Full-text search
- `POST /api/search/roots` - Root search

### User & Auth

- `GET /api/user/me` - Current user
- `POST /api/auth/[...all]` - Better Auth routes

### Admin (protected)

- `GET /api/admin/users` - List users
- `PATCH /api/admin/users/[id]/activate`
- `PATCH /api/admin/users/[id]/block`
- `GET /api/admin/sessions` - Active sessions
- `GET /api/admin/activity` - Activity log

### Statistics

- `GET /api/stats` - Verb statistics

## Development Workflow

1. Start dev server: `pnpm dev`
2. Make changes following code patterns
3. Check linting: `pnpm lint`
4. Check types: `pnpm typecheck`
5. Test locally
6. Commit changes
7. Deploy: Push to repository

## Environment Setup

See `.env.example` for required variables:

- Google OAuth credentials
- Database URL (PostgreSQL)
- Better Auth secret
- Verb database path

## Common Tasks

### Adding a New Component

1. Create file in `app/components/`
2. Use TypeScript with `<script setup lang="ts">`
3. Define props with `interface IComponentProps`
4. Component is auto-imported

### Adding a New API Endpoint

1. Create file: `server/api/[feature]/[name].[method].ts`
2. Export default handler function
3. Use server utilities & services
4. Return typed responses

### Adding a New Composable

1. Create file: `app/composables/use*.ts`
2. Export named function `export function useFeatureName()`
3. Use in components with `const { state, action } = useFeatureName()`

### Adding a New Type

1. Frontend: `app/types/I*.ts`
2. Server: `server/types/I*.ts`
3. Shared: `shared/types/I*.ts` or `shared/types/T*.ts`
4. Follow naming: Interface = `I` prefix, Type alias = `T` prefix

## Code Style Checklist

- [ ] 4 space indentation
- [ ] Single quotes for strings
- [ ] No semicolons at end of statements
- [ ] Interfaces prefixed with `I`
- [ ] Type aliases prefixed with `T`
- [ ] Absolute imports (~/...
- [ ] Max line length 120 chars
- [ ] HTML: double quotes, 4 space indent

## Database Information

### Production (PostgreSQL via Neon)

- User accounts & sessions
- Activity logging
- Better Auth tables

### Development (SQLite)

- Verb data: `.data/db/verbs.db`

### Schema File

- `server/db/schema.ts` - All table definitions

## Important Notes

1. **No relative imports** - ESLint will fail if you use `../`
2. **Type naming is enforced** - ESLint checks I/T prefixes
3. **No code comments** - Code should be self-documenting
4. **No type assertions** - Use type guards instead
5. **No `any` types** - Use `unknown` if truly uncertain

## Previous Documentation

This project has extensive previous documentation in `.devkit/docs/`:

- Database architecture details
- Data pipeline information
- Deployment strategies
- Various bug fixes and solutions
- Historical implementation notes

See other `.md` files in this directory for specific topics.

## Getting Help

1. Check QUICK_REFERENCE.md for common patterns
2. Look at PROJECT_OVERVIEW.md for detailed info
3. Review existing code for patterns
4. Check ESLint output for violations

## Version Info

- **Nuxt:** 4.1.2
- **Vue:** 3.5.22
- **TypeScript:** 5.9.3
- **Tailwind CSS:** 4.1.14
- **Node.js:** 20+ or 22+
- **pnpm:** 9+

---

Last updated: 2025-11-14
Project: Turoyo Verb Glossary
Location: /Users/evb/WebstormProjects/turoyo-verb-glossary
