# Nuxt Plugins vs Middleware: Architectural Differences

## Executive Summary

**Plugins** run once per app initialization (SSR + client hydration).
**Middleware** runs on every route navigation.

Your auth problem: Both are querying the database on every page load because middleware runs per-route, not per-app-init.

---

## Detailed Comparison

### Execution Timing

#### Plugins

```
1. Server receives request
2. Nuxt app initializes
3. → PLUGINS RUN (once per request)
4. → Page component loads
5. HTML sent to client
6. Client hydrates
7. → PLUGINS RUN AGAIN (once on client mount)
```

**Key point:** Plugins run **once per app initialization**, not per route.

#### Middleware

```
1. Server receives request
2. Nuxt app initializes
3. Plugins run
4. → MIDDLEWARE RUN (before route loads)
5. → Page component loads
6. HTML sent to client
7. Client hydrates
8. User clicks link to new route
9. → MIDDLEWARE RUN AGAIN (before new route loads)
```

**Key point:** Middleware runs **before every route navigation**.

---

## Execution Order

On SSR (first page load):

```
1. Server receives request
2. Nuxt starts
3. ✅ Plugins execute (in order defined in nuxt.config.ts or file name)
4. ✅ Middleware executes (global → route-specific)
5. ✅ Page component renders
6. HTML sent to browser
```

On client-side navigation:

```
1. User clicks link
2. ✅ Middleware executes
3. ✅ Page component renders
(Plugins don't run again - app is already initialized)
```

---

## Purpose & Use Cases

### Plugins: App-Level Setup

**Purpose:** Initialize app-wide functionality

**Use cases:**

- Set up composables/utilities
- Initialize third-party libraries
- Inject global helpers
- **Pre-populate app state during SSR**
- Configure Vue plugins
- Set up error handlers

**Examples:**

```typescript
// app/plugins/auth.server.ts
export default defineNuxtPlugin(async () => {
  // Runs once when app starts
  const user = await fetchUser();
  useState("user").value = user; // Available everywhere
});

// app/plugins/i18n.ts
export default defineNuxtPlugin(() => {
  // Set up i18n instance
  return {
    provide: {
      t: (key) => translate(key),
    },
  };
});
```

### Middleware: Route-Level Guards

**Purpose:** Control route access and navigation

**Use cases:**

- Authentication checks
- Authorization/permissions
- Redirects based on user state
- Route protection
- Analytics tracking
- Setting route-specific context

**Examples:**

```typescript
// app/middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to, from) => {
  // Runs before EVERY route navigation
  const user = useState("user").value;

  if (!user && to.path !== "/login") {
    return navigateTo("/login");
  }
});

// app/middleware/admin.ts
export default defineNuxtRouteMiddleware((to) => {
  // Runs only for routes that explicitly use it
  const user = useState("user").value;

  if (user?.role !== "admin") {
    return navigateTo("/");
  }
});
```

---

## Server vs Client Execution

### Plugins

**Control:** Via `import.meta.client` / `import.meta.server`

```typescript
// Runs on both
export default defineNuxtPlugin(() => {
  // Both server and client
});

// Server only
export default defineNuxtPlugin(() => {
  if (import.meta.client) return;
  // Server-only code
});

// Client only
export default defineNuxtPlugin(() => {
  if (import.meta.server) return;
  // Client-only code
});

// File naming convention
// *.client.ts → client only
// *.server.ts → server only
// *.ts → both
```

### Middleware

**Control:** Via `import.meta.server` / `import.meta.client`

```typescript
// Runs on both server and client
export default defineNuxtRouteMiddleware((to) => {
  // Both environments
});

// Different logic per environment
export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) {
    // Server-side logic
  } else {
    // Client-side logic
  }
});
```

---

## Access to Context

### Plugins

```typescript
export default defineNuxtPlugin((nuxtApp) => {
  // Access to:
  nuxtApp.vueApp; // Vue app instance
  nuxtApp.ssrContext; // SSR context (server only)
  nuxtApp.$config; // Runtime config
  nuxtApp.hook(); // Nuxt hooks

  // Access to request event (server only)
  const event = useRequestEvent();
  event.headers; // Request headers
  event.context; // Event context

  // Provide to entire app
  return {
    provide: {
      myHelper: () => {},
    },
  };
});
```

### Middleware

```typescript
export default defineNuxtRouteMiddleware((to, from) => {
  // Access to:
  to.path; // Target route
  from.path; // Source route
  to.params; // Route params
  to.query; // Query string

  // Access to composables
  const user = useState("user");
  const config = useRuntimeConfig();

  // Access to request event (server only)
  const event = useRequestEvent();

  // Can return:
  return navigateTo("/other"); // Redirect
  return abortNavigation(); // Cancel navigation
  // or nothing               // Allow navigation
});
```

