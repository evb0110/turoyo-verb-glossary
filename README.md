# Turoyo Verb Glossary

> Modern web application for browsing and searching Turoyo verbs with etymology and conjugations.

A scholarly reference for Turoyo verbs, their numbered senses and corpus evidence, with an editorial workflow for reviewing machine proposals.

## Features

- Dictionary entries at `/entry/:id` preserve roots, stems, numbered senses, detransitives, idioms and source references. Old `/verbs/:root` links redirect.
- Examples are listed by meaning and form, with Turoyo, translation and references side by side. A clickable matrix under each stem counts the examples for each meaning and form.
- Machine proposals sit, fully visible, beside the material they change: kind, target, summary, diff or proposed wording with translation, cited verses and decision buttons. Rationale, full passages and history open on demand. An entry shows all, only undecided, or no suggestions.
- Approved users accept, reject or discuss proposals with comments and full review history, and can edit a proposal's wording before accepting it. `/review` goes through one group of suggestions at a time, filters by verb or text, and has keyboard shortcuts (ignored while typing).
- `/texts` lists every text on one line, grouped by collection, with one filter. The reader shows each verse beside its translation, labels machine translations, and explains an analysed verb in place with links to its entry and suggestions; `?v=N` opens and highlights verse N. "Back" links return to the previous page at the same scroll position.
- The glossary list (with suggestion counts) and the header search cover roots, attested forms, German/English glosses, examples and corpus passages. Plain search preserves consonant diacritics while ignoring stress, vowel marks and joiners. Regex search is available.
- `/research` pages through question-tagged observations by question and root; `/help` explains the pages (`/about` redirects there).
- Self-hosted Gentium Plus, responsive layouts, dark mode and SSR. Google authentication, pending/blocked flows and user/session/activity administration are preserved.

## Glossary data and reviews

The binding format is [docs/data-contract.md](docs/data-contract.md). Nitro reads `server/assets/glossary/index.json`, `entries/*.json`, `texts/*.json` and `proposals/*.json`. The search index is built once per server instance; restart after regenerating assets. Corpus editions are private and must be present locally for a complete Vercel CLI deployment.

Reviews are stored in Postgres as one current decision per proposal (with any edited wording) plus an append-only history for undo and audit; see `docs/review-storage.md`. Decisions never rewrite the source assets; admins export them as CSV or JSON for the editors. The server brings the database to the current schema on its first request (`server/middleware/0.databaseSchema.ts`), so production needs no manual migration. The retired `verbs` table is kept but unused.

For isolated UI verification, `.devkit/site-fixture/` contains illustrative data covering all proposal kinds. Start with `NUXT_SITE_FIXTURE=1 NUXT_DEV_AUTH_BYPASS=1 pnpm dev`. Both switches require a development build. The bypass supplies an approved development user and uses process-local review history, with no database writes. Neither switch works in production. Leave the flags unset for real auth and data. To verify access denial locally, `NUXT_DEV_AUTH_ROLE=pending`, `blocked` or `guest` changes the bypass role.

## Tech Stack

### Frontend

