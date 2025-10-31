# provide/inject in SSR: The Full Picture

## Quick Answer

**provide/inject is:**

- ✅ Request-scoped on server (isolated per request)
- ❌ NOT automatically serialized/hydrated (unlike useState)
- ⚠️ Code re-executes on client - must provide same values
- ✅ Tree-scoped (only descendants can inject)

---

## How provide/inject Works in SSR

### Server-Side: Request Isolation

```vue
<!-- App.vue (Root) -->
<script setup>
const user = ref({ name: "Alice" });
provide("user", user);
</script>

<!-- Child.vue -->
<script setup>
const user = inject("user");
// Can access user here
</script>
```

**Request isolation:**

```
Request 1 (User Alice):
  App instance 1 created
    → Root provides { name: 'Alice' }
      → Child injects → sees 'Alice' ✅

Request 2 (User Bob) - SIMULTANEOUS:
  App instance 2 created
    → Root provides { name: 'Bob' }
      → Child injects → sees 'Bob' ✅

No leak! Different app instances.
```

**Unlike global variables, provide/inject is safe on server because each request creates a new Vue app instance.**

---

### The Critical Difference from useState

#### useState: Automatic Serialization

```typescript
// Server
useState('auth:user').value = { name: 'Alice' }

// HTML payload
<script id="__NUXT_DATA__">
{ "state": { "auth:user": { "name": "Alice" } } }
</script>

// Client reads from payload
const user = useState('auth:user') // { name: 'Alice' } ✅ Auto-hydrated!
```

#### provide/inject: Manual Re-execution

```vue
<!-- Server executes this -->
<script setup>
provide("user", { name: "Alice" });
</script>

<!-- HTML has NO serialized provide data! -->
<script id="__NUXT_DATA__">
{ "state": {} } <!-- provide/inject NOT here! -->
</script>

<!-- Client executes this AGAIN -->
<script setup>
provide("user", { name: "Alice" }); // Must re-run!
</script>
```

**Key insight:** provide/inject is **code**, not **data**. The client re-executes the provide() call during hydration.

---

## The Hydration Flow

### Step-by-Step Example

```vue
<!-- Root.vue -->
<script setup>
const count = ref(5);
provide("count", count);
</script>

<template>
  <Child />
  <!-- Renders "Count: 5" -->
</template>

<!-- Child.vue -->
<script setup>
const count = inject("count");
</script>

<template>
  <div>Count: {{ count }}</div>
</template>
```

**Server:**

```
1. Root setup() runs → count = ref(5) → provide('count', count)
2. Child setup() runs → inject('count') → gets ref with value 5
3. Render to HTML: <div>Count: 5</div>
4. Send HTML (NO count in payload!)
```

**Client:**

```
5. Receive HTML: <div>Count: 5</div>
6. Root setup() runs AGAIN → count = ref(5) → provide('count', count)
7. Child setup() runs AGAIN → inject('count') → gets ref with value 5
8. Hydrate: <div>Count: 5</div> matches ✅
```

**The code re-executes identically, so values match!**

---

## The Danger: Server-Only Data

### Problem Case

```vue
<!-- Root.vue -->
<script setup>
if (import.meta.server) {
  const event = useRequestEvent();
  provide("headers", event.headers); // Only on server!
}
</script>

<!-- Child.vue -->
<script setup>
const headers = inject("headers");
</script>

<template>
  <div>Cookie: {{ headers?.cookie }}</div>
</template>
```

**What happens:**

```
Server:
  → event.headers exists
  → provide('headers', { cookie: '...' })
  → Child renders: <div>Cookie: abc123</div>

Client:
  → useRequestEvent() returns null (no HTTP request!)
  → provide('headers', null)
  → Child renders: <div>Cookie: </div> ❌ MISMATCH!
```

**Hydration error!** Server rendered with headers, client without.

---

## The Solution: Combine with useState

```vue
<!-- Root.vue -->
<script setup>
// Server: Get headers and store in useState
if (import.meta.server) {
  const event = useRequestEvent();
  useState("request-headers").value = event.headers;
}

// Both server and client: Provide from useState
const headers = useState("request-headers");
provide("headers", headers); // Ref that hydrates!
</script>

<!-- Child.vue -->
<script setup>
const headers = inject("headers");
// Server: gets headers from event
// Client: gets headers from hydrated useState
</script>
```

**Why this works:**

```
Server:
  → useState('request-headers').value = event.headers
  → payload.state['request-headers'] = { cookie: '...' }
  → provide('headers', useState('request-headers'))
  → Child gets ref to useState

Client:
  → useState('request-headers') reads from payload
  → provide('headers', useState('request-headers'))
  → Child gets same ref to hydrated state ✅
```

**useState handles serialization, provide/inject handles tree-scoping!**

---

## Comparison: useState vs provide/inject

