<template>
    <div class="site-frame">
        <a href="#main-content" class="skip-link">Skip to content</a>
        <header class="site-header">
            <NuxtLink to="/" class="wordmark">Turoyo Verb Glossary</NuxtLink>
            <nav class="top-nav" aria-label="Main navigation">
                <NuxtLink v-for="link in links" :key="link.to" :to="link.to">{{
                    link.label
                }}</NuxtLink>
                <button v-if="user" class="text-button" @click="logout">
                    Sign out
                </button>
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
            <button class="text-button" @click="toggleColor">
                {{ colorLabel }}
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
            <button class="text-button" @click="toggleColor">
                {{ colorLabel }}
            </button>
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
        ? [
                {
                    to: '/admin',
                    label: 'Admin',
                },
            ]
        : []),
])
const colorLabel = computed(() => (colorMode.value === 'dark' ? 'Use light colours' : 'Use dark colours'))
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
  padding: 0.5rem max(1rem, calc((100% - 760px) / 2));
  border-bottom: 1px solid var(--rule);
}
.wordmark {
  flex: 1;
  font-family: var(--font-serif);
  font-size: 1.25rem;
  text-decoration: none;
  color: var(--ink);
}
.top-nav {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}
.top-nav a,
.top-nav .text-button {
  min-width: 0;
  padding: 0;
  text-decoration: none;
}
.top-nav .router-link-active {
  text-decoration: underline;
  text-decoration-thickness: 2px;
}
.menu-toggle {
  display: none;
}
.site-menu {
  display: grid;
  justify-items: start;
  gap: 0.3rem;
  padding: 0.5rem max(1rem, calc((100% - 760px) / 2)) 1rem;
  border-bottom: 1px solid var(--rule);
}
.site-menu .text-button {
  min-height: 48px;
  padding: 0;
}
.site-main {
  width: min(100% - 2rem, 760px);
  margin: 2rem auto 4rem;
}
.site-footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  width: min(100% - 2rem, 760px);
  margin: 2rem auto;
  padding-top: 1rem;
  border-top: 1px solid var(--rule);
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
  .menu-toggle {
    display: inline-flex;
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
