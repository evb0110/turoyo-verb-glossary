<template>
    <div class="history small">
        <p v-if="error" role="alert" class="error">
            {{ error }}
        </p>
        <p v-else-if="loading && !events.length" role="status">
            Loading decisions…
        </p>
        <p v-else-if="!events.length" class="muted">
            No decisions yet.
        </p>
        <ol v-else>
            <li v-for="item in events" :key="item.id">
                <strong>{{ label(item) }}</strong> · {{ item.userName }} ·
                <time :datetime="item.createdAt">{{ formatReviewDate(item.createdAt) }}</time>
                <span v-if="item.edited" class="edited">
                    <span v-if="item.edited.headword">{{ item.edited.headword }}. </span>{{ item.edited.text }}
                    <span v-if="item.edited.translation">‘{{ item.edited.translation }}’</span>
                </span>
                <span v-if="item.comment" class="comment">Comment: {{ item.comment }}</span>
            </li>
        </ol>
        <p v-if="events.length === 100" class="muted">
            Showing the most recent 100 events.
        </p>
    </div>
</template>

<script setup lang="ts">
import { formatReviewDate } from '~/utils/formatReviewDate'
import { verdictLabel } from '~/utils/verdictLabel'
import type { IProposalReviewEvent } from '#shared/types/IProposalReviewEvent'

const props = defineProps<{ proposalId: string
    question: boolean }>()
const { decision } = useProposalReviews()
const events = ref<IProposalReviewEvent[]>([])
const loading = ref(false)
const error = ref('')
function label(item: IProposalReviewEvent) {
    if (item.undoneReviewId) return 'Decision undone'
    return item.verdict ? verdictLabel(item.verdict, props.question, !!item.edited) : ''
}
async function load() {
    loading.value = true
    error.value = ''
    try {
        events.value = await $fetch<IProposalReviewEvent[]>(`/api/glossary/reviews/${encodeURIComponent(props.proposalId)}`)
    }
    catch {
        error.value = 'Decision history could not be loaded. Close and reopen it to try again.'
    }
    finally {
        loading.value = false
    }
}
onMounted(load)
// A new decision or an undo while the history is open adds an event.
watch(() => decision(props.proposalId)?.id, (id) => {
    if (!id?.startsWith('pending:')) load()
})
</script>

<style scoped>
ol {
  display: grid;
  gap: 0.2rem;
  margin: 0;
  padding: 0;
  list-style: none;
}
.edited,
.comment {
  display: block;
  padding-left: 1rem;
}
.edited {
  white-space: pre-line;
}
</style>
