# Why Nuxt Doesn't Have Component-Scoped Hydration

## The Insight

**You observed:** `useState('key-${useId()}')` is a hack, not a safe solution.

**You're right.** This is an architectural decision, not an oversight.

---

## Why useState + Unique Key is UNSAFE

### Problem 1: Instance Order Not Guaranteed

```vue
<!-- Server render -->
<div>
  <Counter v-if="showA" /> <!-- useId() = "uid-1", state['counter-uid-1'] = 5 -->
  <Counter v-if="showB" /> <!-- useId() = "uid-2", state['counter-uid-2'] = 3 -->
</div>

<!-- Client hydration (conditions evaluated differently) -->
<div>
  <Counter v-if="showB" /> <!-- useId() = "uid-1" ❌ gets state = 5 (wrong!) -->
  <Counter v-if="showA" /> <!-- useId() = "uid-2" ❌ gets state = 3 (wrong!) -->
</div>
```

**Problem:** `useId()` generates IDs based on render order, not component identity.

---

### Problem 2: Dynamic Lists

```vue
<!-- Server -->
<Counter v-for="item in [1, 2, 3]" :key="item" />
<!-- IDs: uid-1, uid-2, uid-3 -->

<!-- Client (items reordered) -->
<Counter v-for="item in [3, 2, 1]" :key="item" />
<!-- IDs: uid-1, uid-2, uid-3 (same order!)
     But items are different! -->
```

**`useId()` doesn't respect `v-for` keys - it only counts render order!**

---

### Problem 3: Conditional Rendering

```vue
<!-- Server renders 3 instances -->
<Counter v-if="true" />
<!-- uid-1 -->
<Counter v-if="true" />
<!-- uid-2 -->
<Counter v-if="true" />
<!-- uid-3 -->

<!-- Client renders 2 instances -->
<Counter v-if="true" />
<!-- uid-1 ✓ -->
<Counter v-if="false" />
<!-- skipped -->
<Counter v-if="true" />
<!-- uid-2 ❌ gets uid-3's state! -->
```

**Hydration mismatch if conditions differ!**

---

## Nuxt's Architectural Position

### The Official Answer: **There is NO component-scoped hydration primitive**

This is **intentional**, not a missing feature.

---

## Why This is an Architectural Decision

### Philosophy 1: Hydration is for App State, Not Component State

**Nuxt's view:**

- `useState` = **Page-level state** (user, theme, config)
- Component state = **Derived from props** or **recreated client-side**

**Rationale:**

```
Server: Fetch data → Pass to components via props
Client: Receive same props → Components recreate local state

No component-scoped serialization needed!
```

---

### Philosophy 2: Props are the Answer

**The "official" pattern:**

```vue
<!-- ❌ DON'T: Component fetches its own data -->
<script setup>
const id = useId();
const { data } = await useAsyncData(`key-${id}`, fetcher);
</script>

<!-- ✅ DO: Parent fetches, passes props -->
<script setup>
const props = defineProps<{ data: User }>()
const localState = ref(props.data) // Component-scoped, auto-hydrates via props!
</script>
```

**Why props win:**

1. ✅ Type-safe
2. ✅ Explicit data flow
3. ✅ Naturally ordered (follows component tree)
4. ✅ Hydrates automatically (part of VDOM)
5. ✅ No unique key hacks needed

---

### Philosophy 3: Minimize Hydration Payload

**Component-scoped hydration would bloat the payload:**

```html
<!-- Bad: 100 components = 100 state entries -->
<script id="__NUXT_DATA__">
  {
    "state": {
      "counter-uid-1": 0,
      "counter-uid-2": 1,
      "counter-uid-3": 2,
      ... (97 more)
    }
  }
</script>

<!-- Good: Parent fetches once -->
<script id="__NUXT_DATA__">
  {
    "state": {
      "counters-data": [0, 1, 2, ...] // Single array
    }
  }
</script>
```

**Nuxt nudges you toward centralized data fetching, not distributed component fetching.**

---

## The Real Patterns

### Pattern 1: App-Wide Shared State

```typescript
// ✅ Middleware sets app-wide state
useState("auth:user").value = userData;

// All components read it
const { user } = useAuth();
```

**Use case:** User auth, theme, locale

---

### Pattern 2: Parent Fetches, Children Consume

```vue
<!-- Parent.vue -->
<script setup>
// Parent owns the data fetching
const { data: users } = await useAsyncData("users", () => $fetch("/api/users"));
</script>

<template>
  <!-- Pass to children via props -->
  <UserCard v-for="user in users" :key="user.id" :user="user" />
</template>

<!-- UserCard.vue -->
<script setup>
const props = defineProps<{ user: User }>()

// Component-scoped state derived from props
const isExpanded = ref(false)
const localCopy = ref(props.user) // Hydrates via props!
</script>
```

**Why this works:**

- Server fetches → renders with props → client receives same props
- No unique keys needed
- Type-safe
- Clear data ownership

---

### Pattern 3: Component State Doesn't Need Hydration

```vue
<script setup>
// ✅ UI state - starts same on server/client
const isOpen = ref(false);
const selectedTab = ref(0);
const searchQuery = ref("");
</script>
```

**Most component state is UI state that doesn't need to survive SSR!**

---

## What About useAsyncData per Component?