- **[Nuxt 4](https://nuxt.com)** - Vue 3 meta-framework with SSR
- **[Vue 3](https://vuejs.org)** - Progressive JavaScript framework
- **[TypeScript](https://www.typescriptlang.org)** - Type-safe development
- **[Tailwind CSS 4](https://tailwindcss.com)** - Utility-first CSS framework
- **[@nuxt/ui](https://ui.nuxt.com)** - Beautiful UI components
- **[VueUse](https://vueuse.org)** - Composition API utilities

### Backend

- **[Nitro](https://nitro.unjs.io)** - Universal web server
- **[Better Auth](https://www.better-auth.com)** - Modern authentication
- **[Drizzle ORM](https://orm.drizzle.team)** - Type-safe database toolkit
- **[Neon Database](https://neon.tech)** - Serverless Postgres

### Development

- **[ESLint](https://eslint.org)** - Code linting and formatting
- **[Husky](https://typicode.github.io/husky)** - Git hooks for quality control
- **[lint-staged](https://github.com/lint-staged/lint-staged)** - Pre-commit checks

## Getting Started

### Prerequisites

- Node.js 20+ (or 22+)
- pnpm 9+
- Python 3.10+ (for parser)

### Installation

```bash
# Clone the repository
git clone https://github.com/evb0110/turoyo-verb-glossary.git
cd turoyo-verb-glossary

# Install dependencies
pnpm install
```

Glossary entries and proposals live under `server/assets/glossary/`. Corpus texts are staged privately before deployment. See `docs/data-contract.md` and `parser/glossary/`.

Set up environment variables:

```bash
cp .env.example .env
# Add your database and OAuth credentials
```

### Development

```bash
# Start dev server at https://turoyo-verb-glossary.lvh.me:3456
pnpm run dev

# Type checking
pnpm run typecheck

# Linting
pnpm run lint
```

### Production Build

```bash
# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

## Project Structure

```
turoyo-verb-glossary/
├── app/                          # Nuxt application
│   ├── components/               # Vue components
│   ├── composables/              # Vue composables
│   ├── layouts/                  # Layout components
│   ├── middleware/               # Route middleware
│   ├── pages/                    # Page components
│   └── plugins/                  # Nuxt plugins
├── server/                       # Nitro server
│   ├── api/                      # API routes
│   ├── assets/glossary/             # Verb JSON files (generated)
│   ├── db/                       # Database schema
│   ├── lib/                      # Server utilities
│   ├── repositories/             # Data access layer
│   ├── routes/                   # Custom routes
│   └── services/                 # Business logic
├── .devkit/                      # Parser + validation tooling (DOCX-based)
│   ├── analysis/                 # Reports and parsed DOCX output
│   └── scripts/                  # Parser + validation scripts
├── source/                       # Primary sources (see source/README.md)
├── public/                       # Static assets
└── nuxt.config.ts               # Nuxt configuration
```

## Architecture

### Three-Layer Architecture

The application follows a clean three-layer architecture:

1. **Controllers** (`server/api/**/*.ts`) - HTTP layer
   - Handle requests/responses
   - Route to services/repositories
   - Minimal business logic

2. **Services** (`server/services/*.ts`) - Business logic
   - Pure functions
   - Reusable calculations
   - Orchestration

3. **Repositories** (`server/repositories/*.ts`) - Data access
   - Pure functions
   - Database queries
   - Storage access

### Data pipeline

DOCX sources → `parser/glossary/` → `server/assets/glossary/entries/` and `index.json`.
Corpus readers produce `texts/` occurrences and `proposals/`; the website treats all three as read-only assets. Reviews alone are written to Postgres.

## API routes

- `GET /api/glossary/roots` (with each root's proposal count), `/stats`, `/search?q=…&regex=true`
- `GET /api/glossary/entries/:id` (entry, its proposals and the previous/next roots)
- `GET /api/glossary/texts`, `/texts/:id` (`?v=N` returns ±3 context verses)
- `GET /api/glossary/proposals/summary`, `/proposals/undecided` (undecided count per entry), `/proposals/queue`, `/proposals/:id`, `/reviews` (current decisions), `/reviews/:id` (one proposal's history), `/research?question=…&root=…&page=N` (100 notes a page)
- `POST /api/glossary/proposals/:id/review` with `{ verdict, comment?, edited?, acceptWithChanges? }`; `DELETE` with `{ reviewId }` undoes it
- `GET /api/admin/decisions?format=csv|json` (admins)
- Existing `/api/auth/*`, `/api/user/me`, `/api/admin/*`

Glossary APIs require an approved user. Missing entries/texts return 404. Reviews validate proposal IDs, verdicts, edited wording and comment length server-side.

## Environment Variables

```bash
# Database
NUXT_DATABASE_URL=postgresql://...

# Better Auth
NUXT_BETTER_AUTH_SECRET=...  # Generate: openssl rand -base64 32

# Google OAuth
NUXT_GOOGLE_CLIENT_ID=...
NUXT_GOOGLE_CLIENT_SECRET=...

# Site URL (auto-detected on Vercel)
NUXT_PUBLIC_SITE_URL=http://localhost:3456
```

## Deployment

The application is deployed via Vercel CLI:

```bash
# Deploy to production
vercel deploy --prod

# Deploy to preview
vercel deploy
```

Configuration:

- **Preset**: Vercel (automatic in Vercel environment)
- **Node.js**: 20.x
- **Build Command**: `pnpm run build`
- **Output Directory**: `.output`

## Development Workflow

### Before Committing

```bash
# Run type checking and linting
pnpm run lint && pnpm run typecheck
```

Pre-commit hooks automatically:

- Lint and format code
- Check for type errors
- Validate imports

### Parser Changes

See `PARSING.md`: regenerate with `python3 -m parser.glossary`, then keep
`python3 -m parser.glossary.roundtrip` at 100% and `python3 -m unittest parser.glossary.test_glossary` green.

## Code Style

- **Package Manager**: pnpm only (never npm/yarn)
- **Formatting**: Enforced by ESLint
- **Imports**: Absolute paths (`~/` for app, `~~/` for server)
- **File Organization**: One export per file
- **Naming**: Interfaces use `I` prefix, Types use `T` prefix
- **Functions**: Pure functions preferred

## Contributing

This is a personal project, but feedback and suggestions are welcome! Please open an issue to discuss any changes.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Original glossary data from academic research
- Built with modern open-source technologies
- Powered by Vercel's edge network

---

**Status**: ✅ Active development | Deployed at [turoyo-verb-glossary.vercel.app](https://turoyo-verb-glossary.vercel.app)

**Version**: 1.0.0 | **Last Updated**: October 2025
