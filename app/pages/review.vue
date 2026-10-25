<template>
    <div>
        <header class="page-heading">
            <p class="eyebrow">
                Editorial desk
            </p>
            <h1>Review proposals</h1>
            <p>Read the evidence, compare the glossary, and leave a considered decision.</p>
        </header>
        <div class="review-progress">
            <span>
                <strong>{{ proposals.length }}</strong>
                total
            </span>
            <span v-for="value in statuses" :key="value">
                <strong>
                    {{ proposals.filter((item) => status(item.id) === value).length }}
                </strong>
                {{ value }}
            </span>
        </div>
        <div class="queue-filters">
            <label>
                Kind
                <select v-model="kind">
                    <option value="">All kinds</option>
                    <option v-for="value in kinds" :key="value" :value="value">
                        {{ value.replaceAll('-', ' ') }}
                    </option>
                </select>
            </label>
            <label>
                Stage
                <select v-model="stage">
                    <option value="">All stages</option>
                    <option v-for="value in stages" :key="value">{{ value }}</option>
                </select>
            </label>
            <label>
                Priority
                <select v-model="priority">
                    <option value="">All priorities</option>
                    <option value="1">1 · substantive</option>
                    <option value="2">2 · supporting</option>
                    <option value="3">3 · cosmetic</option>
                </select>
            </label>
            <label>
                Status
                <select v-model="verdict">
                    <option value="">All statuses</option>
                    <option v-for="value in statuses" :key="value">{{ value }}</option>
                </select>
            </label>
            <label>
                Text
                <input v-model="text" placeholder="e.g. R024 or 24/"/>
            </label>
            <label>
                Root
                <input v-model="root" placeholder="Filter root…"/>
            </label>
        </div>
        <p v-if="error || reviewError" class="error" role="alert">
            {{ reviewError || 'Proposals could not be loaded.' }}
        </p>
        <div class="keyboard-help">
            <span>{{ filtered.length }} matching · sorted by priority</span>
            <span>
                <kbd>j</kbd>
                /
                <kbd>k</kbd>
                move ·
                <kbd>a</kbd>
                accept ·
                <kbd>r</kbd>
                reject ·
                <kbd>d</kbd>
                discuss ·
                <kbd>o</kbd>
                entry
            </span>
        </div>
        <div v-if="filtered.length" class="queue-layout">
            <div class="queue-list" role="list" aria-label="Proposal queue">
                <button
                    v-for="(proposal, i) in filtered"
                    :id="`queue-${proposal.id}`"
                    :key="proposal.id"
                    class="queue-item"
                    :class="{ active: active?.id === proposal.id }"
                    :aria-current="active?.id === proposal.id ? 'true' : undefined"
                    @click="selectedId = proposal.id"
                >
                    <span class="queue-item-meta">
                        <span>
                            P{{ proposal.priority }} ·
                            {{ entryRoots.get(proposal.entryId) || proposal.entryId }}
                        </span>
                        <span>{{ status(proposal.id) }}</span>
                    </span>
                    <strong>{{ proposal.summary }}</strong>
                    <span class="muted">
                        {{ i + 1 }} · {{ proposal.kind.replaceAll('-', ' ') }}
                    </span>
                </button>
            </div>
            <div v-if="active" class="queue-detail">
                <div class="row detail-heading">
                    <span class="eyebrow">
                        {{ entryRoots.get(active.entryId) || active.entryId }} ·
                        {{ active.target.sense ? `Sense ${active.target.sense}` : 'Entry' }}
                    </span>
                    <NuxtLink
                        :to="entryHref(active.entryId, active.target.stemId, active.target.sense)"
                    >
                        Open entry ↗
                    </NuxtLink>
                </div>
                <ProposalCard :key="active.id" :proposal="active" @reviewed="advance"/>
            </div>
        </div>
        <p v-else class="empty">
            No proposals match these filters.
        </p>
        <p class="queue-notice muted" aria-live="polite">
            {{ notice }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { onKeyStroke } from '@vueuse/core'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'
import { entryHref } from '#shared/utils/entryHref'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

const {
    data,
    error,
} = await useFetch('/api/glossary/proposals')
const { data: index } = await useFetch('/api/glossary/roots')
const {
    load,
    status,
    review,
    error: reviewError,
} = useProposalReviews()
await load()
const proposals = computed(() => data.value || [])
const entryRoots = computed(() => new Map((index.value || []).map(item => [item.id, item.root])))
const statuses = ['open', 'accepted', 'rejected', 'discuss']
const kinds = computed(() => [...new Set(proposals.value.map(item => item.kind))].sort())
const stages = ['synthesis', 'citation-check', 'proofreading']
const kind = ref('')
const route = useRoute()
const stage = ref('')
const priority = ref('')
const verdict = ref(route.query.proposal ? '' : 'open')
const text = ref('')
const root = ref('')
const selectedId = ref(String(route.query.proposal || ''))
watch(
    () => route.query.proposal,
    (id) => {
        if (!id) return
        verdict.value = ''
        kind.value = ''
        stage.value = ''
        priority.value = ''
        text.value = ''
        root.value = ''
        selectedId.value = String(id)
    }
)
const notice = ref('')
const searchOpen = useState('search-open', () => false)
const filtered = computed(() =>
    proposals.value.filter(
        item =>
            (!kind.value || item.kind === kind.value)
            && (!stage.value || item.stage === stage.value)
            && (!priority.value || String(item.priority) === priority.value)
            && (!verdict.value || status(item.id) === verdict.value)
            && (!text.value
                || item.evidence.some(ref =>
                    `${ref.textId} ${ref.cite}`.toLowerCase().includes(text.value.toLowerCase())
                ))
                && normalizeTuroyo(entryRoots.value.get(item.entryId) || item.entryId).includes(
                    normalizeTuroyo(root.value)
                )
    )
)
const active = computed(
    () => filtered.value.find(item => item.id === selectedId.value) || filtered.value[0]
)
function advance() {
    if (active.value) selectedId.value = active.value.id
}
function move(delta: number) {
    const i = filtered.value.findIndex(item => item.id === active.value?.id)
    const next = filtered.value[Math.max(0, Math.min(filtered.value.length - 1, i + delta))]
    if (next) {
        selectedId.value = next.id
        document.getElementById(`queue-${next.id}`)?.scrollIntoView({ block: 'nearest' })
    }
}
onKeyStroke(['j', 'k', 'a', 'r', 'd', 'o'], async (event) => {
    if (
        (event.target as HTMLElement)?.closest('input, textarea, select, [contenteditable=true]')
        || event.metaKey
        || event.ctrlKey
        || event.altKey
        || searchOpen.value
    )
        return
    event.preventDefault()
    if (event.key === 'j' || event.key === 'k') {
        move(event.key === 'j' ? 1 : -1)
        return
    }
    const proposal = active.value
    if (!proposal) return
    if (event.key === 'o') {
        await navigateTo(entryHref(proposal.entryId, proposal.target.stemId, proposal.target.sense))
        return
    }
    const action: TReviewVerdict
        = event.key === 'a' ? 'accept' : event.key === 'r' ? 'reject' : 'discuss'
    const i = filtered.value.findIndex(item => item.id === proposal.id)
    const next = filtered.value[i + 1] || filtered.value[i - 1]
    if (next) selectedId.value = next.id
    const saved = await review(proposal.id, proposal.entryId, action)
    notice.value = saved ? `${action} saved for ${proposal.summary}` : 'Review was not saved.'
})
useHead({ title: 'Review proposals' })
</script>

<style scoped>
.review-progress {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    padding-bottom: 1.2rem;
    font-size: 0.75rem;
    color: var(--muted);
}
.review-progress strong {
    color: var(--ink);
    font-weight: 500;
}
.queue-filters {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.7rem;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 1rem 0;
}
.queue-filters label {
    display: grid;
    font-size: 0.65rem;
    gap: 0.25rem;
    color: var(--muted);
}
.queue-filters input,
.queue-filters select {
    width: 100%;
    font-size: 0.75rem;
}
.keyboard-help {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.5rem;
    font-size: 0.65rem;
    color: var(--muted);
    margin: 1rem 0;
}
kbd {
    color: var(--ink);
    font-family: monospace;
}
.queue-layout {
    display: grid;
    grid-template-columns: minmax(220px, 35%) minmax(0, 1fr);
    gap: 2rem;
    align-items: start;
}
.queue-list {
    max-height: 75vh;
    overflow-y: auto;
    border-top: 1px solid var(--rule);
}
.queue-item {
    display: grid;
    text-align: left;
    width: 100%;
    gap: 0.35rem;
    border-bottom: 1px solid var(--rule);
    padding: 0.9rem;
    border-left: 3px solid transparent;
}
.queue-item.active {
    background: var(--panel);
    border-left-color: var(--accent);
}
.queue-item strong {
    font-size: 0.85rem;
    font-weight: 400;
}
.queue-item-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.65rem;
    color: var(--accent);
}
.queue-item > .muted {
    font-size: 0.65rem;
}
.detail-heading {
    justify-content: space-between;
    font-size: 0.7rem;
    padding: 0.5rem 0;
}
.queue-notice {
    font-size: 0.8rem;
    padding-top: 1rem;
}
@media (max-width: 950px) {
    .queue-layout {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    .queue-list {
        max-height: 230px;
    }
}
@media (max-width: 500px) {
    .queue-filters {
        grid-template-columns: 1fr 1fr;
    }
}
</style>
