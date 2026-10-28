<template>
    <div class="review" :class="{ 'has-group': !!group }">
        <aside class="review-side">
            <h1>Review</h1>
            <p class="small">
                <strong>{{ decided.toLocaleString("en") }}</strong> of {{ (summary?.total || 0).toLocaleString("en") }}
                decided by the team
            </p>
            <progress
                :value="decided"
                :max="summary?.total || 1"
                :aria-label="`${decided} of ${summary?.total || 0} decided`"
            ></progress>
            <DocumentDownload href="/api/glossary/export/decisions" label="Decisions so far"/>
            <div class="filters">
                <label for="review-root">Verb</label>
                <input
                    id="review-root"
                    v-model="rootInput"
                    type="search"
                    placeholder="e.g. sym"
                />
                <label for="review-text">Text</label>
                <input
                    id="review-text"
                    v-model="textInput"
                    type="search"
                    placeholder="e.g. 24/48 or R024"
                />
            </div>
            <label class="group-select small">
                Group
                <select :value="group" @change="start(($event.target as HTMLSelectElement).value)">
                    <option v-for="item in allGroups" :key="item.kind" :value="item.kind">
                        {{ item.label }} ({{ item.undecided.toLocaleString("en") }})
                    </option>
                </select>
            </label>
            <nav class="groups" aria-label="Suggestion groups">
                <p class="small muted">
                    Group · undecided
                </p>
                <button
                    v-for="item in allGroups"
                    :key="item.kind"
                    type="button"
                    class="group"
                    :aria-current="item.kind === group ? 'true' : undefined"
                    :disabled="summaryPending"
                    @click="start(item.kind)"
                >
                    <span>{{ item.label }}</span>
                    <span class="num">{{ item.undecided.toLocaleString("en") }}</span>
                </button>
                <p v-if="!allGroups.length && !error && !summaryPending" class="empty small">
                    No suggestions match. Clear the verb or text filter.
                </p>
            </nav>
        </aside>
        <section class="review-main" aria-label="Current suggestion">
            <p v-if="error || queueError || proposalError || reviewError" class="error" role="alert">
                {{ reviewError || "Suggested changes could not be loaded. Please try again." }}
            </p>
            <p v-if="lastSaved" class="saved" role="status">
                Saved: {{ savedLabel }}.
                <button
                    type="button"
                    class="btn-link"
                    :disabled="undoing"
                    @click="undoLast"
                >
                    Undo
                </button>
            </p>
            <template v-if="!group">
                <h2>Choose a group</h2>
                <p>
                    Pick a group of suggestions from the list. Each suggestion opens on its own: what the machine
                    suggests, the glossary text as it is now, the machine’s reason and the passages it cites. After a
                    decision the next undecided suggestion opens.
                </p>
                <p class="start">
                    <button
                        v-if="summary?.resume"
                        type="button"
                        class="btn btn-primary"
                        @click="continueReview"
                    >
                        Continue where you left off
                    </button>
                    <button
                        v-if="allGroups.some((item) => item.kind === 'important')"
                        type="button"
                        :class="summary?.resume ? 'btn' : 'btn btn-primary'"
                        @click="start('important')"
                    >
                        Start with the most important
                    </button>
                </p>
                <p class="small muted">
                    Decisions are saved for the team; the glossary text itself does not change.
                </p>
            </template>
            <template v-else>
                <div class="card-bar">
                    <p class="small">
                        <template v-if="!queuePending">
                            {{ position + 1 }} of {{ queue.length.toLocaleString("en") }} · {{ groupLabel }} ·
                            {{ remaining(queue).toLocaleString("en") }} undecided
                        </template>
                    </p>
                    <button
                        type="button"
                        class="btn"
                        :disabled="position <= 0"
                        @click="move(-1)"
                    >
                        ← Previous
                    </button>
                    <button
                        type="button"
                        class="btn"
                        :disabled="position >= queue.length - 1"
                        @click="move(1)"
                    >
                        Next →
                    </button>
                </div>
                <p v-if="queuePending || proposalPending" role="status">
                    Loading the suggestion…
                </p>
                <p v-else-if="proposalError" class="error">
                    The suggestion could not be loaded.
                    <button type="button" class="btn-link" @click="refreshProposal()">
                        Try again
                    </button>
                </p>
                <template v-else-if="active">
                    <h2 ref="cardHeading" class="card-root serif" tabindex="-1">
                        <NuxtLink :to="entryHref(active.entryId, active.target.stemId, active.target.sense)">
                            <span v-text="detail?.entry?.root || active.entryId"></span>
                        </NuxtLink>
                    </h2>
                    <ProposalCard
                        :key="active.id"
                        :proposal="active"
                        :entry="detail?.entry || null"
                        queue
                        @reviewed="advance"
                        @undone="undoneOnCard"
                    />
                    <p class="keys small muted">
                        Keys: <kbd>A</kbd> {{ question ? "noted" : "accept" }} ·
                        <template v-if="!question">
                            <kbd>E</kbd> edit ·
                        </template>
                        <kbd>R</kbd> {{ question ? "dismiss" : "reject" }} ·
                        <kbd>D</kbd> {{ question ? "discuss later" : "decide later" }} ·
                        <kbd>C</kbd> comment · <kbd>U</kbd> undo the last decision ·
                        <kbd>J</kbd> or <kbd>→</kbd> next · <kbd>K</kbd> or <kbd>←</kbd> previous.
                        Keys do nothing while you type in a field.
                    </p>
                </template>
                <div v-else class="done">
                    <h2>End of this group</h2>
                    <p>
                        {{ remaining(queue).toLocaleString("en") }} suggestions in this group remain undecided.
                        Use Previous to return to a suggestion and change its decision.
                    </p>
                    <button type="button" class="btn" @click="openFirst">
                        Start this group again
                    </button>
                </div>
            </template>
        </section>
    </div>
