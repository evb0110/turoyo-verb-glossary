# Turoyo Verb Glossary

> Modern web application for browsing and searching Turoyo verbs with etymology and conjugations.

A comprehensive digital glossary featuring **1,696 Turoyo verbs** with full conjugation tables, etymological information, and cross-references. Built with modern web technologies for fast, responsive browsing.

## Features

- **🔍 Smart Search** - Search by root, meaning, or full-text across all examples
- **📚 Comprehensive Data** - 3,553 stems, 4,685 conjugation examples
- **🌐 Etymology** - 10+ source languages (Arabic, Middle Eastern Aramaic, Kurdish, Turkish, etc.)
- **⚡ Fast SSR** - Server-side rendering for instant page loads
- **🎨 Modern UI** - Clean interface built with Tailwind CSS 4
- **🔐 Authentication** - Google OAuth integration via Better Auth

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

# Generate verb data
python3 parser/parse_verbs.py

# Set up environment variables
cp .env.example .env
# Add your database and OAuth credentials
```

### Development

```bash
# Start dev server at http://localhost:3456
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
│   ├── assets/verbs/             # Verb JSON files (generated)
│   ├── db/                       # Database schema
│   ├── lib/                      # Server utilities
│   ├── repositories/             # Data access layer
│   ├── routes/                   # Custom routes
│   └── services/                 # Business logic
├── parser/                       # Python parser
│   ├── parse_verbs.py            # Master parser
│   ├── snapshot_baseline.py      # Validation baseline
│   └── html_utils.py             # HTML utilities
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

### Data Pipeline

```
Source HTML → Parser → JSON Files → API → Frontend
```

- **Source**: Proprietary HTML glossary (not in repo)
- **Parser**: `parser/parse_verbs.py` - Extracts and structures data
- **Storage**: `server/assets/verbs/*.json` - Individual verb files
- **API**: Nitro endpoints serve data via `useStorage('assets:server')`
- **Stats**: Calculated dynamically from verb files

## API Routes

```
GET /api/verbs              # Search verbs (query params: q, type)
GET /api/verbs/:root        # Get specific verb by root
GET /api/stats              # Get dataset statistics
GET /api/auth/*             # Authentication endpoints
GET /api/user/me            # Current user info
```

## Data Generation

Verb data is generated from source HTML using the parser:

```bash
# Generate all verb files
python3 parser/parse_verbs.py

# With validation
python3 parser/parse_verbs.py --validate

# Create validation baseline
python3 parser/snapshot_baseline.py
```

The parser:

- Extracts 1,696 verbs from HTML source
- Generates individual JSON files
- Adds homonym numbering
- Creates validation reports
- Validates against baseline (prevents regressions)

**Note**: Generated verb files are not included in version control. Run the parser to generate them locally.

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://...

# Better Auth
BETTER_AUTH_SECRET=...  # Generate: openssl rand -base64 32

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

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

When modifying the parser:

```bash
# 1. Create baseline (first time)
python3 parser/snapshot_baseline.py

# 2. Make changes
vim parser/parse_verbs.py

# 3. Validate (prevents regressions)
python3 parser/parse_verbs.py --validate

# 4. Check results
open data/validation/regression_report.html
```

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

**Status**: ✅ Active development | Deployed at [turoyo-verbs.vercel.app](https://turoyo-verbs.vercel.app)

**Version**: 1.0.0 | **Last Updated**: October 2025
