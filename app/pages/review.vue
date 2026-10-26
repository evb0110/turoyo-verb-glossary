<template>
    <div>
        <header v-if="!group" class="page-heading">
            <h1>Review suggested changes</h1>
            <p>
                Check one machine suggestion at a time and choose Accept, Reject or
                Decide later.
            </p>
        </header>
        <p v-if="error || queueError || proposalError || reviewError" class="error" role="alert">
            {{
                reviewError
                    || "Suggested changes could not be loaded. Please try again."
            }}
        </p>
        <div v-if="lastSaved" class="saved-notice" role="status">
            <span>Saved.
                {{
                    lastSaved.verdict === "accept"
                        ? "Accepted"
                        : lastSaved.verdict === "reject"
                            ? "Rejected"
                            : "For discussion later"
                }}.</span>
            <button class="text-button" :disabled="undoing" @click="undoLast">
                Undo
            </button>
        </div>
        <template v-if="!group">
            <section class="progress-section stack">
                <p>
                    <strong>{{ decided.toLocaleString() }} of
                        {{ (summary?.total || 0).toLocaleString() }} decided</strong>
                </p>
                <progress
                    :value="decided"
                    :max="(summary?.total || 0) || 1"
                    :aria-label="`${decided} of ${(summary?.total || 0)} decided`"
                ></progress>
                <button
                    v-if="summary?.resume"
                    class="primary resume-button"
                    @click="continueReview"
                >
                    Continue where you left off →
                </button>
            </section>
            <details class="filter-disclosure">
                <summary>Filter by verb or text</summary>
                <div class="stack">
                    <label for="review-root">Verb root</label><input id="review-root" v-model="root" placeholder="e.g. sym"/>
                    <label for="review-text">Text reference</label><input
                        id="review-text"
                        v-model="text"
                        placeholder="e.g. 24/48 or R024"
                    />
                </div>
            </details>
            <p v-if="summaryPending" role="status">
                Loading suggested changes…
            </p>
            <div class="groups" aria-label="Suggestion groups">
                <button
                    v-if="important"
                    class="group-row important"
                    :disabled="summaryPending"
                    @click="start('important')"
                >
                    <strong>Most important first</strong><span>{{ important.undecided }} still undecided ·
                        {{ important.total }} total</span><span class="group-arrow" aria-hidden="true">→</span>
                </button>
                <button
                    v-for="item in groups"
                    :key="item.kind"
                    class="group-row"
                    :disabled="summaryPending"
                    @click="start(item.kind)"
                >
                    <strong>{{ item.label }}</strong><span>{{ item.undecided }} still undecided ·
                        {{ item.total }} total</span><span class="group-arrow" aria-hidden="true">→</span>
                </button>
            </div>
            <p v-if="!groups.length && !error && !summaryPending" class="empty">
                No suggestions match. Try clearing the verb or text filter.
            </p>
            <p class="caption rule-section">
                Your decisions are saved for the team. The glossary text stays
                unchanged.
            </p>
        </template>
        <template v-else>
            <NuxtLink to="/review" class="back-link">← Back to groups</NuxtLink>
            <header ref="cardHeading" class="card-heading stack" tabindex="-1">
                <p v-if="!queuePending">
                    {{ position + 1 }} of {{ queue.length }} · {{ groupLabel }}
                </p>
                <h1 v-if="active">
                    <NuxtLink
                        :to="
                            entryHref(
                                active.entryId,
                                active.target.stemId,
                                active.target.sense
                            )
                        "
                    >{{ detail?.entry?.root || active.entryId }}</NuxtLink>
                </h1>
            </header>
            <p v-if="queuePending || proposalPending" role="status">
                Loading the glossary passage…
            </p>
            <p v-else-if="proposalError" class="error">
                The glossary passage could not be loaded.
                <button class="text-button" @click="refreshProposal()">
                    Try again
                </button>
            </p>
            <template v-else-if="active">
                <ProposalCard
                    :key="active.id"
                    :proposal="active"
                    :entry="detail?.entry || null"
                    queue
                    @reviewed="advance"
                />
                <nav class="card-navigation" aria-label="Move between suggestions">
                    <button class="quiet" :disabled="position <= 0" @click="move(-1)">
                        ← Previous
                    </button>
                    <button class="text-button" @click="skip">
                        Skip
                    </button>
                    <button
                        class="quiet"
                        :disabled="position >= queue.length - 1"
                        @click="move(1)"
                    >
                        Next →
                    </button>
                </nav>
            </template>
            <div v-else class="stack completed">
                <h2>You have reached the end of this group</h2>
                <p>
                    {{ remaining(queue) }} suggestions remain undecided. You can return to
                    a previous suggestion to change a decision.
                </p>
                <button class="quiet" @click="openFirst">
                    Review this group again
                </button><NuxtLink to="/review" class="primary">Back to groups</NuxtLink>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { proposalLabels } from '~/utils/proposalLabels'