| Aspect                 | useState                   | provide/inject               |
| ---------------------- | -------------------------- | ---------------------------- |
| **Scope**              | App-wide (all components)  | Tree (descendants only)      |
| **Serialization**      | Automatic (in payload)     | None (code re-runs)          |
| **Isolation (server)** | Per-request                | Per-request                  |
| **Use case**           | Global state (auth, theme) | Tree-scoped config/callbacks |
| **Hydration**          | Automatic                  | Manual (via re-execution)    |

---

## When to Use What

### Use useState

```typescript
// App-wide state that needs to persist through hydration
useState("auth:user").value = userData;
useState("theme").value = "dark";
useState("locale").value = "en";

// Any component anywhere can access
const user = useState("auth:user");
```

**Use for:**

- Authentication
- Global settings
- App-wide config
- Data from server that ALL components need

---

### Use provide/inject

```vue
<!-- Layout.vue -->
<script setup>
const theme = ref("dark");
const toggleTheme = () => {
  theme.value = theme.value === "dark" ? "light" : "dark";
};

provide("theme", theme);
provide("toggleTheme", toggleTheme);
</script>

<!-- Nested child (anywhere in tree) -->
<script setup>
const theme = inject("theme");
const toggleTheme = inject("toggleTheme");
</script>
```

**Use for:**

- Tree-scoped configuration
- Callbacks/methods to children
- Avoiding prop drilling
- Layout-specific state

---

### Use Both Together

```vue
<!-- Root.vue -->
<script setup>
// Global state (hydrates)
const user = useState("auth:user");

// Provide to tree (with hydrated data)
provide("user", user);
provide(
  "isAdmin",
  computed(() => user.value?.role === "admin"),
);
</script>

<!-- Child.vue -->
<script setup>
// Inject from parent (tree-scoped)
const user = inject("user"); // Gets useState ref
const isAdmin = inject("isAdmin"); // Gets computed
</script>
```

**Why combine:**

- useState: Serialization/hydration
- provide/inject: Tree scoping
- Best of both worlds!

---

## Real-World Patterns

### Pattern 1: Layout-Specific State

```vue
<!-- layouts/admin.vue -->
<script setup>
const sidebarOpen = ref(true);
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

provide("sidebarOpen", sidebarOpen);
provide("toggleSidebar", toggleSidebar);
</script>

<!-- pages/admin/users.vue -->
<script setup>
const sidebarOpen = inject("sidebarOpen");
const toggleSidebar = inject("toggleSidebar");
</script>
```

**Works because:**

- Initial state (`ref(true)`) is same on server and client
- No server-only data
- Code re-executes identically

---

### Pattern 2: Computed from Global State

```vue
<!-- App.vue -->
<script setup>
const user = useState("auth:user"); // Global, hydrates

// Provide computed values to tree
provide(
  "isAdmin",
  computed(() => user.value?.role === "admin"),
);
provide(
  "canEdit",
  computed(() => ["admin", "editor"].includes(user.value?.role)),
);
</script>

<!-- Deep child -->
<script setup>
const isAdmin = inject("isAdmin"); // Reactive computed!
</script>
```

**Benefits:**

- Global data via useState
- Tree-scoped computed via provide
- No prop drilling

---

### Pattern 3: Server Data with Provide

```vue
<!-- Root.vue -->
<script setup>
// Server: Fetch data
if (import.meta.server) {
  const event = useRequestEvent();
  const userData = await $fetch("/api/user/me", { headers: event.headers });
  useState("auth:user").value = userData;
}

// Both: Provide from useState
const user = useState("auth:user");
provide("currentUser", readonly(user)); // Provide read-only version!
</script>

<!-- Child -->
<script setup>
const currentUser = inject("currentUser"); // Read-only ref
</script>
```

**Why readonly?**

- Children can read
- Only root can modify
- Clear ownership

---

## Edge Cases

### Edge Case 1: Async in provide

```vue
<!-- ❌ WRONG -->
<script setup>
const data = await $fetch("/api/data");
provide("data", data);
// Client re-fetches! Might differ from server!
</script>

<!-- ✅ RIGHT -->
<script setup>
const { data } = await useAsyncData("data", () => $fetch("/api/data"));
provide("data", data); // useAsyncData handles hydration!
</script>
```

**useAsyncData ensures server data is serialized and client doesn't re-fetch.**

---

### Edge Case 2: Different Provide on Server/Client

```vue
<!-- ⚠️ DANGEROUS -->
<script setup>
if (import.meta.server) {
  provide("platform", "server");
} else {
  provide("platform", "client");
}
</script>

<!-- Child -->
<script setup>
const platform = inject("platform");
</script>

<template>
  <div>Platform: {{ platform }}</div>
</template>
```

**Result:**

```
Server renders: <div>Platform: server</div>
Client hydrates: <div>Platform: client</div> ❌ MISMATCH!
```

