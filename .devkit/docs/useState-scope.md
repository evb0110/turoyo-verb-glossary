# Is useState Global State?

## Quick Answer

**No!** `useState` is **NOT global**. It's scoped to the **Nuxt app instance**.

---

## The Scoping Rules

### Server-Side (Critical for Security!)

**Each HTTP request gets its OWN isolated state:**

```typescript
// Request 1: User A visits /dashboard
useState("auth:user").value = { id: "123", name: "Alice" };
// Stored in: request1NuxtApp.payload.state['auth:user']

// Request 2: User B visits /dashboard (simultaneous)
useState("auth:user").value = { id: "456", name: "Bob" };
// Stored in: request2NuxtApp.payload.state['auth:user']

// ✅ NO CONFLICT! Different nuxtApp instances
```

**Visual representation:**

```
┌──────────────────────────────────────────────────┐
│ Node.js Server Process                            │
├──────────────────────────────────────────────────┤
│                                                   │
│  Request 1 (Alice):                              │
│  ┌────────────────────────────────┐              │
│  │ nuxtApp instance #1            │              │
│  │ payload.state: {               │              │
│  │   'auth:user': {id: '123'}     │              │
│  │ }                              │              │
│  └────────────────────────────────┘              │
│                                                   │
│  Request 2 (Bob):                                │
│  ┌────────────────────────────────┐              │
│  │ nuxtApp instance #2            │              │
│  │ payload.state: {               │              │
│  │   'auth:user': {id: '456'}     │              │
│  │ }                              │              │
│  └────────────────────────────────┘              │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Each request creates a new `nuxtApp` instance with isolated state.**

---

### Client-Side (Browser)

**State is shared across all components in the browser tab:**

```typescript
// Component A
const user = useState("auth:user");
user.value = { name: "Alice" };

// Component B (same page)
const user = useState("auth:user");
console.log(user.value); // { name: 'Alice' } ✅

// Different browser tab
const user = useState("auth:user");
console.log(user.value); // undefined (new app instance)
```

**Visual representation:**

```
┌──────────────────────────────────────────────────┐
│ Browser Tab 1                                     │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌────────────────────────────────┐              │
│  │ nuxtApp instance               │              │
│  │ payload.state: {               │              │
│  │   'auth:user': {id: '123'}     │ ◄── Shared  │
│  │ }                              │     by all   │
│  │                                │     components│
│  │ Components:                    │              │
│  │  - Header (reads auth:user)    │              │
│  │  - Sidebar (reads auth:user)   │              │
│  │  - Page (reads auth:user)      │              │
│  └────────────────────────────────┘              │
│                                                   │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ Browser Tab 2 (separate instance)                │
├──────────────────────────────────────────────────┤
│  ┌────────────────────────────────┐              │
│  │ Different nuxtApp instance     │              │
│  │ payload.state: {}              │              │
│  └────────────────────────────────┘              │
└──────────────────────────────────────────────────┘
```

---

## Comparison: Global vs useState

### True Global State (DANGEROUS on Server!)

```typescript
// ❌ NEVER DO THIS!
let globalUser = null;

export default defineNuxtRouteMiddleware(async () => {
  globalUser = await $fetch("/api/user/me");
});
```

**Problem:**

```
Request 1 (Alice): globalUser = { name: 'Alice' }
Request 2 (Bob):   globalUser = { name: 'Bob' }
Request 1 reads:   globalUser → { name: 'Bob' } ❌ LEAK!
```

**Alice sees Bob's data!** This is a critical security vulnerability.

---

### useState (Safe on Server!)

```typescript
// ✅ CORRECT
export default defineNuxtRouteMiddleware(async () => {
  const user = useState("auth:user");
  user.value = await $fetch("/api/user/me");
});
```

**What happens:**

```
Request 1 (Alice): nuxtApp1.state['auth:user'] = { name: 'Alice' }
Request 2 (Bob):   nuxtApp2.state['auth:user'] = { name: 'Bob' }
Request 1 reads:   nuxtApp1.state['auth:user'] → { name: 'Alice' } ✅
```

**Each request has isolated state. No leaks!**

---

## How Nuxt Creates Isolated Instances

### Server-Side Request Handling

```typescript
// Simplified Nuxt internal flow
export async function handleServerRequest(httpRequest) {
  // 1. Create NEW nuxtApp for this request
  const nuxtApp = createNuxtApp({
    payload: {
      state: {}, // Fresh, empty state
    },
  });

  // 2. Run app with this isolated instance
  await nuxtApp.runWithContext(async () => {
    // Middleware, pages, etc. run here
    // All useState calls use THIS nuxtApp's state
  });

  // 3. Serialize state to HTML
  const html = renderToString(nuxtApp);
  return html;
}
```

**Key:** Each request gets `createNuxtApp()` called, creating isolated state.

---

### Client-Side (Browser)

```typescript
// Browser initialization
const nuxtApp = createNuxtApp();

