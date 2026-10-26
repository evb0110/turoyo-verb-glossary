<template>
    <div class="stack home">
        <section
            v-if="isApproved"
            class="review-welcome stack"
            aria-labelledby="review-title"
        >
            <p class="caption">
                For the editors
            </p>
            <h1 id="review-title">
                Review the suggested changes
            </h1>
            <p v-if="summary">
                The machine has suggested
                {{ summary.total.toLocaleString() }} changes to the glossary. You
                have decided {{ summary.ownDecided.toLocaleString() }}.
            </p>
            <p v-else class="error">
                Suggested changes could not be loaded. Please try again.
            </p>
            <NuxtLink
                to="/review"
                class="primary"
            >Start reviewing <span aria-hidden="true">→</span></NuxtLink>
        </section>
        <section class="lookup stack">
            <h2>Find a verb</h2>
            <form class="home-search" @submit.prevent="search">
                <label for="home-query">Find a verb: root, form or meaning</label>
                <input
                    id="home-query"
                    v-model="query"
                    type="search"
                    placeholder="e.g. sym or put"
                />
                <button class="primary" type="submit">
                    Search
                </button>
            </form>
            <NuxtLink to="/glossary" class="browse-link">Browse all verbs →</NuxtLink>
        </section>
        <section class="rule-section stack">
            <h2>How this works</h2>
            <p>
                This glossary brings together Turoyo verbs and examples from the texts.
                The machine has read the texts and suggested changes for the editors to
                check. Your decisions are saved for the team; they do not change the
                glossary text.
            </p>
            <NuxtLink to="/help">Read the guide →</NuxtLink>
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
  gap: 2rem;
}
.review-welcome {
  border: 1px solid var(--rule);
  border-top: 4px solid var(--accent);
  border-radius: 8px;
  padding: clamp(1.1rem, 4vw, 2rem);
  background: var(--panel);
}
.review-welcome h1 {
  font-size: 2.2rem;
}
.review-welcome .primary {
  justify-self: start;
  gap: 1.2rem;
}
.home-search {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.7rem;
}
.home-search label {
  grid-column: 1 / -1;
}
.browse-link {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  justify-self: start;
}
.rule-section {
  margin-top: 0;
}
</style>