**Never provide different values on server vs client!**

---

### Edge Case 3: provide in Middleware

```typescript
// ❌ CAN'T DO THIS
export default defineNuxtRouteMiddleware(() => {
  provide("something", value); // provide() not available in middleware!
});

// ✅ USE useState INSTEAD
export default defineNuxtRouteMiddleware(() => {
  useState("something").value = value;
});
```

**provide/inject only works in component setup, not middleware.**

---

## The provide/inject + SSR Mental Model

### What Gets Serialized

```vue
<script setup>
// ✅ Serialized (in payload)
useState("user").value = { name: "Alice" };

// ❌ NOT serialized (code only)
provide("user", { name: "Alice" });

// ✅ Serialized (useAsyncData uses useState internally)
const { data } = await useAsyncData("key", fetcher);

// ❌ NOT serialized
const data = await $fetch("/api/data");
provide("data", data);
</script>
```

### Request Isolation

```
Both useState AND provide/inject are request-isolated on server:

Request A:
  App instance A
    → useState('user') = Alice
    → provide('theme') = 'dark'

Request B:
  App instance B
    → useState('user') = Bob
    → provide('theme') = 'light'

No leaks! ✅
```

### Hydration Strategy

```
useState:
  Server sets → Payload serializes → Client reads
  (One-way: Server → Client)

provide/inject:
  Server executes → Client re-executes
  (Must produce same result both times)
```

---

## Best Practices

### 1. Use useState for Data, provide for Structure

```vue
<!-- ✅ GOOD -->
<script setup>
// Data from server (hydrates)
const user = useState("auth:user");

// Tree structure (re-executes)
provide("user", user);
provide("logout", () => {
  user.value = null;
});
</script>
```

### 2. Provide Reactive Refs, Not Values

```vue
<!-- ❌ BAD -->
provide('userName', user.value.name) // String, not reactive

<!-- ✅ GOOD -->
provide('user', user) // Ref, reactive provide('userName', computed(() =>
user.value?.name)) // Computed, reactive
```

### 3. Use readonly for Read-Only Data

```vue
<script setup>
const internalState = ref(0);
provide("state", readonly(internalState)); // Children can't modify!
</script>
```

### 4. Document Injection Keys

```typescript
// types/injection-keys.ts
import type { InjectionKey, Ref } from "vue";
import type { IAuthUser } from "#shared/types/IAuthUser";

export const CurrentUserKey: InjectionKey<Ref<IAuthUser | null>> =
  Symbol("currentUser");
export const ThemeKey: InjectionKey<Ref<"light" | "dark">> = Symbol("theme");

// Usage
provide(CurrentUserKey, user);
const user = inject(CurrentUserKey); // Type-safe!
```

---

## Your Auth Use Case

### Current Pattern (useState only)

```typescript
// Middleware
useState("auth:user").value = userData;

// Any component
const user = useState("auth:user");
```

**This is fine for app-wide auth!**

### Alternative (useState + provide)

```vue
<!-- App.vue -->
<script setup>
// Global state (hydrates)
const user = useState("auth:user");

// Provide to tree (with utilities)
provide("auth", {
  user: readonly(user),
  isAdmin: computed(() => user.value?.role === "admin"),
  isPending: computed(() => user.value?.role === "pending"),
});
</script>

<!-- Components -->
<script setup>
const auth = inject("auth");
// auth.user, auth.isAdmin, etc.
</script>
```

**Benefits:**

- Centralized auth interface
- Type-safe injection
- Read-only to children

**But probably overkill for simple auth!** useState alone is fine.

---

## Summary

### Key Insights

1. ✅ **provide/inject is request-scoped on server**
   - Each request = new app instance
   - Safe from data leaks

2. ❌ **provide/inject does NOT auto-serialize**
   - Code re-executes on client
   - Must produce same values

3. ✅ **Combine with useState for server data**
   - useState handles serialization
   - provide/inject handles tree scoping

4. ✅ **Use for tree-scoped state, not global**
   - useState: App-wide (auth, theme)
   - provide/inject: Layout/tree-specific (callbacks, config)

### Decision Matrix

| Need                     | Solution                                     |
| ------------------------ | -------------------------------------------- |
| Global state from server | `useState`                                   |
| Tree-scoped callbacks    | `provide/inject`                             |
| Both                     | `useState` + `provide(key, useState('key'))` |
| Component-specific       | Props                                        |
| UI state                 | `ref()`                                      |

### The Pattern

```vue
<!-- Root: Get server data -->
if (import.meta.server) { useState('data').value = await fetchData(event) }

<!-- Root: Provide to tree -->
provide('data', useState('data'))

<!-- Child: Inject from tree -->
const data = inject('data')
```

**useState for hydration, provide/inject for scoping - they complement each other!**
