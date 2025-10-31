# Middleware Server/Client Separation Explained

## The Two Execution Contexts

In Nuxt 4 with SSR, middleware runs in **TWO different environments**:

### 1. Server Context (`import.meta.server`)

**When it runs:** Initial page load or hard refresh

**Example flow:**

```
User visits: https://example.com/dashboard
  ↓
Server receives HTTP request (with cookies, headers)
  ↓
Middleware runs ON SERVER
  ↓
Server fetches user from database using session cookie
  ↓
Server renders HTML with auth state embedded
  ↓
HTML + state sent to browser
```

**What it has access to:**

- ✅ HTTP request object (`event`)
- ✅ Request headers (cookies, auth tokens)
- ✅ Can call server-only APIs
- ✅ Can read database directly
- ❌ No DOM, no `window` object

**Code:**

```typescript
if (import.meta.server) {
  const event = useRequestEvent(); // HTTP request
  const userData = await $fetch("/api/user/me", {
    headers: event.headers, // Forward cookies
  });

  // Set state for hydration
  useState("auth:user").value = userData;
}
```

---

### 2. Client Context (`import.meta.client`)

**When it runs:** Client-side navigation (SPA mode)

**Example flow:**

```
User clicks link: /dashboard → /admin
  ↓
No server request! (SPA navigation)
  ↓
Middleware runs IN BROWSER
  ↓
Client checks auth using existing state
  ↓
Client navigates (no page reload)
```

**What it has access to:**

- ✅ Reactive state (Vue refs, composables)
- ✅ Browser APIs (window, localStorage)
- ✅ State set by server during SSR
- ❌ No HTTP request object
- ❌ No access to cookies (except via document.cookie)

**Code:**

```typescript
// Client-side (runs in browser)
const { user, sessionStatus } = useAuth(); // Reactive state

const decision = authorizeNavigation(user.value, to.path);
if (decision.shouldRedirect) {
  return navigateTo(decision.redirectTo);
}
```

---

## Why We Need Both Branches

### Problem: Different Data Sources

**Server has:** HTTP headers with session cookie
**Client has:** Reactive state from `useAuth()`

You **cannot** use `useAuth()` on the server because Better Auth client doesn't exist server-side.
You **cannot** use `event.headers` on the client because there's no HTTP request.

### Solution: Branch Based on Context

```typescript
export default defineNuxtRouteMiddleware(async (to) => {
  // SERVER: Initial page load
  if (import.meta.server) {
    // Fetch fresh data from database using cookies
    const userData = await $fetch("/api/user/me", {
      headers: event.headers, // Session cookie
    });

    // Populate state for client hydration
    useState("auth:user").value = userData;

    // Check authorization
    const decision = authorizeNavigation(userData, to.path);
    if (decision.shouldRedirect) {
      return navigateTo(decision.redirectTo);
    }
  }

  // CLIENT: Subsequent navigation
  else {
    // Use state already loaded from server
    const { user } = useAuth();

    // Check authorization (same logic!)
    const decision = authorizeNavigation(user.value, to.path);
    if (decision.shouldRedirect) {
      return navigateTo(decision.redirectTo);
    }
  }
});
```

---

## How State Flows: Server → Client

### Step-by-Step Example

**1. User visits `/dashboard` (first load)**

**Server-side:**

```typescript
// Runs on Nuxt server
const userData = await $fetch("/api/user/me", { headers: event.headers });
// userData = { id: '123', name: 'John', role: 'admin' }

useState("auth:user").value = userData; // Store in SSR state
```

**2. Server renders HTML and embeds state:**

```html
<html>
  <script>
    window.__NUXT__ = {
      state: {
        "auth:user": { id: "123", name: "John", role: "admin" },
        "auth:sessionStatus": "authenticated",
      },
    };
  </script>
  <body>
    ...
  </body>
</html>
```

**3. Browser receives HTML and hydrates:**

```typescript
// Client reads embedded state
const { user } = useAuth();
// user.value = { id: '123', name: 'John', role: 'admin' } (from SSR)
```

**4. User clicks link to `/admin` (client-side navigation)**

```typescript
// Runs in browser (NO server request)
const { user } = useAuth(); // Still has SSR data!
const decision = authorizeNavigation(user.value, to.path);
// decision = { shouldRedirect: false } (admin can access)
```

