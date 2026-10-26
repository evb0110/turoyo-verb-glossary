<template>
    <div class="home">
        <h1>Turoyo Verb Glossary</h1>
        <p class="muted">
            Turoyo verbs with their stems, meanings and examples from the texts, and machine suggestions for
            the editors to check.
        </p>
        <form class="home-search" role="search" @submit.prevent="search">
            <label for="home-query">Search roots, forms, meanings, examples and texts</label>
            <div class="row">
                <input
                    id="home-query"
                    v-model="query"
                    type="search"
                    placeholder="e.g. sym, wollen or put"
                    autocomplete="off"
                />
                <button class="btn btn-primary" type="submit">
                    Search
                </button>
            </div>
        </form>
        <section v-if="isApproved" class="block">
            <h2>Review</h2>
            <p v-if="summary">
                {{ summary.decided.toLocaleString("en") }} of {{ summary.total.toLocaleString("en") }} suggestions
                decided by the team, {{ summary.ownDecided.toLocaleString("en") }} of them by you.
            </p>
            <p v-else class="error">
                Suggested changes could not be loaded. Please try again.
            </p>
            <NuxtLink to="/review" class="btn btn-primary">
                {{ summary?.decided ? "Continue reviewing" : "Start reviewing" }}
            </NuxtLink>
        </section>
        <section class="block">
            <h2>Browse</h2>
            <ul class="links">
                <li>
                    <NuxtLink to="/glossary">Glossary</NuxtLink>: every root with its first meaning and its suggestions
                </li>
                <li><NuxtLink to="/texts">Texts</NuxtLink>: the corpus with translations and the analysed verbs</li>
                <li>
                    <NuxtLink to="/research">Research notes</NuxtLink>: observations from the texts by research question
                </li>
                <li><NuxtLink to="/help">Help</NuxtLink>: how the pages and the review work</li>
            </ul>
        </section>
    </div>
</template>

<script setup lang="ts">
const { isApproved } = useAuth()
const { data: summary } = await useFetch('/api/glossary/proposals/summary')
const query = ref('')
function search() {
    return navigateTo({
        path: '/glossary',
        query: query.value.trim() ? { q: query.value.trim() } : {},
    })
}
useHead({ title: 'Welcome' })
</script>

<style scoped>
.home {
  display: grid;
  gap: 0.75rem;
  max-width: 48rem;
}
.home-search {
  display: grid;
  gap: 0.25rem;
}
.home-search label {
  font-size: 0.875rem;
  font-weight: 600;
}
.row {
  display: flex;
  gap: 0.5rem;
}
.row input {
  flex: 1;
}
.block {
  display: grid;
  justify-items: start;
  gap: 0.35rem;
  margin-top: 0.5rem;
}
.links {
  margin: 0;
  padding-left: 1.1rem;
  list-style: disc;
}
</style>
