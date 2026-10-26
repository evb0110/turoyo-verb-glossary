<template>
    <div class="research">
        <div class="page-head">
            <h1>Research notes</h1>
            <label for="rq-filter" class="small">Question</label>
            <select id="rq-filter" v-model="question">
                <option value="">
                    All questions ({{ (data?.all || 0).toLocaleString("en") }})
                </option>
                <option v-for="item in data?.questions" :key="item.name" :value="item.name">
                    {{ item.name }} ({{ item.count.toLocaleString("en") }})
                </option>
            </select>
            <label for="rq-root" class="small">Root</label>
            <input
                id="rq-root"
                v-model="rootInput"
                type="search"
                class="root-filter"
                placeholder="e.g. ʔbʕ"
            />
        </div>
        <p class="small muted intro">
            Observations from the corpus readers, tagged by research question. Each note links to the verse that
            prompted it and to the glossary entry.
        </p>
        <p v-if="error" class="error">
            Research notes could not be loaded.
        </p>
        <template v-else-if="data">
            <p class="small" role="status">
                {{ data.total.toLocaleString("en") }} notes<template v-if="data.pages > 1">
                    · page {{ data.page }} of {{ data.pages }}
                </template>
            </p>
            <article v-for="note in data.notes" :key="note.id" class="note">
                <p class="note-head">
                    <strong class="serif">{{ note.occurrence.root }}</strong>
                    <span class="tur">{{ note.occurrence.form }}</span>
                    <span class="small muted">{{ note.questions.join(" · ") }}</span>
                </p>
                <p>{{ note.occurrence.observations || note.occurrence.meaning }}</p>
                <p class="small muted">
                    {{ note.occurrence.meaning }} · {{ note.occurrence.arguments }}
                </p>
                <p class="links small">
                    <NuxtLink :to="verseHref(note.textId, note.occurrence.v)">
                        {{ note.cite }} · {{ note.title }}
                    </NuxtLink>
                    <NuxtLink v-if="note.occurrence.entryId" :to="noteEntry(note.occurrence)">
                        Entry {{ note.occurrence.root }}
                    </NuxtLink>
                </p>
            </article>
            <p v-if="!data.notes.length" class="empty">
                No observations match.
            </p>
            <nav v-if="data.pages > 1" class="pager" aria-label="Pages">
                <button
                    type="button"
                    class="btn"
                    :disabled="data.page <= 1"
                    @click="go(data.page - 1)"
                >
                    ← Previous page
                </button>
                <button
                    type="button"
                    class="btn"
                    :disabled="data.page >= data.pages"
                    @click="go(data.page + 1)"
                >
                    Next page →
                </button>
            </nav>
        </template>
    </div>
</template>

<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { verseHref } from '~/utils/verseHref'
import type { IOccurrence } from '#shared/types/IOccurrence'
import { entryHref } from '#shared/utils/entryHref'

// Over 75,000 notes: the server filters and pages them, and the URL keeps the place for Back.
const route = useRoute()
const router = useRouter()
const question = ref(String(route.query.question || ''))
const rootInput = ref(String(route.query.root || ''))
const root = refDebounced(rootInput, 350)
const page = ref(Number(route.query.page || 1))
watch([question, root], () => {
    page.value = 1
})
watch([question, root, page], () => router.replace({
    query: {
        ...(question.value ? { question: question.value } : {}),
        ...(root.value ? { root: root.value } : {}),
        ...(page.value > 1 ? { page: String(page.value) } : {}),
    },
}))
const {
    data,
    error,
} = await useFetch('/api/glossary/research', {
    query: computed(() => ({
        question: question.value,
        root: root.value,
        page: page.value,
    })),
})
function go(target: number) {
    page.value = target
    window.scrollTo({
        top: 0,
        behavior: 'instant',
    })
}
function noteEntry(occurrence: IOccurrence) {
    return entryHref(occurrence.entryId || '', `${occurrence.entryId}.${occurrence.stem}`, occurrence.sense)
}
useHead({ title: 'Research notes' })
</script>

<style scoped>
.research {
  max-width: 72rem;
}
.root-filter {
  width: 9rem;
}
.intro {
  margin-bottom: 0.5rem;
}
.note {
  display: grid;
  gap: 0.1rem;
  padding: 0.4rem 0;
  border-top: 1px solid var(--rule);
}
.note-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.75rem;
}
.note-head .serif {
  font-size: 1.0625rem;
}
.links {
  display: flex;
  flex-wrap: wrap;
  gap: 0 1rem;
}
.pager {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
</style>