---

## Why Not Just Use Client-Side?

### Problem 1: Initial Page Load Security

If middleware only ran client-side:

```typescript
// BAD: Client-only middleware
export default defineNuxtRouteMiddleware(async (to) => {
  const { user } = useAuth();

  if (!user.value) {
    return navigateTo("/login");
  }
});
```

**What happens:**

1. User visits `/admin` directly (not logged in)
2. Server renders `/admin` page (no auth check!)
3. HTML sent to browser with admin content
4. Client hydrates and THEN redirects to `/login`
5. **Problem:** User briefly sees admin content!

### Problem 2: SEO and Crawlers

- Search engines don't execute JavaScript
- Server-side auth ensures proper redirects for crawlers
- Prevents indexing of protected pages

### Problem 3: Performance

- Client-side only: Server renders page → sends HTML → client redirects (wasted work)
- Server-side check: Server redirects immediately (no wasted render)

---

## Why Not Just Use Server-Side?

### Problem: Client-Side Navigation

After hydration, Nuxt uses **SPA mode** for navigation:

```
User on /dashboard → clicks link to /settings
  ↓
NO server request (client-side routing)
  ↓
Middleware runs, but import.meta.server = false
  ↓
Need client-side auth check!
```

If middleware only ran server-side, client navigation would bypass auth entirely.

---

## Current Middleware Analysis

### What It Does Right ✅

1. **Server-side initial check:**
   - Fetches fresh user data from database
   - Sets state for hydration
   - Prevents unauthorized page renders

2. **Client-side subsequent checks:**
   - Uses existing state (no unnecessary API calls)
   - Fast navigation (no server roundtrip)

3. **Shared authorization logic:**
   - Both branches use same `authorizeNavigation()` function
   - Single source of truth for rules

### Potential Issues ❓

1. **Client state staleness:**
   - What if user's role changes while browsing?
   - Client keeps using old state from SSR
   - Possible fix: Periodic state refresh

2. **Inconsistent loading states:**
   - Server: No loading state (synchronous check)
   - Client: Has 'idle' and 'loading' states
   - Lines 34-36: What triggers these states?

---

## Common Questions

### Q: Why does server set `useState` if it's server-side?

**A:** `useState` in Nuxt is **SSR-aware**. When set on server, it:

1. Stores value in server memory
2. Serializes it into HTML payload
3. Browser reads it during hydration
4. Client-side code sees the same value

### Q: Why can't we just use `getCurrentUser(event)` directly?

**A:** We could! Currently using `$fetch('/api/user/me')` which Nitro optimizes to direct call anyway.

Alternative (might be cleaner):

```typescript
if (import.meta.server) {
  const { getCurrentUser } = await import(
    "~~/server/repositories/auth/getCurrentUser"
  );
  const userData = await getCurrentUser(event);
}
```

### Q: Does middleware run on EVERY navigation?

**A:** Yes!

- Server: On initial page load/refresh
- Client: On every route change (even same page with different params)

### Q: What about API routes? Does middleware run?

**A:** No! Route middleware only runs for **pages**, not API endpoints.
API endpoints need their own auth checks.

---

## Recommendations

### 1. Consider Server-Only Initial Fetch

Instead of `$fetch`, use repository directly:

```typescript
if (import.meta.server) {
  const { getCurrentUser } = await import(
    "~~/server/repositories/auth/getCurrentUser"
  );
  const userData = await getCurrentUser(event);
  // More explicit than $fetch
}
```

### 2. Add Client State Refresh

If user roles can change:

```typescript
// Client-side
if (sessionStatus.value === "authenticated") {
  // Refresh if state is old
  await checkSession();
}
```

### 3. Simplify Client Loading Logic

Lines 34-36 skip auth check if loading. When does this happen?
Might indicate state management issue in `useAuth()`.

---

## Summary

**Why two branches?**

- **Server:** Has HTTP request, no reactive state
- **Client:** Has reactive state, no HTTP request
- **Solution:** Different data sources, same authorization logic

**How they work together:**

1. Server fetches user → sets state → checks auth
2. State embedded in HTML
3. Client hydrates → reads state → checks auth on navigation

**Key insight:** Server does the expensive work (database query), client reuses the result for fast navigation.
