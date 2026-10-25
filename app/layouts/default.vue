<template>
    <div class="site-frame">
        <a href="#main-content" class="skip-link">Skip to content</a>
        <header class="site-header">
            <button
                class="quiet menu-button"
                aria-label="Toggle root index"
                :aria-expanded="sidebar"
                @click="sidebar = !sidebar"
            >
                ☰
            </button>
            <NuxtLink to="/" class="wordmark">
                <span class="wordmark-symbol">ܛ</span>
                <span>
                    Turoyo
                    <span class="muted">Verb Glossary</span>
                </span>
            </NuxtLink>
            <nav class="top-nav" aria-label="Main navigation">
                <NuxtLink to="/texts">Texts</NuxtLink>
                <NuxtLink to="/review">Review</NuxtLink>
                <NuxtLink to="/research">Research</NuxtLink>
                <NuxtLink to="/about">About</NuxtLink>
                <NuxtLink v-if="isAdmin" to="/admin">Admin</NuxtLink>
            </nav>
            <div class="header-actions">
                <button
                    class="quiet search-trigger"
                    aria-label="Open search"
                    @click="searchOpen = true"
                >
                    Search
                    <kbd>⌘ K</kbd>
                </button>
                <button class="quiet" aria-label="Toggle dark mode" @click="toggleColor">
                    ◐
                </button>
                <button class="quiet signout" aria-label="Sign out" @click="logout">
                    Sign out
                </button>
            </div>
        </header>
        <aside
            v-if="isApproved"
            class="sidebar"
            :class="{ 'sidebar-open': sidebar }"
            aria-label="Root index"
            :inert="mobile && !sidebar"
        >
            <RootIndex @navigate="sidebar = false"/>
        </aside>
        <button
            v-if="sidebar"
            class="sidebar-backdrop"
            aria-label="Close root index"
            @click="sidebar = false"
        ></button>
        <main id="main-content" class="site-main" :class="{ 'without-sidebar': !isApproved }">
            <div v-if="fixture" class="fixture-banner">
                Development fixture · illustrative data · reviews stay in memory
            </div>
            <PendingUserBanner/>
            <slot v-if="!isPending"></slot>
        </main>
        <UModal
            v-model:open="searchOpen"
            title="Search the glossary and corpus"
            description="Roots, forms, meanings and passages. Use regular expressions for full-text searches."
        >
            <template #body>
                <SearchExplorer autofocus @navigate="searchOpen = false"/>
            </template>
        </UModal>
        <EvidencePanel v-if="selected"/>
    </div>
</template>

<script setup lang="ts">
import { useMediaQuery } from '@vueuse/core'

const {
    isAdmin,
    isPending,
    isApproved,
    signOut,
} = useAuth()
const colorMode = useColorMode()
const searchOpen = useState('search-open', () => false)
const sidebar = ref(false)
const mobile = useMediaQuery('(max-width: 780px)')
const { selected } = useEvidence()
const fixture = import.meta.dev && useRuntimeConfig().public.siteFixture
async function logout() {
    await signOut()
    await navigateTo('/login')
}
function toggleColor() {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
defineShortcuts({
    escape: () => {
        sidebar.value = false
        selected.value = null
    },
    meta_k: () => {
        searchOpen.value = !searchOpen.value
    },
    ctrl_k: () => {
        searchOpen.value = !searchOpen.value
    },
})
</script>

<style scoped>
.site-header {
    height: 68px;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 0 1.6rem;
    border-bottom: 1px solid var(--rule);
    background: var(--paper);
    position: sticky;
    top: 0;
    z-index: 30;
}
.wordmark {
    color: var(--ink);
    text-decoration: none;
    font-family: var(--font-serif);
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    white-space: nowrap;
}
.wordmark-symbol {
    border-right: 1px solid var(--rule);
    padding-right: 0.7rem;
    font-size: 1.7rem;
}
.top-nav {
    display: flex;
    gap: 1.3rem;
    font-size: 0.78rem;
    margin-left: auto;
}
.top-nav a {
    color: var(--muted);
    text-decoration: none;
}
.top-nav .router-link-active {
    color: var(--accent);
}
.header-actions {
    display: flex;
    gap: 0.4rem;
}
kbd {
    font-size: 0.65rem;
    margin-left: 1rem;
    color: var(--muted);
}
.sidebar {
    position: fixed;
    top: 68px;
    bottom: 0;
    left: 0;
    width: 238px;
    border-right: 1px solid var(--rule);
    background: var(--panel);
    z-index: 25;
}
.site-main {
    margin-left: 238px;
    padding: 1.5rem clamp(1.3rem, 4vw, 4rem) 5rem;
    max-width: 1500px;
}
.without-sidebar {
    margin-left: auto;
    margin-right: auto;
}
.fixture-banner {
    font-size: 0.7rem;
    padding: 0.35rem 0.6rem;
    background: var(--panel);
    border: 1px dashed var(--rule);
    color: var(--muted);
    margin-bottom: 1rem;
}
.menu-button {
    display: none;
}
.skip-link {
    position: fixed;
    top: -100px;
    padding: 0.6rem;
    z-index: 100;
    background: var(--paper);
}
.skip-link:focus {
    top: 0;
}
.sidebar-backdrop {
    display: none;
}
@media (max-width: 1100px) {
    .signout {
        display: none;
    }
    .site-header {
        gap: 0.8rem;
        padding: 0 1rem;
    }
    .top-nav {
        gap: 0.8rem;
    }
    .wordmark {
        font-size: 1.05rem;
    }
}
@media (max-width: 780px) {
    .site-header {
        flex-wrap: wrap;
        height: 100px;
        gap: 0.5rem;
        padding: 0.5rem 0.8rem;
    }
    .menu-button {
        display: block;
    }
    .wordmark {
        flex: 1;
        font-size: 1rem;
    }
    .wordmark-symbol {
        display: none;
    }
    .top-nav {
        order: 5;
        width: 100%;
        justify-content: center;
        gap: 1.4rem;
    }
    .search-trigger {
        font-size: 0;
    }
    kbd {
        font-size: 0.7rem;
        margin: 0;
    }
    .sidebar {
        top: 100px;
        transform: translateX(-100%);
        width: 260px;
        transition: transform 0.15s;
    }
    .sidebar-open {
        transform: translateX(0);
    }
    .sidebar-backdrop {
        display: block;
        position: fixed;
        inset: 100px 0 0;
        background: #0005;
        z-index: 20;
    }
    .site-main {
        margin-left: 0;
        padding-top: 1rem;
    }
}
</style>
