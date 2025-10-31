# Auth Flow Deep Dive: Cookie Cache vs DB Query

## Your Question

> "Why does server always query DB when it can get session from cookie? `cookieCache` is enabled, so what's the actual difference between server and client?"

Excellent question! The answer reveals an important architectural decision.

---

## What Better Auth's `cookieCache` Actually Does

```typescript
// server/lib/auth.ts
session: {
    cookieCache: {
        enabled: true,
        maxAge: 5 * 60,  // 5 minutes
    },
}
```

**Cookie cache means:**

- Session data is stored **in the cookie itself** (encrypted)
- `auth.api.getSession()` decodes the cookie WITHOUT hitting DB (for 5 min)
- After 5 minutes, it validates against DB

**What's in the cached session cookie?**

- `user.id`
- `user.email`
- `user.name`
- **NOT** our custom `role` field!

---

## Why We Still Query the Database

### Current Flow (Server)

```typescript
// server/repositories/auth/getCurrentUser.ts
export async function getCurrentUser(event: H3Event) {
  // Step 1: Check session (cached in cookie, fast)
  const session = await auth.api.getSession({ headers: event.headers });

  if (!session?.user) {
    return null; // Not logged in
  }

  // Step 2: Query DB for fresh user data (ALWAYS)
  return getUserById(session.user.id); // Gets role from DB!
}
```

### Why Not Just Use Cached Session?

**Problem:** The cookie cache doesn't include our custom `role` field!

**Scenario:**

1. User logs in as `role: 'user'`
2. Session cached in cookie for 5 minutes
3. Admin changes user to `role: 'blocked'`
4. **If we only check cookie:** User still appears as 'user' for 5 more minutes
5. **By querying DB:** We get fresh role immediately

**Trade-off:**

- ✅ **Security:** Always get current role from DB
- ❌ **Performance:** DB query on every page load

---

## What About the Client?

### Client During Navigation (Key Insight!)

```typescript
// app/middleware/auth.global.ts (client branch)
const { user, sessionStatus } = useAuth();

// Uses STATE from server hydration - NO API call!
const decision = authorizeNavigation(user.value, to.path);
```

**This is the critical difference:**

- **Server:** Queries DB on every page load/refresh
- **Client:** Uses hydrated state WITHOUT querying anything

### Client State Flow

**Initial page load:**

```
Server queries DB → Sets useState('auth:user') → HTML with embedded state → Client reads it
```

**Client-side navigation (user clicks link):**

```
Client reads useState('auth:user') → Authorization check → Navigate

NO API CALL!
```

**Manual session refresh:**

```typescript
// app/composables/useAuth.ts
const checkSession = async () => {
  const session = await client.getSession(); // Better Auth check
  if (session.data?.user) {
    const response = await $fetch<IAuthUser | null>("/api/user/me"); // DB query
    user.value = response;
  }
};
```

---

## The Real Difference: Server vs Client

| Aspect           | Server Branch         | Client Branch            |
| ---------------- | --------------------- | ------------------------ |
| **When it runs** | Page load/refresh     | Navigation (link clicks) |
| **Data source**  | Fresh DB query        | Hydrated state (stale!)  |
| **API calls**    | YES (every page load) | NO (uses cached state)   |
| **How often**    | Once per page load    | Every route change       |
| **Staleness**    | Always fresh          | Can be stale!            |

---

## The Staleness Problem You Identified

### Scenario

```
1. User visits /dashboard at 10:00 AM
   → Server queries DB: role = 'user'
   → State hydrated: { role: 'user' }

2. User browses site (client-side navigation)
   → 10:05 AM: visits /profile (uses cached state)
   → 10:10 AM: visits /settings (uses cached state)

3. Admin blocks user at 10:08 AM (DB updated: role = 'blocked')

4. User clicks /admin at 10:12 AM
   → Client checks: user.value.role === 'user' (stale!)
   → Middleware allows navigation! 🚨

5. User refreshes page at 10:15 AM
   → Server queries DB: role = 'blocked' (fresh!)
   → Redirected to /blocked
```

**Client-side auth is "soft" - real security must be server-side!**

---

## Why This Design Exists

### Performance vs Security Trade-off

**Option 1: Query DB on every navigation (current server behavior)**

- ✅ Always fresh data
- ❌ Slow, expensive (DB query every route change)

**Option 2: Use cached state on client (current client behavior)**

- ✅ Fast navigation (no API calls)
- ❌ Stale data (can be minutes old)

**Current architecture uses BOTH:**

- Server: Fresh data (security)
- Client: Cached data (performance)

### The Real Security Layer

**Middleware is not enough!** Every sensitive API endpoint must check auth:

```typescript
// server/api/admin/users.get.ts
export default defineEventHandler(async (event) => {
  const user = await getCurrentUser(event);

  if (!user || user.role !== "admin") {
    throw createError({ statusCode: 403 });
  }

  // Continue...
});
```

Even if client middleware has stale state, API endpoints check fresh DB data.

---

## Potential Improvements

### 1. Include Role in Better Auth Session

**Pros:**

- No DB query needed in middleware
- Fast server-side checks

**Cons:**

- Role changes take 5 min to propagate (cookie cache)
- Security risk if role changes aren't immediate

### 2. Periodic Client State Refresh

```typescript
// Auto-refresh every 2 minutes
setInterval(
  async () => {
    const { checkSession } = useAuth();
    await checkSession();
  },
  2 * 60 * 1000,
);
```

**Pros:**

- Client state stays fresher

**Cons:**

- Extra API calls
- Complexity

### 3. WebSocket for Real-Time Updates

**Pros:**

- Instant role change propagation

**Cons:**

- Complex infrastructure
- Overkill for most apps

### 4. Accept Current Design

**Reasoning:**

- Middleware is UX, not security
- API endpoints are the real security layer
- Staleness is acceptable for navigation
- Refresh page = fresh data

**Current design is actually reasonable!**

---

## Summary

### Your Insights Were Correct

1. ✅ **Cookie cache exists** - `auth.api.getSession()` is fast (cached 5 min)
2. ✅ **We still query DB** - to get fresh `role` field not in session
3. ✅ **Server and client are different** - server fetches, client uses cache

### The Architecture

```
Server (Page Load):
  auth.api.getSession() [cached] → getUserById() [fresh DB] → Hydrate state

Client (Navigation):
  Read cached state → NO API calls → Fast!

Client (Manual Refresh):
  checkSession() → $fetch('/api/user/me') [fresh DB] → Update state
```

### The Key Insight

**Middleware provides fast UX, not security. Real security = API endpoints checking fresh DB data.**

Client state can be stale, and that's okay because:

1. Server-side API checks are always fresh
2. Page refresh updates stale data
3. Sensitive operations (API calls) always validate

The trade-off is:

- **Fast client navigation** (cached state)
- **Fresh server security** (DB queries)
- **Acceptable staleness window** (until next page load)

This is a common pattern in SSR apps!