</template>

<script setup lang="ts">
import { refDebounced, useEventListener } from '@vueuse/core'
import { isEditableTarget } from '~/utils/isEditableTarget'
import { proposalLabels } from '~/utils/proposalLabels'
import type { IProposalDetail } from '#shared/types/IProposalDetail'
import type { IProposalQueue } from '#shared/types/IProposalQueue'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TProposalKind } from '#shared/types/TProposalKind'
import { entryHref } from '#shared/utils/entryHref'
import { verdictLabel } from '#shared/utils/verdictLabel'

const route = useRoute()
const router = useRouter()
const request = useRequestFetch()
const { user } = useAuth()
const resume = useCookie<{ group: string
    id: string } | null>(
    `review-resume-${user.value?.id || 'reviewer'}`,
    {
        sameSite: 'lax',
        maxAge: 31536000,
    }
)
// The Verb and Text filters live in the address, so returning from an entry keeps them.
const rootInput = ref(String(route.query.root || ''))
const textInput = ref(String(route.query.text || ''))
const root = refDebounced(rootInput, 350)
const text = refDebounced(textInput, 350)
function filterQuery() {
    return {
        ...(root.value ? { root: root.value } : {}),
        ...(text.value ? { text: text.value } : {}),
    }
}
watch([root, text], () => router.replace({
    query: {
        ...route.query,
        root: root.value || undefined,
        text: text.value || undefined,
    },
}))
// Back and Forward change the address; the filters' own updates (already applied) are left alone,
// so typing goes on undisturbed.
watch(() => [route.query.root, route.query.text], ([rootQuery, textQuery]) => {
    if (String(rootQuery || '') !== root.value) rootInput.value = String(rootQuery || '')
    if (String(textQuery || '') !== text.value) textInput.value = String(textQuery || '')
})
const {
    load,
    status,
    undo,
    error: reviewError,
} = useProposalReviews()
await load()
const {
    data: summary,
    error,
    pending: summaryPending,
    refresh: refreshSummary,
} = await useFetch('/api/glossary/proposals/summary', {
    query: computed(() => ({
        root: root.value,
        text: text.value,
        resume: resume.value?.id || '',
        resumeGroup: resume.value?.group || '',
    })),
    watch: false,
})
watch([root, text], () => refreshSummary())
const allGroups = computed(() => {
    const important = summary.value?.groups.find(item => item.kind === 'important')
    return [
        ...(important
            ? [{
                    ...important,
                    label: 'Most important first',
                }]
            : []),
        ...Object.entries(proposalLabels).flatMap(([kind, label]) => {
            const counts = summary.value?.groups.find(item => item.kind === kind)
            return counts
                ? [{
                        ...counts,
                        label,
                    }]
                : []
        }),
    ]
})
const decided = computed(() => summary.value?.decided || 0)
const requestedGroup = computed(() => String(route.query.group || ''))
// A proposal-only deep link resolves its group on the server. Normal navigation
// keeps this key unchanged, so moving between cards reuses the group's id list.
const queueKey = computed(() => JSON.stringify([
    'proposal-queue',
    requestedGroup.value,
    requestedGroup.value ? '' : String(route.query.proposal || ''),
    root.value,
    text.value,
]))
const {
    data: queueData,
    pending: queuePending,
    error: queueError,
} = await useAsyncData<IProposalQueue>(queueKey, () => {
    const proposal = requestedGroup.value ? '' : String(route.query.proposal || '')
    return requestedGroup.value || (proposal && proposal !== 'done')
        ? request('/api/glossary/proposals/queue', {
                query: {
                    group: requestedGroup.value,
                    proposal,
                    root: root.value,
                    text: text.value,
                },
            })
        : Promise.resolve({
                group: '',
                ids: [],
            })
})
const group = computed(() => requestedGroup.value || queueData.value?.group || '')
const groupLabel = computed(() => group.value === 'important'
    ? 'Most important first'
    : proposalLabels[group.value as TProposalKind] || 'Suggested changes')
