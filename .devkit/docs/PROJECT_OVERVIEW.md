# Turoyo Verb Glossary - Project Structure Overview

## Project Summary

A comprehensive web application for browsing and searching Turoyo verbs with etymology and conjugations. Built with Nuxt 4, Vue 3, TypeScript, and features 1,696 verbs with 3,553 stems and 4,685 conjugation examples.

**Directory:** `/Users/evb/WebstormProjects/turoyo-verb-glossary`

---

## 1. Project Structure

```
turoyo-verb-glossary/
├── app/                          # Nuxt frontend application (srcDir)
│   ├── app.vue                   # Root component
│   ├── assets/                   # Static assets (CSS, images)
│   ├── components/               # Vue components
│   │   ├── Navbar.vue
│   │   ├── VerbHeader.vue
│   │   ├── VerbFilters.vue
│   │   ├── GlobalSearchModal.vue
│   │   ├── Edit/StemEditor.vue
│   │   ├── Edit/EtymologyEditor.vue
│   │   └── [...other components]
│   ├── composables/              # Vue 3 composition API utilities
│   │   ├── useAuth.ts
│   │   ├── useQuery.ts
│   │   ├── useClientPathHeader.ts
│   │   └── useContainerWide.ts
│   ├── config/                   # App configuration
│   │   ├── REDIRECT_RULES.ts
│   │   ├── isAdminRoute.ts
│   │   └── matchesRoutePattern.ts
│   ├── layouts/                  # Nuxt layouts
│   ├── middleware/               # Nuxt middleware
│   │   └── auth.global.ts
│   ├── pages/                    # File-based routing
│   │   ├── index.vue             # Home page
│   │   ├── login.vue             # Authentication
│   │   ├── blocked.vue
│   │   ├── admin/index.vue
│   │   ├── admin/sessions.vue
│   │   ├── admin/activity.vue
│   │   └── verbs/[root].vue      # Dynamic verb pages
│   ├── plugins/                  # Nuxt plugins
│   │   └── auth-redirect.client.ts
│   ├── types/                    # TypeScript type definitions (I-prefixed)
│   │   ├── IVerbIndex.ts
│   │   ├── IFilterableVerb.ts
│   │   ├── IExample.ts
│   │   ├── IGlossToken.ts
│   │   ├── IConjugationGroup.ts
│   │   ├── IEtymon.ts
│   │   ├── IStructuredExample.ts
│   │   ├── INavigationState.ts
│   │   └── [17 total type files]
│   └── utils/                    # Frontend utilities
├── server/                       # Nitro server (backend)
│   ├── api/                      # API endpoints
│   │   ├── auth/[...all].ts      # Better Auth routes
│   │   ├── verb/[root].get.ts
│   │   ├── search/fulltext.post.ts
│   │   ├── search/roots.post.ts
│   │   ├── stats/index.get.ts
│   │   ├── user/me.get.ts
│   │   └── admin/
│   │       ├── users/index.get.ts
│   │       ├── users/[id]/activate.patch.ts
│   │       ├── users/[id]/block.patch.ts
│   │       ├── sessions/index.get.ts
│   │       ├── activity/index.get.ts
│   │       └── pending-count.get.ts
│   ├── db/                       # Database
│   │   ├── schema.ts             # Drizzle ORM schema (PostgreSQL)
│   │   └── verbs/               # Verb data storage (SQLite)
│   ├── services/                 # Business logic
│   │   ├── searchFullText.ts
│   │   ├── searchRoots.ts
│   │   ├── calculateStats.ts
│   │   ├── generateVerbMetadata.ts
│   │   ├── checkAdminRole.ts
│   │   ├── requireAdmin.ts
│   │   ├── extractMetadata.ts
│   │   ├── extractVerbPreview.ts
│   │   └── activity/
│   │       └── [activity logging services]
│   ├── repositories/            # Database access layer
│   ├── types/                   # Server-side type definitions
│   ├── utils/                   # Server utilities
│   ├── lib/                     # Library code
│   └── plugins/                 # Nuxt plugins
├── shared/                       # Code shared between client & server
│   ├── config/
│   │   └── activityEventTypes.ts
│   ├── types/                   # Shared type definitions
│   │   ├── IVerb.ts             # Main verb type
│   │   ├── IStem.ts             # Stem type
│   │   ├── IEtymology.ts        # Etymology type
│   │   ├── IAuthUser.ts         # Auth user type
│   │   ├── TUserRole.ts         # User role type (T-prefixed)
│   │   ├── IUserActivityLog.ts
│   │   └── [more shared types]
│   └── utils/
│       └── slugToRoot.ts
├── data/                         # Verb data files
│   ├── verbs_final.json         # Complete verb database
│   ├── verbs_final_sample.json
│   └── baseline/                # Validation baselines
├── parser/                       # Python data parser
│   ├── parse_docx_production.py # Main DOCX parser
│   ├── parse_verbs.py
│   ├── regression_validator.py
│   ├── snapshot_baseline.py
│   ├── validate.py
│   └── requirements.txt
├── scripts/                      # Utility scripts
│   ├── migrate_json_to_sqlite.py
│   ├── migrate_sqlite_to_postgres.py
│   └── validate_parsing_completeness.py
├── drizzle/                      # Database migrations
│   ├── 0000_vengeful_night_thrasher.sql
│   ├── 0001_known_thunderbolt.sql
│   ├── 0002_thin_songbird.sql
│   ├── 0003_left_stephen_strange.sql
│   └── meta/
├── public/                       # Static files (favicons, robots.txt)
├── docs/                         # Documentation
│   └── validation/
├── .devkit/                      # Development kit & analysis
│   ├── analysis/
│   ├── debug/
│   ├── test/
│   ├── docs/
│   ├── scripts/
│   └── tmp/
├── .nuxt/                        # Nuxt build output (generated)
├── dist/                         # Production build output
├── .output/                      # Nitro output
└── node_modules/                 # Dependencies
```

