# Component-Scoped Hydration in Nuxt 4

## The Problem

**You want state that:**

- ✅ Hydrates from server → client (survives SSR)
- ✅ Is scoped to component instance (not shared)
- ❌ `ref()` doesn't hydrate
- ❌ `useState()` is app-scoped (shared everywhere)

**Real scenario:**

```vue
<!-- components/Counter.vue (used multiple times on page) -->
<template>
  <div>
    Count: {{ count }}
    <button @click="count++">+</button>
  </div>
</template>

<script setup>
// ❌ ref() - doesn't hydrate, client starts at 0
const count = ref(0);

// ❌ useState('count') - all counters share same value!
const count = useState("count", () => 0);

// ❓ What do we use?
</script>
```

---

## Solution 1: useState with Unique Instance Key

**Use component instance ID to create unique keys:**

```vue
<script setup>
import { getCurrentInstance } from "vue";

// Generate unique key per component instance
const instance = getCurrentInstance();
const instanceId = instance?.uid || Math.random();

// Each component gets its own state
const count = useState(`counter-${instanceId}`, () => 0);
</script>
```

**How it works:**

```
Server renders:
  <Counter /> → useState('counter-1') = 5
  <Counter /> → useState('counter-2') = 3

Payload:
  state: {
    'counter-1': 5,
    'counter-2': 3
  }

Client hydrates:
  <Counter /> → useState('counter-1') = 5 ✅
  <Counter /> → useState('counter-2') = 3 ✅
```

**Problem:** Vue instance UIDs might not be stable between server/client!

---

## Solution 2: Nuxt's useId() (Recommended)

**Nuxt 4 has `useId()` for stable SSR-safe IDs:**

```vue
<script setup>
// Generates same ID on server and client
const id = useId();

// Component-scoped state that hydrates
const count = useState(`counter-${id}`, () => 0);
</script>
```

**Why this works:**

- `useId()` generates stable IDs consistent between server/client
- Each component instance gets unique ID
- `useState` with unique key = component-scoped + hydrated

---

## Solution 3: Props from Parent (Simplest)

**If data comes from parent, use props:**

```vue
<!-- Parent.vue -->
<template>
  <Counter :initial-count="5" />
  <Counter :initial-count="3" />
</template>

<!-- Counter.vue -->
<script setup>
const props = defineProps<{ initialCount: number }>()
const count = ref(props.initialCount) // Hydrates via props!
</script>
```

**Why this works:**

- Server renders with `initialCount` prop
- Client receives same prop during hydration
- `ref()` initialized with prop value = matches server

**This is the most common pattern!**

---

## Solution 4: useAsyncData with Component Key

**For async data that's component-scoped:**

```vue
<script setup>
const id = useId();

const { data: userData } = await useAsyncData(`user-${id}`, async () => {
  return $fetch(`/api/user/${userId}`);
});
</script>
```

**Benefits:**

- Component-scoped (unique key)
- Auto-hydrates
- Handles loading states
- Prevents duplicate fetches

---

## Solution 5: Accept No Hydration (Common)

**Most component state doesn't need hydration:**

```vue
<script setup>
// ✅ This is fine!
const isMenuOpen = ref(false);
const selectedTab = ref(0);

// Server: renders closed
// Client: starts closed (matches)
// No hydration mismatch!
</script>
```

**When you DON'T need hydration:**

- UI state (open/closed, selected)
- Temporary values (form drafts)
- Client-only features (animations)

**Key:** Initial value on client matches server render.

---

## Real-World Examples

### Example 1: Multiple Counters (Unique State)

```vue
<!-- components/StatCard.vue (used 3 times on page) -->
<script setup>
const props = defineProps<{
  label: string
  value: number
}>()

// Component-scoped, hydrated via props
const count = ref(props.value)
</script>

<template>
  <div>
    {{ label }}: {{ count }}
    <button @click="count++">+</button>
  </div>
</template>
```