import type { IProposalDetail } from '#shared/types/IProposalDetail'
import type { IProposalQueue } from '#shared/types/IProposalQueue'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TProposalKind } from '#shared/types/TProposalKind'
import { entryHref } from '#shared/utils/entryHref'

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
const root = ref('')
const text = ref('')
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
const groups = computed(() => Object.entries(proposalLabels).flatMap(([kind, label]) => {
    const counts = summary.value?.groups.find(item => item.kind === kind)
    return counts
        ? [{
                ...counts,
                label,
            }]
        : []
}))
const important = computed(() => summary.value?.groups.find(item => item.kind === 'important'))
const decided = computed(() => summary.value?.decided || 0)
const requestedGroup = computed(() => String(route.query.group || ''))
// A proposal-only deep link resolves its group on the server. Normal navigation
// keeps this key unchanged, so moving between cards reuses the group's id list.
const queueKey = computed(() => JSON.stringify([
    'proposal-queue', requestedGroup.value,
    requestedGroup.value ? '' : String(route.query.proposal || ''), root.value, text.value,
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
const position = computed(() => activeProposalId.value
    ? queue.value.indexOf(activeProposalId.value)
    : queue.value.length - 1)
const lastSaved = ref<IProposalReview | null>(null)
const lastSavedGroup = ref('')
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
function skip() {
    const next = queue.value[position.value + 1] || queue.value[0]
    if (next) return select(group.value, next)
}
function openFirst() {
    if (queue.value[0]) return select(group.value, queue.value[0])
}
async function advance(saved: IProposalReview) {
    lastSaved.value = saved
    lastSavedGroup.value = group.value
    const candidates = [...queue.value.slice(position.value + 1), ...queue.value.slice(0, position.value)]
    const next = candidates.find(id => status(id) === 'open')
    await Promise.all([select(group.value, next || 'done'), refreshSummary()])
}
async function undoLast() {
    if (!lastSaved.value) return
    undoing.value = true
    if (await undo(lastSaved.value)) {
        const id = lastSaved.value.proposalId
        lastSaved.value = null
        await Promise.all([select(group.value || lastSavedGroup.value, id), refreshSummary()])
    }
    undoing.value = false
}
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
            },
        })
    }, { immediate: true })
})
useHead({ title: 'Review suggested changes' })
</script>

<style scoped>
.progress-section {
  margin: 1.5rem 0;
}
progress {
  width: 100%;
  accent-color: var(--accent);
  height: 12px;
}
.resume-button {
  justify-self: start;
}
.filter-disclosure {
  margin-bottom: 1rem;
}
.groups {
  border-top: 1px solid var(--rule);
}
.group-row {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.35rem 1rem;
  text-align: left;
  padding: 1.2rem 0.4rem;
  border-bottom: 1px solid var(--rule);
}
.group-row strong {
  font-weight: 500;
  font-size: 1.1rem;
}
.group-row > span:not(.group-arrow) {
  font-size: 0.889rem;
  color: var(--muted);
}
.group-arrow {
  grid-column: 2;
  grid-row: 1 / 3;
  align-self: center;
  color: var(--accent);
}
.important {
  background: var(--panel);
  padding-left: 1rem;
  padding-right: 1rem;
}
.back-link {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  margin-bottom: 0.6rem;
}
.card-heading {
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.card-heading h1 {
  font-size: 3rem;
}
.card-heading h1 a {
  text-decoration: none;
}
.saved-notice {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.7rem;
  padding: 0.4rem 1rem;
  margin-bottom: 0.8rem;
  background: var(--panel);
  border-left: 4px solid var(--accent);
}
.card-navigation {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
.completed {
  margin-top: 2rem;
}
@media (max-width: 760px) {
  .card-navigation {
    margin-top: -6rem;
    padding-bottom: 8rem;
    position: relative;
  }
}
</style>
