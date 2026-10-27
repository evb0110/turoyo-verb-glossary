<template>
    <div class="history small">
        <p v-if="error" role="alert" class="error">
            {{ error }}
        </p>
        <p v-else-if="loading && !events.length && !quiet" role="status">
            Loading the decision history…
        </p>
        <p v-else-if="!loading && !events.length && !quiet" class="muted">
            No decisions yet.
        </p>
        <template v-else-if="events.length">
            <p><strong>Decision history:</strong></p>
            <ol>
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
        </template>
    </div>
</template>

<script setup lang="ts">
import type { IProposalReviewEvent } from '#shared/types/IProposalReviewEvent'
import { formatReviewDate } from '#shared/utils/formatReviewDate'
import { verdictLabel } from '#shared/utils/verdictLabel'

// Quiet: nothing is shown while loading or when there are no decisions (the review queue opens it on every card).
const props = withDefaults(
    defineProps<{ proposalId: string
        question: boolean
        quiet?: boolean }>(),
    { quiet: false }
)
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
        error.value = 'The decision history could not be loaded. Reload the page to try again.'
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