---

## 2. Package.json - Dependencies & Scripts

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/package.json`

### Key Dependencies

**Frontend/Framework:**

- `nuxt@^4.1.2` - Vue 3 meta-framework with SSR
- `vue@^3.5.22` - Progressive JavaScript framework
- `vue-router@^4.5.1` - Client-side routing
- `@nuxt/ui@4.0.0` - Nuxt UI component library
- `@nuxt/eslint@1.9.0` - ESLint integration for Nuxt

**Utilities & Composition:**

- `@vueuse/core@11.1.0` - Composition API utilities
- `@vueuse/router@^13.9.0` - Router-aware composables

**Backend/Database:**

- `drizzle-orm@^0.44.6` - Type-safe ORM for SQL databases
- `drizzle-kit@^0.31.5` - Drizzle migration toolkit
- `@neondatabase/serverless@^1.0.2` - Neon serverless database client
- `better-auth@^1.3.27` - Modern authentication library

**Development:**

- `typescript@^5.9.3` - TypeScript compiler
- `eslint@^9.36.0` - Code linting
- `prettier@^3.6.2` - Code formatter
- `tailwindcss@^4.1.14` - Utility CSS framework
- `sass-embedded@^1.93.3` - SCSS compilation
- `husky@^9.0.11` - Git hooks management
- `lint-staged@^15.2.10` - Pre-commit linting
- `vite-plugin-mkcert@^1.17.9` - HTTPS support for dev

### NPM Scripts

```json
{
  "build": "nuxt build", // Production build
  "build:c": "CLOUDFLARE=1 pnpm run build", // Cloudflare build
  "dev": "nuxt dev", // Development server
  "generate": "nuxt generate", // Static generation
  "preview": "nuxt preview", // Preview build
  "lint": "eslint . --fix", // Lint & fix code
  "typecheck": "nuxi typecheck", // TypeScript type checking
  "validate": "node scripts/validate.js", // Custom validation
  "build:all": "npm run build && npm run validate",
  "postinstall": "nuxt prepare && husky install",
  "prepare": "husky"
}
```

### Lint-Staged Configuration

Pre-commit hooks that run:

- ESLint --fix on `*.{js,ts,vue}` files
- Prettier --write on `*.{json,md}` files

---

## 3. TypeScript Configuration

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/tsconfig.json`

Uses Nuxt's reference-based TypeScript setup with multiple tsconfig files:

```json
{
  "files": [],
  "references": [
    { "path": "./.nuxt/tsconfig.app.json" },
    { "path": "./.nuxt/tsconfig.server.json" },
    { "path": "./.nuxt/tsconfig.shared.json" },
    { "path": "./.nuxt/tsconfig.node.json" }
  ]
}
```

**Generated files** (in .nuxt/) handle actual compilation. TypeScript configuration is managed by Nuxt.

---