const queue = computed(() => queueData.value?.ids || [])
const activeProposalId = computed(() => {
    if (!group.value || queuePending.value || route.query.proposal === 'done') return ''
    const requested = String(route.query.proposal || '')
    if (queue.value.includes(requested)) return requested
    const remembered = resume.value?.group === group.value ? resume.value.id : ''
    if (!requested && queue.value.includes(remembered) && status(remembered) === 'open') return remembered
    return queue.value.find(id => status(id) === 'open') || queue.value[0] || ''
})
const {
    data: detail,
    pending: proposalPending,
    error: proposalError,
    refresh: refreshProposal,
} = await useAsyncData<IProposalDetail | null>(
    computed(() => `proposal-detail-${activeProposalId.value}`),
    () => activeProposalId.value
        ? request(`/api/glossary/proposals/${encodeURIComponent(activeProposalId.value)}`)
        : Promise.resolve(null)
)
const active = computed(() => detail.value?.proposal.id === activeProposalId.value ? detail.value.proposal : null)
const question = computed(() => !!active.value && ['question', 'note'].includes(active.value.kind))
const position = computed(() => activeProposalId.value
    ? queue.value.indexOf(activeProposalId.value)
    : queue.value.length - 1)
const lastSaved = ref<IProposalReview | null>(null)
const lastSavedGroup = ref('')
const lastSavedQuestion = ref(false)
const savedLabel = computed(() => lastSaved.value
    ? `${verdictLabel(lastSaved.value.verdict, lastSavedQuestion.value, !!lastSaved.value.edited)} (${lastSaved.value.entryId.replaceAll('-', ' ')})`
    : '')