---

## Performance Implications

### Plugins: Once Per App Init

```
Page 1 load:  Plugin runs (200ms)
Page 2 nav:   Plugin doesn't run
Page 3 nav:   Plugin doesn't run
Hard reload:  Plugin runs (200ms)

Total: 200ms for entire session (except hard reloads)
```

### Middleware: Every Route Navigation

```
Page 1 load:  Middleware runs (200ms)
Page 2 nav:   Middleware runs (200ms)
Page 3 nav:   Middleware runs (200ms)
Hard reload:  Middleware runs (200ms)

Total: 200ms × number of navigations
```

---

## Your Current Problem

### What's Happening

```
Page Request
  ↓
Plugin runs:      fetchUser() → 472ms
  ↓
Middleware runs:  checkAuth() → 204ms
  ↓
Total: 676ms BLOCKING SSR
```

### Why It's Duplicated

1. **Plugin** fetches user data "once" per app init
2. **Middleware** checks auth "every" route navigation
3. **On SSR:** Both happen on same request (app init = route navigation)
4. **On client nav:** Only middleware runs (plugin state already exists)

### The Issue

- Both are doing database queries during SSR
- Middleware can't trust plugin state (timing uncertainty)
- Plugin can't prevent middleware from running
- They're independent but need the same data

---

## Solution Patterns

### Pattern 1: Middleware Only (Recommended for Your Case)

**Remove plugin, consolidate into middleware**

```typescript
// app/middleware/auth.global.ts
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    // Fetch user data ONCE
    const userData = await fetchUser();

    // Populate state for SSR hydration
    useState("auth:user").value = userData;

    // Do redirects based on userData
    if (!userData && to.path !== "/login") {
      return navigateTo("/login");
    }
  }

  // Client-side logic uses existing state
  const user = useState("auth:user").value;
  // ... route protection logic
});
```

**Pros:**

- Single database query per request
- Simpler mental model (one auth entry point)
- Middleware naturally runs before routes

**Cons:**

- Runs on every navigation (even on client)
- Need to skip DB query on client-side navigations

### Pattern 2: Plugin Populates, Middleware Reads

**Plugin fetches data, middleware uses it**

```typescript
// app/plugins/auth.server.ts
export default defineNuxtPlugin(async () => {
  if (import.meta.client) return;

  const userData = await fetchUser();
  useState("auth:user").value = userData;
});

// app/middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to) => {
  // Read from state (no API call!)
  const user = useState("auth:user").value;

  // Route protection logic
  if (!user && to.path !== "/login") {
    return navigateTo("/login");
  }
});
```

**Pros:**

- Clear separation: plugin=fetch, middleware=protect
- Plugin runs once, middleware is fast

**Cons:**

- Plugin execution order not 100% guaranteed before middleware
- Need null checks in middleware
- More complex to reason about

### Pattern 3: Event Context Sharing

**Middleware fetches once, stores in event context**

```typescript
// app/middleware/auth.global.ts
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    const event = useRequestEvent();

    // Check if already fetched
    if (!event.context.userData) {
      event.context.userData = await fetchUser();
    }

    // Use cached data
    const userData = event.context.userData;
    useState("auth:user").value = userData;

    // Route protection...
  }
});
```

**Pros:**

- Caches within single request
- Middleware controls everything

**Cons:**

- Still runs on every client navigation
- More complex state management

---

## Recommendation for Your App

**Use Pattern 1: Middleware Only**

Why:

1. You're already doing auth checks in middleware
2. Middleware runs at the perfect time (before route loads)
3. Simpler than coordinating plugin + middleware
4. Single query per request
5. Easy to add client-side optimization later

### Implementation

1. Delete `app/plugins/auth.server.ts`
2. Modify `app/middleware/auth.global.ts`:
   - Change `/api/auth/check` to `/api/user/me`
   - Add `useState` population
   - Skip DB query on client navigations

### Client Navigation Optimization

```typescript
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    // Server: fetch from DB
    const userData = await $fetch("/api/user/me");
    useState("auth:user").value = userData;
  } else {
    // Client: state already exists from SSR or previous nav
    // Just use it for route protection
  }

  const user = useState("auth:user").value;
  // ... route protection logic
});
```

This way:

- SSR: One DB query via middleware
- Client nav: No DB query, state already exists
- Simple, fast, maintainable

---

## Key Takeaways

1. **Plugins = App setup** (runs once per app lifecycle)
2. **Middleware = Route guard** (runs per navigation)
3. **SSR = App init + first navigation** (both run)
4. **Client nav = Only middleware** (plugin state persists)
5. **Auth fits middleware better** (route protection is its job)
6. **Plugins for state = Bad pattern** when middleware needs same data