**Usage:**

```vue
<StatCard label="Users" :value="100" />
<StatCard label="Posts" :value="50" />
<StatCard label="Comments" :value="200" />
```

Each has independent state, hydrates correctly!

---

### Example 2: Dynamic Components with Server Data

```vue
<!-- components/UserCard.vue -->
<script setup>
const props = defineProps<{ userId: string }>()
const id = useId()

// Component-scoped async data
const { data: user } = await useAsyncData(`user-card-${id}`, () =>
  $fetch(`/api/users/${props.userId}`)
)
</script>
```

**Multiple instances:**

```vue
<UserCard user-id="1" />
<UserCard user-id="2" />
<UserCard user-id="3" />
```

Each fetches independently, state is scoped!

---

### Example 3: Local UI State (No Hydration Needed)

```vue
<!-- components/Accordion.vue -->
<script setup>
// Starts closed on both server and client
const isOpen = ref(false);
</script>

<template>
  <div>
    <button @click="isOpen = !isOpen">Toggle</button>
    <div v-if="isOpen">Content</div>
  </div>
</template>
```

No hydration needed - client starts with same value as server!

---

## Decision Tree

```
Do you need component-scoped hydrated state?
│
├─ YES → Is it async data?
│   │
│   ├─ YES → Use useAsyncData(`${useId()}`, fetcher)
│   │
│   └─ NO → Does data come from parent?
│       │
│       ├─ YES → Use props + ref(props.value)
│       │
│       └─ NO → Use useState(`${useId()}`)
│
└─ NO → Is it UI state?
    │
    ├─ YES → Use ref() (starts same on server/client)
    │
    └─ NO → Do all components share it?
        │
        ├─ YES → Use useState('shared-key')
        │
        └─ NO → Reconsider if you really need it
```

---

## Common Patterns Summary

| Use Case                  | Solution                           | Example                    |
| ------------------------- | ---------------------------------- | -------------------------- |
| **App-wide auth**         | `useState('auth:user')`            | User data everywhere       |
| **Component prop**        | `ref(props.value)`                 | Counter with initial value |
| **Async per instance**    | `useAsyncData(\`key-${useId()}\`)` | User cards                 |
| **UI state**              | `ref(false)`                       | Menu open/closed           |
| **Unique instance state** | `useState(\`key-${useId()}\`)`     | Form drafts                |

---

## Best Practice: Most State Doesn't Need Hydration

**Ask yourself:**

1. Does server render this value differently than client initial?
2. Does this data come from async source?
3. Is it truly component-scoped or should it be shared?

**90% of component state:**

```vue
// ✅ This is fine! const isOpen = ref(false) const selectedIndex = ref(0) const
searchQuery = ref('')
```

**No hydration needed** if initial value matches server render!

---

## Your Auth Case

```typescript
// app/middleware/auth.global.ts

// ✅ CORRECT: App-wide shared state
useState("auth:user").value = userData;

// All components see it:
// - Header shows user name
// - Sidebar shows user role
// - Profile shows user data
// They SHOULD share the same user!
```

**If you had per-component user data:**

```vue
<!-- components/UserProfile.vue -->
<script setup>
const props = defineProps<{ userId: string }>()
const id = useId()

// Component-scoped, hydrated
const { data: userProfile } = await useAsyncData(`profile-${id}`, () =>
  $fetch(`/api/users/${props.userId}`)
)
</script>
```

---

## Key Takeaway

**Component-scoped hydration is rare!** Most cases are:

1. **App-wide** → `useState('key')` ✅
2. **From props** → `ref(props.value)` ✅
3. **UI state** → `ref(initialValue)` ✅

**When you truly need it:**

- `useAsyncData(\`key-${useId()}\`)` for async data
- `useState(\`key-${useId()}\`)` for sync state
- Props are usually the better solution

The fact that `useState` is app-scoped is usually what you want!