```vue
<!-- Multiple instances -->
<UserProfile user-id="1" />
<UserProfile user-id="2" />

<!-- UserProfile.vue -->
<script setup>
const props = defineProps<{ userId: string }>()

// This LOOKS component-scoped...
const { data: user } = await useAsyncData('user-' + props.userId, () =>
  $fetch(`/api/users/${props.userId}`)
)
</script>
```

**Reality check:** `useAsyncData` uses a **GLOBAL cache**, not component-scoped state!

```javascript
// Nuxt's internal state
{
  'user-1': { name: 'Alice' },
  'user-2': { name: 'Bob' },
  'user-3': { name: 'Charlie' }
}
```

**It's still app-level state, just keyed by a component prop!**

---

## Why No Native Component-Scoped Hydration?

### Reason 1: Props Already Solve It

If you need component-scoped data from server:

```vue
<!-- Parent fetches -->
const data = await $fetch('/api/data')

<!-- Passes to child -->
<Child :data="data" />

<!-- Child uses it -->
const props = defineProps<{ data: Data }>() const local = ref(props.data) // ✅
Hydrates!
```

**No new primitive needed.**

---

### Reason 2: Encourages Anti-Patterns

**Component-scoped hydration encourages:**

- Components fetching their own data (hard to coordinate)
- Waterfalls (parent renders → child fetches → grandchild fetches)
- Duplicate fetches across instances

**Props-based approach enforces:**

- Parent fetches once
- Children receive data
- Clear data ownership

---

### Reason 3: Technical Complexity

**Challenges of true component-scoped hydration:**

1. **Instance identity:** How to match server instance to client instance?
   - React uses tree position (fragile)
   - Vue uses keys (but only in v-for)
   - No universal solution

2. **Partial hydration:** What if component doesn't render client-side?
   - Wasted payload bytes

3. **Ordering:** Dynamic lists, conditional rendering, async components

**Nuxt avoids this complexity by saying: "Use props."**

---

### Reason 4: Performance

**Payload size matters:**

```
100 components with useState('key-${uid}'):
  → 100 state entries in payload
  → Harder to compress
  → More parsing

1 parent with useState('data'):
  → 1 state entry
  → Better compression
  → Faster parsing
```

**Centralized state is more efficient.**

---

## The Architectural Truth

**Nuxt's design:**

```
┌─────────────────────────────────────┐
│ useState('key')                     │
│ - App-wide shared state             │
│ - Auth, theme, config               │
│ - Survives SSR via hydration        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Props + ref(props.value)            │
│ - Component-scoped state            │
│ - Data flows parent → child         │
│ - Hydrates via VDOM, not payload    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ref(initialValue)                   │
│ - Component-local UI state          │
│ - Doesn't need to survive SSR       │
│ - Recreated on client               │
└─────────────────────────────────────┘
```

**There is NO fourth category** - component-scoped hydrated state without props.

---

## When You Think You Need It

**Scenario:** "Each component instance needs different server data"

**Wrong approach:**

```vue
<!-- Child fetches its own data -->
<script setup>
const props = defineProps<{ id: string }>()
const data = await useAsyncData('data-' + props.id, fetcher)
</script>
```

**Right approach:**

```vue
<!-- Parent fetches all data -->
<script setup>
const { data: items } = await useAsyncData("items", () => $fetch("/api/items"));
</script>

<template>
  <Child v-for="item in items" :key="item.id" :data="item" />
</template>
```

**Benefits:**

- Single fetch (parallel, not waterfall)
- Clear ownership (parent manages data)
- Type-safe props
- No unique key hacks

---

## Your Original Question Answered

> "ref isn't fine, but then what?"

**Nuxt's answer: Props.**

```vue
<!-- If data comes from server, it flows via props -->
<Component :server-data="data" />

<!-- Component receives and uses it -->
const props = defineProps<{ serverData: Data }>() const local =
ref(props.serverData) // ✅ Component-scoped, hydrates via props
```

**If you can't use props, you're probably structuring your components wrong.**

---

## Key Insights

1. ✅ **useState + unique key is UNSAFE**
   - Instance order not guaranteed
   - Breaks with conditional rendering
   - Hydration mismatches

2. ✅ **Nuxt deliberately has NO component-scoped hydration**
   - Architectural decision, not missing feature
   - Props are the official answer

3. ✅ **Props naturally hydrate**
   - Part of VDOM tree
   - No special mechanism needed
   - Type-safe and explicit

4. ✅ **Most component state doesn't need hydration**
   - UI state can be recreated
   - `ref()` works fine if initial matches

5. ✅ **Component-scoped hydration would be complex and dangerous**
   - Instance matching is hard
   - Encourages anti-patterns
   - Bloats payload

---

## The Bottom Line

**You were right to question the unique key pattern - it's not safe.**

**Nuxt's architectural stance:**

- ✅ App-level state: `useState('key')`
- ✅ Component state from server: **Props**
- ✅ Component UI state: `ref()`
- ❌ Component-scoped hydration without props: **Not supported (by design)**

**This forces you to think about data flow, which is a feature, not a bug.**

If you're fighting against this, you're probably trying to make components too autonomous. Nuxt is nudging you toward:

- Parent owns data fetching
- Children receive via props
- Clear, explicit data flow

**This is the Vue way, and Nuxt reinforces it.**
