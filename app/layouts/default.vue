<template>
    <div class="site-frame">
        <a href="#main-content" class="skip-link">Skip to content</a>
        <header class="site-header">
            <NuxtLink to="/" class="wordmark">Turoyo Verb Glossary</NuxtLink>
            <nav class="top-nav" aria-label="Main navigation">
                <NuxtLink v-for="link in links" :key="link.to" :to="link.to">{{
                    link.label
                }}</NuxtLink>
            </nav>
            <button
                class="quiet menu-toggle"
                :aria-expanded="menu"
                aria-controls="site-menu"
                @click="menu = !menu"
            >
                {{ menu ? "Close" : "Menu" }}
            </button>
        </header>
        <nav
            v-if="menu"
            id="site-menu"
            class="site-menu"
            aria-label="Site menu"
        >
            <NuxtLink
                v-for="link in links"
                :key="link.to"
                :to="link.to"
                @click="menu = false"
            >{{ link.label }}</NuxtLink>
            <NuxtLink
                v-if="isAdmin"
                to="/admin"
                @click="menu = false"
            >Admin</NuxtLink>
            <button class="text-button" @click="toggleColor">
                {{
                    colorMode.value === "dark" ? "Use light colours" : "Use dark colours"
                }}
            </button>
            <button v-if="user" class="text-button" @click="logout">
                Sign out
            </button>
        </nav>
        <main id="main-content" class="site-main">
            <PendingUserBanner/>
            <slot v-if="!isPending"></slot>
        </main>
        <footer class="site-footer">
            <NuxtLink to="/help">Help with the glossary</NuxtLink>
        </footer>
        <EvidencePanel v-if="selected"/>
    </div>
</template>

<script setup lang="ts">
const {
    isAdmin,
    isPending,
    user,
    signOut,
} = useAuth()
const colorMode = useColorMode()
const menu = ref(false)
const { selected } = useEvidence()
const route = useRoute()
const links = [
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
]
watch(
    () => route.path,
    () => {
        menu.value = false
    }
)
async function logout() {
    await signOut()
    await navigateTo('/login')
}
function toggleColor() {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<style scoped>
.site-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 76px;
  padding: 0.5rem max(1rem, calc((100vw - 1100px) / 2));
  border-bottom: 1px solid var(--rule);
}
.wordmark {
  flex: 1;
  font-family: var(--font-serif);
  font-size: 1.25rem;
  text-decoration: none;
  color: var(--ink);
  padding: 0.5rem 0;
}
.top-nav {
  display: flex;
  gap: 1.2rem;
}
.top-nav a {
  display: flex;
  align-items: center;
  min-height: 48px;
  text-decoration: none;
}
.top-nav .router-link-active {
  text-decoration: underline;
  text-decoration-thickness: 2px;
}
.site-menu {
  display: grid;
  gap: 0.3rem;
  max-width: 760px;
  margin: 0 auto;
  padding: 1rem;
  border-bottom: 1px solid var(--rule);
}
.site-menu a {
  display: flex;
  align-items: center;
  min-height: 48px;
}
.site-menu button {
  justify-self: start;
}
.site-main {
  width: min(100% - 2rem, 760px);
  margin: 2rem auto 4rem;
}
.site-footer {
  width: min(100% - 2rem, 760px);
  margin: 2rem auto;
  padding-top: 1rem;
  border-top: 1px solid var(--rule);
}
.site-footer a {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
}
.skip-link {
  position: fixed;
  top: -100px;
  padding: 0.7rem;
  z-index: 100;
  background: var(--paper);
}
.skip-link:focus {
  top: 0;
}
@media (max-width: 760px) {
  .top-nav {
    display: none;
  }
  .site-header {
    gap: 0.5rem;
    min-height: 68px;
  }
  .wordmark {
    font-size: 1.12rem;
  }
  .site-main {
    margin-top: 1.4rem;
  }
}
</style>