## 4. ESLint & Prettier Configuration

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/eslint.config.mjs`

### Code Style (via Stylistic)

- **Indent:** 4 spaces
- **Quotes:** Single quotes
- **Semicolons:** No
- **Comma Dangle:** Never on functions, always-multiline on arrays/objects

### Custom ESLint Rules

**Location:** `/eslint-rules/`

- `enforce-destructuring-newline.mjs` - Enforce newlines in destructuring
- `prefer-generic-type-annotation.mjs` - Prefer generic type annotations

### Type Naming Convention (MANDATORY)

- **Interfaces:** Must start with `I` (e.g., `IUser`, `IVerbIndex`)
- **Type Aliases:** Must start with `T` (e.g., `TUserRole`, `TStatus`)

### Import Order

1. Builtin (Node.js)
2. External (npm packages)
3. Internal (absolute imports with `~/` or `~~/`)
4. Parent/Sibling (relative imports - NOT ALLOWED, use absolute)
5. Index
6. Object imports
7. Type imports

**Restriction:** Relative imports (`.`, `../`) are forbidden - use absolute imports with `~/` or `~~/`

### Vue Component Formatting

- HTML indent: 4 spaces
- Double quotes for attributes
- Attributes per line: 3 single-line, 1 multi-line
- Self-closing tags for components
- Max line length: 120 characters (with exceptions for patterns like `class=`, `v-`, etc.)

### Component Block Order

Scripts must come before templates, templates before styles.

### Ignored Paths

- `app/components/Editor/**` - Custom editor components
- `server/db/verbs/**` - Verb database files

---

## 5. Nuxt Configuration

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/nuxt.config.ts`

### Core Settings

```ts
export default defineNuxtConfig({
  srcDir: "app", // Frontend source directory
  dir: { public: "public" }, // Public assets folder
  pages: true, // Enable file-based routing
  components: [
    {
      // Auto component importing
      path: "~/components",
      pathPrefix: false,
    },
  ],
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
});
```

### Modules

- `@nuxt/eslint` - ESLint integration
- `@nuxt/ui` - UI component library

### App Configuration

- **Title:** "Turoyo Verb Glossary"
- **Theme Color:** #2e7d73 (Teal)
- **Favicons:** SVG favicon + Safari pinned tab

### CSS

- Main stylesheet: `~/assets/css/main.css`

### Runtime Configuration

```ts
runtimeConfig: {
  betterAuthSecret: '',
  databaseUrl: '',
  googleClientId: '',
  googleClientSecret: '',
  public: {
    siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://turoyo-verb-glossary.lvh.me:3456'
  }
}
```

### Development Server

- **Host:** 0.0.0.0
- **Port:** 3456
- **Protocol:** HTTPS (with self-signed cert via mkcert)
- **URL:** https://turoyo-verb-glossary.lvh.me:3456

### Vite Configuration

- **mkcert plugin:** Auto-generates HTTPS certificates for `*.lvh.me`, `localhost`
- **Watch ignored:** Extensive list excluding build/data directories
- **Source maps:** Disabled in production

### Nitro (Server) Configuration

```ts
nitro: {
  preset: process.env.VERCEL ? 'vercel'
        : process.env.CLOUDFLARE ? 'cloudflare-pages'
        : undefined,
  scanDirs: ['server'],
  publicAssets: [{ dir: 'public', baseURL: '/' }],
}
```

### Route Rules (Caching)

- `/_nuxt/**` - 1 year immutable cache
- `/favicon.ico`, `/favicon.svg`, `/safari-pinned-tab.svg` - 1 year immutable

### Icon Configuration

- **Provider:** Iconify
- **Collections:** Heroicons, Lucide
- **Mode:** SVG
- **Client bundle limit:** 512KB

### ESLint Config (in Nuxt)

- **Stylistic indent:** 4
- **Quotes:** Single
- **Semicolons:** No
- **Comma dangle:** Never

---

## 6. Database Schema (Drizzle ORM)

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/server/db/schema.ts`
**Config:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/drizzle.config.ts`

### Database Type

- **Dialect:** PostgreSQL (via Neon serverless)
- **ORM:** Drizzle ORM

### Core Tables

**user**

```ts
- id: text (PK)
- name: text
- email: text (UNIQUE)
- emailVerified: boolean (default: false)
- image: text (nullable)
- role: enum (admin | user | pending | blocked, default: pending)
- createdAt: timestamp
- updatedAt: timestamp
```

**session**

```ts
- id: text (PK)
- token: text (UNIQUE)
- expiresAt: timestamp
- userId: text (FK -> user.id, CASCADE)
- ipAddress: text
- userAgent: text
- createdAt: timestamp
- updatedAt: timestamp
```

**account** (OAuth/Auth provider accounts)

```ts
- id: text (PK)
- accountId: text
- providerId: text
- userId: text (FK -> user.id, CASCADE)
- accessToken, refreshToken, idToken: text
- accessTokenExpiresAt, refreshTokenExpiresAt: timestamp
- scope: text
- password: text
- createdAt, updatedAt: timestamp
```

**verification** (Email/2FA verification)

```ts
- id: text (PK)
- identifier: text
- value: text
- expiresAt: timestamp
- createdAt, updatedAt: timestamp
```

**userSessionActivity**

```ts
- id: text (PK)
- sessionId: text (FK, UNIQUE)
- userId: text (FK)
- ipAddress, userAgent: text
- createdAt, lastActivityAt: timestamp
- totalRequests, searchRequests, statsRequests: integer
- lastSearchQuery: text
- lastFilters: jsonb
```

**userActivityLog**

```ts
- id: text (PK)
- userId: text (FK)
- sessionActivityId: text (FK, nullable)
- eventType: enum (activity event types)
- host, path, query: text
- filters, metadata: jsonb
- resultCount: integer
- statusCode: integer (default: 200)
- createdAt: timestamp
```

### Enums

- **userRoleEnum:** admin | user | pending | blocked
- **activityEventTypeEnum:** Defined in `shared/config/activityEventTypes.ts`

### Database Migrations

Located in `/drizzle/` directory:

- `0000_vengeful_night_thrasher.sql`
- `0001_known_thunderbolt.sql`
- `0002_thin_songbird.sql`
- `0003_left_stephen_strange.sql`

---

## 7. Environment Variables

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/.env.example`

```env
# Authentication
NUXT_GOOGLE_CLIENT_SECRET=your_google_client_secret
NUXT_GOOGLE_CLIENT_ID=your_google_client_id

# Database (PostgreSQL via Neon)
NUXT_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Better Auth Secret (32+ characters recommended)
NUXT_BETTER_AUTH_SECRET=your_32_char_secret_key

# Verb Database (SQLite for verb storage)
VERB_DATABASE=sqlite
VERB_DATABASE_PATH=.data/db/verbs.db
```

---

## 8. Key Packages & Libraries

### VueUse

- Comprehensive composition API utilities
- Used for reactive utilities and hooks
- Route-aware composables available

### Better Auth

- Modern authentication library
- Google OAuth integration
- Session management built-in

### Drizzle ORM

- Type-safe SQL toolkit
- Full TypeScript support
- PostgreSQL dialect for production

### Tailwind CSS 4

- Latest version with better performance
- Integrated with @nuxt/ui
- Custom color schemes (primary: teal, gray: slate)

### @nuxt/ui

- Production-ready components
- Built on Headless UI & Radix UI concepts
- Tailwind CSS powered

---

## 9. API Endpoints

### Authentication

- `POST /api/auth/[...all]` - Better Auth routes

### Verbs

- `GET /api/verb/[root]` - Get verb by root

### Search

- `POST /api/search/fulltext` - Full-text search
- `POST /api/search/roots` - Search verb roots

### User

- `GET /api/user/me` - Current user profile

### Admin

- `GET /api/admin/users` - List users
- `PATCH /api/admin/users/[id]/activate` - Activate user
- `PATCH /api/admin/users/[id]/block` - Block user
- `GET /api/admin/sessions` - Active sessions
- `GET /api/admin/activity` - Activity log
- `GET /api/admin/pending-count` - Pending user count

### Statistics

- `GET /api/stats` - Verb statistics

---

## 10. Server Services

**Location:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/server/services/`

### Core Services

- **searchFullText.ts** - Full-text search implementation
- **searchRoots.ts** - Root-based search
- **calculateStats.ts** - Statistics generation
- **generateVerbMetadata.ts** - Verb metadata creation
- **extractMetadata.ts** - Metadata extraction
- **extractVerbPreview.ts** - Verb preview generation

### Authentication Services

- **checkAdminRole.ts** - Admin role verification
- **requireAdmin.ts** - Admin requirement middleware

### Activity Tracking

- `/activity/*` - Session activity logging services

---

## 11. Type System Structure

### Type Naming Convention (Enforced)

- **Interfaces:** `I` prefix (e.g., `IVerb`, `IUser`, `IExample`)
- **Type Aliases:** `T` prefix (e.g., `TUserRole`, `TStatus`)

### Frontend Types (app/types/)

- `IVerbIndex.ts` - Verb index structure
- `IFilterableVerb.ts` - Verb with filters
- `IExample.ts` - Example structure
- `IGlossToken.ts` - Gloss token
- `IConjugationGroup.ts` - Conjugation grouping
- `IEtymon.ts` - Etymology info
- `IStructuredExample.ts` - Structured example
- `INavigationState.ts` - Navigation state
- `INavigationDecision.ts` - Navigation decision
- `ITextSegment.ts` - Text segment
- `ISelectOption.ts` - Select option
- `IStatistics.ts` - Statistics
- `IFilters.ts` - Filter criteria
- `IExampleToken.ts` - Example token
- `ICrossReferences.ts` - Cross references
- `ITransformedStem.ts` - Transformed stem
- `css-highlight-api.d.ts` - CSS Highlight API types

### Shared Types (shared/types/)

- `IVerb.ts` - Main verb definition
- `IStem.ts` - Verb stem
- `IEtymology.ts` - Etymology details
- `IExcerpt.ts` - Excerpt/example
- `IAuthUser.ts` - Authenticated user
- `TUserRole.ts` - User role type
- `IUserActivityLog.ts` - Activity logging
- `IUserSessionActivity.ts` - Session activity
- `IVerbMetadata.ts` - Verb metadata
- `IVerbMetadataWithPreview.ts` - With preview
- `IAdminActivityResponse.ts` - Admin activity response
- `IAdminSessionsResponse.ts` - Admin sessions response

---

## 12. Build & Deployment

### Build Output

- **Nuxt:** `.nuxt/` (dev), `dist/` (prod)
- **Nitro:** `.output/` (server output)

### Deployment Targets

- **Vercel** - `preset: 'vercel'`
- **Cloudflare Pages** - `preset: 'cloudflare-pages'`
- **Custom server** - Default Nitro server

### Build Configuration

```bash
pnpm build                # Standard build
CLOUDFLARE=1 pnpm build  # Cloudflare-specific build
```

### Vercel Configuration

- Project file: `.vercel/project.json`
- Ignore rules: `.vercelignore`
- Ignores Vercel API routes in production

---

## 13. Development Tools & Utilities

### Makefile Targets

```makefile
make parse              # Parse DOCX files to JSON
make migrate-sqlite     # Migrate JSON to SQLite
make migrate-postgres   # Migrate SQLite to Postgres
make deploy-verbs       # Full pipeline (parse + migrate)
make test-verbs         # Test verb API locally
make clean-db           # Delete SQLite database
```

### Python Scripts

- **parser/parse_docx_production.py** - Main DOCX parser
- **parser/regression_validator.py** - Validate parsing
- **scripts/migrate_json_to_sqlite.py** - JSON to SQLite
- **scripts/migrate_sqlite_to_postgres.py** - SQLite to Postgres

### Git Hooks (Husky)

- Pre-commit hooks via husky + lint-staged
- Automatic linting before commits

---

## 14. Key Features & Patterns

### Authentication

- Google OAuth via Better Auth
- User roles: admin, user, pending, blocked
- Session management with activity tracking

### Search Capabilities

- Full-text search across verb data
- Root-based search
- Filtered results with statistics

### Data Formats

- **Frontend DB:** SQLite (`.data/db/verbs.db`)
- **Production DB:** PostgreSQL (via Neon)
- **Data files:** JSON (`data/verbs_final.json`)

### Component Architecture

- Fully typed Vue 3 SFCs
- Composition API with composables
- Auto-imported components
- Editor components in isolation

### Server-Side Rendering

- Full SSR with Nuxt 4
- Automatic page generation
- Middleware-based routing

---

## 15. Deployment Notes

### Hosting

- **Dev URL:** https://turoyo-verb-glossary.lvh.me:3456
- **Public URL:** `NUXT_PUBLIC_SITE_URL` environment variable

### Database

- **Auth/Sessions:** PostgreSQL (Neon serverless)
- **Verbs:** SQLite (for local dev), migrated to Postgres for production

### Caching Strategy

- Static assets: 1 year immutable cache
- Dynamic routes: Standard HTTP caching

### API Rate Limiting

- Activity tracking on all requests
- User session activity monitoring
- Request counting per session

---

## Summary

This is a full-stack Nuxt 4 application with:

- **Type-safe** TypeScript throughout
- **Enforced naming** conventions (I/T prefixes)
- **Strict linting** with custom ESLint rules
- **Modern stack** (Vue 3, Tailwind CSS 4, Drizzle ORM)
- **Production-ready** authentication and authorization
- **Multi-database** support (SQLite dev, PostgreSQL prod)
- **Comprehensive** data model for linguistic glossary
- **Scalable** server architecture with Nitro

All code should follow the established patterns and conventions above.
