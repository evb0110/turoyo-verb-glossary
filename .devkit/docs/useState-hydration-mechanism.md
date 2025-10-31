# How useState Hydration Works in Nuxt 4

## The Hydration Mechanism

### Step-by-Step Flow

#### 1. Server-Side Execution (Middleware Runs)

```typescript
// app/middleware/auth.global.ts (SERVER)
const userData = await $fetch("/api/user/me", { headers: event.headers });

// This is the magic line:
useState("auth:user").value = userData;
```

**What happens internally:**

```typescript
// Nuxt's useState implementation (simplified)
function useState(key: string, init?: () => any) {
  const nuxtApp = useNuxtApp();

  if (import.meta.server) {
    // Server: Store in nuxtApp.payload
    if (!nuxtApp.payload.state[key]) {
      nuxtApp.payload.state[key] = init ? init() : undefined;
    }
    return toRef(nuxtApp.payload.state, key);
  }
}
```

**Server stores data in `nuxtApp.payload.state`:**

```javascript
nuxtApp.payload.state = {
  "auth:user": { id: "123", name: "John", role: "admin" },
  "auth:sessionStatus": "authenticated",
  // ... other useState values
};
```

---

#### 2. Server Renders HTML with Embedded Payload

**Nuxt serializes the payload and embeds it in HTML:**

```html
<!DOCTYPE html>
<html>
  <head>
    ...
  </head>
  <body>
    <div id="__nuxt">
      <!-- Your rendered page content -->
      <header>...</header>
      <main>Welcome, John!</main>
    </div>

    <!-- THE HYDRATION PAYLOAD -->
    <script type="application/json" id="__NUXT_DATA__">
      {
          "state": {
              "auth:user": {"id":"123","name":"John","role":"admin"},
              "auth:sessionStatus": "authenticated"
          },
          "serverRendered": true,
          "path": "/dashboard",
          "pinia": {},
          "config": {...}
      }
    </script>

    <!-- Then your Vue app bundle -->
    <script type="module" src="/_nuxt/app.js"></script>
  </body>
</html>
```

**Key points:**

- Payload is JSON in a `<script type="application/json">` tag
- ID is `__NUXT_DATA__` (Nuxt 4 standard)
- Contains all `useState` values from server-side execution
- Sent as part of the initial HTML (no separate request needed!)

---

#### 3. Client-Side Hydration

**Browser receives HTML and JavaScript loads:**

```typescript
// Nuxt's client-side initialization (simplified)
const nuxtApp = createNuxtApp();

// 1. Read payload from DOM
const payloadElement = document.getElementById("__NUXT_DATA__");
const payload = JSON.parse(payloadElement.textContent);

// 2. Restore state
nuxtApp.payload = payload;
```

**Now when client code calls `useState`:**

```typescript
// app/composables/useAuth.ts (CLIENT)
const user = useState<IAuthUser | null>("auth:user", () => null);

// Nuxt's useState on client:
function useState(key: string, init?: () => any) {
  const nuxtApp = useNuxtApp();

  if (import.meta.client) {
    // Client: Read from already-loaded payload
    if (nuxtApp.payload.state[key] === undefined) {
      nuxtApp.payload.state[key] = init ? init() : undefined;
    }
    return toRef(nuxtApp.payload.state, key);
  }
}
```

**Result:**

```typescript
user.value; // { id: '123', name: 'John', role: 'admin' }
// Same object that server set!
```

---

## Visual Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│ SERVER (Node.js)                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. User requests /dashboard                                     │
│    ↓                                                             │
│ 2. Middleware runs:                                             │
│    userData = await $fetch('/api/user/me')                      │
│    → DB query: { id: '123', role: 'admin' }                     │
│    ↓                                                             │
│ 3. useState('auth:user').value = userData                       │
│    → Stores in: nuxtApp.payload.state['auth:user']             │
│    ↓                                                             │
│ 4. Page renders with user data                                  │
│    → HTML: <main>Welcome, John!</main>                          │
│    ↓                                                             │
│ 5. Serialize payload to JSON                                    │
│    → <script id="__NUXT_DATA__">                                │
│      {"state":{"auth:user":{...}}}                              │
│      </script>                                                   │
│    ↓                                                             │
│ 6. Send HTML to browser ──────────────────────┐                │
│                                                 │                │
└─────────────────────────────────────────────────┼────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ CLIENT (Browser)                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 7. Receive HTML                                                  │
│    ↓                                                             │
│ 8. Parse HTML, find #__NUXT_DATA__ script                       │
│    → payload = JSON.parse(scriptContent)                        │
│    ↓                                                             │
│ 9. Initialize Nuxt app with payload                             │
│    → nuxtApp.payload.state = payload.state                      │
│    ↓                                                             │
│ 10. Vue hydrates (attaches to existing DOM)                     │
│     ↓                                                            │
│ 11. Components call useState('auth:user')                       │
│     → Returns ref to nuxtApp.payload.state['auth:user']         │
│     → Value: { id: '123', role: 'admin' }                       │
│     ↓                                                            │
│ 12. Hydration complete! ✓                                       │
│                                                                  │
│ 13. User clicks link /settings (client-side nav)                │
│     ↓                                                            │
│ 14. Middleware runs in browser:                                 │
│     const { user } = useAuth()                                  │
│     → useState('auth:user') returns same ref                    │
│     → NO API CALL! Uses existing payload data                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Nuxt 3 vs Nuxt 4 Differences