const undoing = ref(false)
const cardHeading = ref<HTMLElement | null>(null)
function remaining(ids: string[]) {
    return ids.filter(id => status(id) === 'open').length
}
async function select(kind: string, id?: string) {
    if (id && id !== 'done') resume.value = {
        group: kind,
        id,
    }
    await router.push({
        path: '/review',
        query: {
            group: kind,
            ...(id ? { proposal: id } : {}),
            ...filterQuery(),
        },
    })
    await nextTick()
    cardHeading.value?.focus({ preventScroll: true })
    window.scrollTo({
        top: 0,
        behavior: 'instant',
    })
}
function start(kind: string) {
    return select(kind)
}
function continueReview() {
    if (summary.value?.resume) return select(summary.value.resume.group, summary.value.resume.id)
}
function move(delta: number) {
    const next = queue.value[position.value + delta]
    if (next) return select(group.value, next)
}
function openFirst() {
    if (queue.value[0]) return select(group.value, queue.value[0])
}
async function advance(saved: IProposalReview) {
    lastSaved.value = saved
    lastSavedGroup.value = group.value
    lastSavedQuestion.value = question.value
    const candidates = [...queue.value.slice(position.value + 1), ...queue.value.slice(0, position.value)]
    const next = candidates.find(id => status(id) === 'open')
    await Promise.all([select(group.value, next || 'done'), refreshSummary()])
}
async function undoLast() {
    if (!lastSaved.value || undoing.value) return
    undoing.value = true
    if (await undo(lastSaved.value)) {
        const id = lastSaved.value.proposalId
        lastSaved.value = null
        await Promise.all([select(group.value || lastSavedGroup.value, id), refreshSummary()])
    }
    undoing.value = false
}
// Undo from the card itself, for example after going back to an earlier decision.
function undoneOnCard(proposalId: string) {
    if (lastSaved.value?.proposalId === proposalId) lastSaved.value = null
    refreshSummary()
}
// Navigation and undo keys. Decision keys live on the card (ProposalDecision).
useEventListener('keydown', (event: KeyboardEvent) => {
    if (event.defaultPrevented || event.repeat || event.metaKey || event.ctrlKey || event.altKey
        || !group.value || isEditableTarget(event.target)) return
    const key = event.key.toLowerCase()
    const action = key === 'j' || key === 'arrowright'
        ? () => move(1)
        : key === 'k' || key === 'arrowleft'
            ? () => move(-1)
            : key === 'u' && lastSaved.value ? () => undoLast() : null
    if (!action) return
    event.preventDefault()
    action()
})
watch(group, (value) => {
    if (!value) refreshSummary()
})
onMounted(() => {
    watch([activeProposalId, group], ([id, kind]) => {
        if (!id || !kind) return
        resume.value = {
            group: kind,
            id,
        }
        if (!route.query.proposal) router.replace({
            query: {
                group: kind,
                proposal: id,
                ...filterQuery(),
            },
        })
    }, { immediate: true })
})
useHead({ title: 'Review suggested changes' })
</script>

<style scoped>
.review {
  display: grid;
  grid-template-columns: 17rem minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
}
.review-side {
  position: sticky;
  top: 0.75rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.5rem;
  max-height: calc(100vh - 1.5rem);
  overflow-y: auto;
}
progress {
  width: 100%;
  height: 0.5rem;
  accent-color: var(--accent);
}
.filters {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 0.3rem 0.5rem;
  font-size: 0.875rem;
}
.group-select {
  display: none;
}
.groups {
  display: grid;
}
.group {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.2rem 0.4rem;
  border-left: 3px solid transparent;
  color: var(--ink);
  font-size: 0.9375rem;
  text-align: left;
}
.group:hover:not(:disabled) {
  background: var(--bg-soft);
}
.group[aria-current="true"] {
  border-left-color: var(--accent);
  background: var(--bg-soft);
  font-weight: 600;
}
.group .num {
  color: var(--muted);
}
.review-main {
  display: grid;
  gap: 0.6rem;
  max-width: 90rem;
}
.saved {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.25rem 0.6rem;
  border-left: 3px solid var(--accent);
  background: var(--bg-soft);
}
.card-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
}
.card-bar p {
  flex: 1;
}
.card-root {
  font-size: 1.75rem;
  font-weight: 700;
}
.card-root a {
  text-decoration: none;
}
.card-root a:hover {
  text-decoration: underline;
}
.start {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.done {
  display: grid;
  justify-items: start;
  gap: 0.4rem;
}
@media (max-width: 900px) {
  .review {
    grid-template-columns: minmax(0, 1fr);
    gap: 0.75rem;
  }
  .review-side {
    position: static;
    max-height: none;
    overflow: visible;
  }
  .has-group .groups,
  .has-group .filters,
  .has-group progress {
    display: none;
  }
  .has-group .group-select {
    display: grid;
    gap: 0.15rem;
  }
  .has-group .review-main {
    padding-bottom: 4rem;
  }
  .keys {
    display: none;
  }
}
</style>
