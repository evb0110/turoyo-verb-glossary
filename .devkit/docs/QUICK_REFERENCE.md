# Turoyo Verb Glossary - Quick Reference Guide

## Directory Quick Paths

```
Frontend:        app/
Backend:         server/
Shared Code:     shared/
Database Schema: server/db/schema.ts
Configuration:   nuxt.config.ts, eslint.config.mjs, package.json
```

## Critical Naming Rules (ENFORCED)

```typescript
interface IMyType {} // ✓ Correct: Interface with I prefix
type TMyType = string; // ✓ Correct: Type alias with T prefix
interface MyType {} // ✗ WRONG: Missing I prefix
type MyType = string; // ✗ WRONG: Missing T prefix
```

## Code Quality Checks

```bash
pnpm lint                       # Lint & auto-fix
pnpm typecheck                  # Type checking
pnpm build                      # Production build
```

## Import Rules

```typescript
// ✓ Correct - Absolute imports
import { useAuth } from "~/composables/useAuth";
import { IVerbData } from "~/types/IVerbData";

// ✗ Wrong - Relative imports NOT allowed
import { useAuth } from "../composables/useAuth";
import { IVerbData } from "../types/IVerbData";
```

## File Organization

### Types

- **Frontend:** `app/types/I*.ts`
- **Server:** `server/types/I*.ts`
- **Shared:** `shared/types/I*.ts` or `shared/types/T*.ts`

### Services

- **Location:** `server/services/`
- **Pattern:** Export functions that handle business logic

### Components

- **Location:** `app/components/`
- **Auto-imported:** No need to import in components
- **Exception:** `app/components/Editor/**` ignored by ESLint

### Composables

- **Location:** `app/composables/use*.ts`
- **Pattern:** Export `function useFeatureName() { }`

### API Endpoints

- **Location:** `server/api/[feature]/[endpoint].[method].ts`
- **Pattern:** Default export of handler function

## Database Info

- **Type:** PostgreSQL (production), SQLite (verb data local)
- **ORM:** Drizzle
- **Schema File:** `server/db/schema.ts`
- **Verb Data:** `.data/db/verbs.db` (SQLite)

## Environment Variables

```bash
NUXT_GOOGLE_CLIENT_ID=
NUXT_GOOGLE_CLIENT_SECRET=
NUXT_DATABASE_URL=postgresql://...
NUXT_BETTER_AUTH_SECRET=
VERB_DATABASE=sqlite
VERB_DATABASE_PATH=.data/db/verbs.db
```

## Key Types to Know

### Main Verb Type (Shared)

```typescript
import { IVerb } from "~/types/IVerb"; // Complete verb data
import { IStem } from "~/types/IStem"; // Verb stem
import { IEtymology } from "~/types/IEtymology"; // Etymology
```

### User/Auth

```typescript
import { IAuthUser } from "~/types/IAuthUser"; // Authenticated user
import { TUserRole } from "~/types/TUserRole"; // Role: admin|user|pending|blocked
```

## Common API Routes

```typescript
// Verbs
GET / api / verb / [root]; // Get verb by root

// Search
POST / api / search / fulltext; // Full-text search
POST / api / search / roots; // Root search

// User
GET / api / user / me; // Current user

// Admin
GET / api / admin / users;
PATCH / api / admin / users / [id] / activate;
PATCH / api / admin / users / [id] / block;
GET / api / admin / sessions;
GET / api / admin / activity;

// Stats
GET / api / stats; // Verb statistics
```

## Component Patterns

### Vue 3 Single File Component (SFC)

```vue
<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

interface IComponentProps {
  title: string;
  count?: number;
}

const props = withDefaults(defineProps<IComponentProps>(), {
  count: 0,
});

const route = useRoute();
const doubleCount = computed(() => props.count * 2);
</script>

<template>
  <div class="container">
    <h1>{{ props.title }}</h1>
    <p>{{ doubleCount }}</p>
  </div>
</template>

<style scoped>
.container {
  padding: 1rem;
}
</style>
```

## Composable Pattern

```typescript
export function useMyFeature() {
  const state = ref<IMyState>({});

  const action = () => {
    // Logic here
  };

  return {
    state: readonly(state),
    action,
  };
}
```

## Server Service Pattern

```typescript
// server/services/myService.ts
export async function processData(input: IInput): Promise<IOutput> {
  // Business logic
  return result;
}
```

## API Endpoint Pattern

```typescript
// server/api/feature/action.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event);

  // Process

  return { success: true, data };
});
```

## Code Style Rules

| Rule            | Style                                      |
| --------------- | ------------------------------------------ |
| Indentation     | 4 spaces                                   |
| Quotes          | Single (`'`)                               |
| Semicolons      | No                                         |
| Comma Dangle    | Never (functions), Always (arrays/objects) |
| Max Line Length | 120 characters                             |
| HTML Indent     | 4 spaces                                   |
| HTML Quotes     | Double (`"`)                               |

## Linting Disabled Paths

These paths are ignored by ESLint:

- `app/components/Editor/**` - Custom editor components
- `server/db/verbs/**` - Verb database files

## Development Server

```bash
# Start dev server
pnpm dev

# URL: https://turoyo-verb-glossary.lvh.me:3456
# HTTPS enabled automatically
```

## Build & Deploy

```bash
pnpm build              # Standard build
CLOUDFLARE=1 pnpm build # Cloudflare Pages build
pnpm generate           # Static site generation
```

## Database Schema Quick View

Key tables:

- `user` - User accounts
- `session` - User sessions
- `account` - OAuth accounts
- `userSessionActivity` - Session tracking
- `userActivityLog` - Event logging

## Making Changes

1. Check naming conventions (I/T prefix)
2. Use absolute imports (`~/`)
3. Run `pnpm lint` before committing
4. Run `pnpm typecheck` for type safety
5. Verify code follows 4-space indent, single quotes, no semis

## Gitignore Key Items

```
node_modules/
.nuxt/
dist/
.output/
.data/db/verbs.db
.env
.env.local
.devkit/
```

## Project Statistics

- 1,696 Turoyo verbs
- 3,553 stems
- 4,685 conjugation examples
- 10+ etymology source languages