### Nuxt 3 (Old Approach)

```html
<script>
  window.__NUXT__ = {
      state: { 'auth:user': {...} },
      data: {...}
  }
</script>
```

**Issues:**

- Global pollution (`window.__NUXT__`)
- Security concerns (exposed on window)
- Debugging harder

### Nuxt 4 (Current Approach)

```html
<script type="application/json" id="__NUXT_DATA__">
  {"state":{"auth:user":{...}}}
</script>
```

**Improvements:**

- ✅ No global pollution
- ✅ JSON format (safer, compressed)
- ✅ Encapsulated in `useNuxtApp().payload`
- ✅ Better performance (payload compression)

---

## Code Example: Full Flow

### Server-Side (Middleware)

```typescript
// app/middleware/auth.global.ts
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    const userData = await $fetch("/api/user/me", { headers: event.headers });

    // SERVER: This writes to nuxtApp.payload.state
    useState("auth:user").value = userData;

    // Behind the scenes:
    // useNuxtApp().payload.state['auth:user'] = userData
  }
});
```

### Client-Side (Composable)

```typescript
// app/composables/useAuth.ts
export const useAuth = () => {
  // CLIENT: This reads from nuxtApp.payload.state (already populated!)
  const user = useState<IAuthUser | null>("auth:user", () => null);

  // Behind the scenes:
  // return toRef(useNuxtApp().payload.state, 'auth:user')

  return { user };
};
```

### HTML Output

```html
<!DOCTYPE html>
<html>
  <body>
    <div id="__nuxt">
      <!-- Pre-rendered with server data -->
      <main>Welcome, John (admin)!</main>
    </div>

    <!-- Payload for hydration -->
    <script type="application/json" id="__NUXT_DATA__">
      {
        "state": {
          "auth:user": {
            "id": "123",
            "name": "John",
            "email": "john@example.com",
            "role": "admin"
          },
          "auth:sessionStatus": "authenticated"
        }
      }
    </script>

    <script type="module" src="/_nuxt/app.js"></script>
  </body>
</html>
```

---

## Why This Matters for Our Auth Flow

### The Key Insight

**Server sets state ONCE, client reuses it MANY times:**

```
Page load (server):
  └─> DB query → useState → Payload → HTML

Navigation 1 (client):
  └─> useState → Read payload (no API!)

Navigation 2 (client):
  └─> useState → Read payload (no API!)

Navigation 3 (client):
  └─> useState → Read payload (no API!)

Page refresh (server):
  └─> DB query → useState → Payload → HTML (fresh data!)
```

### This Explains the Staleness

**Client state is frozen from initial server render:**

```
10:00 AM: Page load
  → Server queries DB: role = 'user'
  → Payload: {"auth:user": {"role": "user"}}
  → Client receives and stores

10:05 AM: Admin changes role in DB to 'blocked'

10:08 AM: User navigates /admin (client-side)
  → Client reads useState('auth:user')
  → Still has: {"role": "user"} (from 10:00 AM payload!)
  → Allows navigation ❌

10:10 AM: User refreshes page
  → Server queries DB: role = 'blocked'
  → NEW payload: {"auth:user": {"role": "blocked"}}
  → Client updates, blocks user ✓
```

---

## Advanced: How to Inspect Payload

### In Browser DevTools

```javascript
// Open console on any Nuxt page
const nuxtApp = useNuxtApp()
console.log(nuxtApp.payload.state)

// Output:
{
    'auth:user': { id: '123', name: 'John', role: 'admin' },
    'auth:sessionStatus': 'authenticated',
    // ... other useState values
}
```

### View Raw Payload in HTML

1. Load any page
2. View source (Cmd+Option+U on Mac)
3. Search for `__NUXT_DATA__`
4. See JSON payload

---

## Summary

**Hydration Flow:**

1. Server sets `useState('key').value = data`
2. Nuxt stores in `nuxtApp.payload.state['key']`
3. Nuxt serializes payload to JSON
4. JSON embedded in HTML as `<script id="__NUXT_DATA__">`
5. Browser parses JSON on load
6. Client `useState('key')` returns ref to payload data
7. No API calls needed for subsequent navigations!

**Key Points:**

- ✅ Payload is JSON in HTML (not a separate request)
- ✅ Client reads from pre-loaded payload (fast!)
- ✅ State persists across client-side navigation
- ❌ State can become stale (until page refresh)

**Why Server/Client Branches Exist:**

- Server: Has HTTP request → queries DB → populates payload
- Client: Has payload → reads existing data → no API calls

This is how SSR frameworks achieve fast navigation while maintaining server-rendered content!