// Read payload from HTML
const payload = JSON.parse(
  document.getElementById("__NUXT_DATA__").textContent,
);
nuxtApp.payload = payload;

// All useState calls share this ONE instance
// (until page reload creates new instance)
```

**Key:** Browser has one `nuxtApp` per page load, shared by all components.

---

## Practical Examples

### Example 1: Shared Across Components (Client)

```typescript
// components/Header.vue
const user = useState("auth:user");
user.value = { name: "Alice" };

// components/Sidebar.vue
const user = useState("auth:user");
console.log(user.value); // { name: 'Alice' } ✅

// Same state key = same reactive object
```

---

### Example 2: Isolated Between Requests (Server)

```typescript
// app/middleware/auth.global.ts
if (import.meta.server) {
  const user = useState("auth:user");
  user.value = await $fetch("/api/user/me", { headers: event.headers });
}

// Request A (Alice): useState('auth:user') = Alice's data
// Request B (Bob):   useState('auth:user') = Bob's data
// No interference!
```

---

### Example 3: NOT Shared Between Tabs

```typescript
// Browser Tab 1
const counter = useState("counter", () => 0);
counter.value++; // 1

// Browser Tab 2 (user opens new tab)
const counter = useState("counter", () => 0);
console.log(counter.value); // 0 (new app instance!)

// Each tab has its own nuxtApp instance
```

---

## Security Implications

### Why This Matters for Auth

**Bad pattern (global):**

```typescript
// ❌ DANGEROUS
let currentUser = null;

export default defineEventHandler(async (event) => {
  currentUser = await getCurrentUser(event);
  return { user: currentUser };
});

// User A's request might see User B's data!
```

**Good pattern (useState):**

```typescript
// ✅ SAFE (but useState is for Vue components, not event handlers)
export default defineNuxtRouteMiddleware(async () => {
  const user = useState("auth:user");
  user.value = await $fetch("/api/user/me");
});

// Each request has isolated state
```

**Note:** Event handlers (API routes) don't use `useState`. They use:

```typescript
export default defineEventHandler(async (event) => {
  // Each event is isolated by default
  const user = await getCurrentUser(event);
  return user;
});
```

---

## Common Misconceptions

### Misconception 1: "useState is like localStorage"

**Wrong!**

- `localStorage`: Persists across page reloads, shared by all tabs
- `useState`: Lost on reload, NOT shared between tabs

### Misconception 2: "useState is like Vuex/Pinia global store"

**Partially correct:**

- Like Vuex: Shared across components (in same instance)
- Unlike Vuex: NOT shared between requests on server

### Misconception 3: "I can use useState to share data between users"

**NO!** Each user's request gets isolated state. Use a database for sharing.

---

## When to Use What

| Need                                  | Solution                          |
| ------------------------------------- | --------------------------------- |
| **Component state** (local)           | `ref()`, `reactive()`             |
| **Page state** (shared in components) | `useState()`                      |
| **Persist across reloads**            | `localStorage`, cookies, database |
| **Share between users**               | Database                          |
| **Server-only state**                 | Database, cache (Redis)           |

---

## Key Takeaways

1. ✅ **useState is request-scoped on server**
   - Each request gets isolated state
   - No data leaks between users
   - Safe for SSR

2. ✅ **useState is app-scoped on client**
   - Shared across components
   - Lost on page reload
   - NOT shared between tabs

3. ❌ **useState is NOT global**
   - Not like `window.myVar`
   - Not persisted
   - Not shared between requests

4. ✅ **Perfect for SSR hydration**
   - Server sets → Client reads
   - Auto-serialized in payload
   - Type-safe and reactive

## In Our Auth Middleware

```typescript
// Server: Each request gets isolated user state
useState("auth:user").value = userData; // Safe!

// Client: All components share this state
const { user } = useAuth(); // useState('auth:user')

// No security issues because:
// - Server: Each request isolated
// - Client: Each browser tab isolated
// - Payload: Serialized per-request
```

This is why `useState` is the recommended pattern for SSR state in Nuxt!
