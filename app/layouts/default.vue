<template>
    <div>
        <a href="#main-content" class="skip-link">Skip to content</a>
        <header class="site-header">
            <NuxtLink to="/" class="wordmark">Turoyo Verb Glossary</NuxtLink>
            <nav class="site-nav" aria-label="Main">
                <NuxtLink
                    v-for="link in links"
                    :key="link.to"
                    :to="link.to"
                    :class="{ active: section === link.to }"
                >{{ link.label }}</NuxtLink>
            </nav>
            <form
                v-if="user && section !== '/glossary'"
                class="site-search"
                role="search"
                @submit.prevent="search"
            >
                <label for="site-search" class="sr-only">Search verbs and texts</label>
                <input
                    id="site-search"
                    v-model="query"
                    type="search"
                    placeholder="Search verbs and texts"
                    autocomplete="off"
                />
            </form>
            <div class="site-tools">
                <button type="button" class="btn-link" @click="toggleColor">
                    {{ colorLabel }}
                </button>
                <button
                    v-if="user"
                    type="button"
                    class="btn-link"
                    @click="logout"
                >
                    Sign out
                </button>
            </div>
        </header>
        <main id="main-content" class="site-main" tabindex="-1">
            <PendingUserBanner/>
            <slot v-if="!isPending"></slot>
        </main>
    </div>
</template>

<script setup lang="ts">
import { useMounted } from '@vueuse/core'

const {
    isAdmin,
    isPending,
    user,
    signOut,
} = useAuth()
const colorMode = useColorMode()
const mounted = useMounted()
const route = useRoute()
const query = ref('')
const links = computed(() => [
    {
        to: '/review',
        label: 'Review',
    },
    {
        to: '/glossary',
        label: 'Glossary',
    },
    {
        to: '/texts',
        label: 'Texts',
    },
    {
        to: '/help',
        label: 'Help',
    },
    ...(isAdmin.value
        ? [{
                to: '/admin',
                label: 'Admin',
            }]
        : []),
])
// Entries belong to the glossary and readers to the texts.
const section = computed(() => {
    const path = route.path
    if (path.startsWith('/entry/')) return '/glossary'
    return links.value.find(link => path === link.to || path.startsWith(`${link.to}/`))?.to || ''
})
// The colour mode is only known in the browser, so the label waits for mounting.
const colorLabel = computed(() => (!mounted.value ? 'Theme' : colorMode.value === 'dark' ? 'Light theme' : 'Dark theme'))
function toggleColor() {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
function search() {
    const q = query.value.trim()
    query.value = ''
    return navigateTo({
        path: '/glossary',
        query: q ? { q } : {},
    })
}
async function logout() {
    await signOut()
    await navigateTo('/login')
}
</script>

<style scoped>
.site-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 1.5rem;
  padding: 0.4rem 1.5rem;
  border-bottom: 1px solid var(--rule);
}
.wordmark {
  font-family: var(--font-serif);
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--ink);
  text-decoration: none;
}
.site-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0 1.1rem;
}
.site-nav a {
  padding: 0.3rem 0;
  border-bottom: 2px solid transparent;
  color: var(--ink);
  text-decoration: none;
}
.site-nav a:hover {
  color: var(--accent);
}
.site-nav a.active {
  border-bottom-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}
.site-search {
  margin-left: auto;
}
.site-search input {
  width: 18rem;
}
.site-tools {
  display: flex;
  gap: 0.75rem;
}
.site-nav + .site-tools {
  margin-left: auto;
}
.site-main {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 1.5rem 3rem;
  overflow-wrap: break-word;
}
.site-main:focus {
  outline: none;
}
.skip-link {
  position: fixed;
  top: -100px;
  left: 0.5rem;
  z-index: 100;
  padding: 0.5rem;
  background: var(--bg);
}
.skip-link:focus {
  top: 0.5rem;
}
@media (max-width: 760px) {
  .site-header {
    padding: 0.35rem 0.75rem;
  }
  .site-search {
    display: none;
  }
  .site-tools {
    margin-left: auto;
  }
  .site-nav {
    order: 3;
    width: 100%;
  }
  .site-main {
    padding: 0.75rem 0.75rem 3rem;
  }
}
</style>
