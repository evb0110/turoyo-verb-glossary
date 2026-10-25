<template>
    <div>
        <header v-if="!group" class="page-heading">
            <h1>Review suggested changes</h1>
            <p>
                Check one machine suggestion at a time and choose Accept, Reject or
                Decide later.
            </p>
        </header>
        <p v-if="error || reviewError" class="error" role="alert">
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
                        {{ proposals.length.toLocaleString() }} decided</strong>
                </p>
                <progress
                    :value="decided"
                    :max="proposals.length || 1"
                    :aria-label="`${decided} of ${proposals.length} decided`"
                ></progress>
                <button
                    v-if="resume && proposals.some((item) => item.id === resume?.id)"
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
            <div class="groups" aria-label="Suggestion groups">
                <button
                    v-if="important.length"
                    class="group-row important"
                    @click="start('important')"
                >
                    <strong>Most important first</strong><span>{{ remaining(important) }} still undecided ·
                        {{ important.length }} total</span><span class="group-arrow" aria-hidden="true">→</span>
                </button>
                <button
                    v-for="item in groups"
                    :key="item.kind"
                    class="group-row"
                    @click="start(item.kind)"
                >
                    <strong>{{ item.label }}</strong><span>{{ remaining(item.items) }} still undecided ·
                        {{ item.items.length }} total</span><span class="group-arrow" aria-hidden="true">→</span>
                </button>
            </div>
            <p v-if="!groups.length && !error" class="empty">
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
                <p>{{ position + 1 }} of {{ queue.length }} · {{ groupLabel }}</p>
                <h1 v-if="active">
                    <NuxtLink
                        :to="
                            entryHref(
                                active.entryId,
                                active.target.stemId,
                                active.target.sense
                            )
                        "
                    >{{ roots.get(active.entryId) || active.entryId }}</NuxtLink>
                </h1>
            </header>
            <template v-if="active">
                <p v-if="entryPending" role="status">
                    Loading the glossary passage…
                </p>
                <p v-else-if="entryError" class="error">
                    The glossary passage could not be loaded.
                    <button class="text-button" @click="refreshEntry()">
                        Try again
                    </button>
                </p>
                <ProposalCard
                    v-else-if="activeEntry"
                    :key="active.id"
                    :proposal="active"
                    :entry="activeEntry.entry"
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
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TProposalKind } from '#shared/types/TProposalKind'
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
    undo,
    error: reviewError,
} = useProposalReviews()
await load()
const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const resume = useCookie<{ group: string
    id: string } | null>(
    `review-resume-${user.value?.id || 'reviewer'}`,
    {
        sameSite: 'lax',
        maxAge: 31536000,
    }
)
const proposals = computed(() => data.value || [])
const roots = computed(
    () => new Map((index.value || []).map(item => [item.id, item.root]))
)
const root = ref('')
const text = ref('')
const matching = computed(() =>
    proposals.value.filter(
        item =>
            normalizeTuroyo(roots.value.get(item.entryId) || item.entryId).includes(
                normalizeTuroyo(root.value)
            )
            && (!text.value.trim()
                || item.evidence.some(ref =>
                    `${ref.textId} ${ref.cite}`
                        .toLowerCase()
                        .includes(text.value.trim().toLowerCase())
                )
                || `${item.before || ''} ${item.after || ''} ${item.summary} ${item.rationale}`
                    .toLowerCase()
                    .includes(text.value.trim().toLowerCase()))
    )
)
const groups = computed(() =>
    Object.entries(proposalLabels)
        .map(([kind, label]) => ({
            kind,
            label,
            items: matching.value.filter(item => item.kind === kind),
        }))
        .filter(item => item.items.length)
)
const important = computed(() =>
    matching.value.filter(item => item.priority === 1)
)
const decided = computed(
    () => proposals.value.filter(item => status(item.id) !== 'open').length
)
const group = computed(() =>
    String(
        route.query.group
        || (route.query.proposal
            ? proposals.value.find(item => item.id === route.query.proposal)
                ?.kind || ''
            : '')
    )
)
const groupLabel = computed(() =>
    group.value === 'important'
        ? 'Most important first'
        : proposalLabels[group.value as TProposalKind] || 'Suggested changes'
)
const queue = computed(() =>
    matching.value
        .filter(item =>
            group.value === 'important'
                ? item.priority === 1
                : item.kind === group.value
        )
        .toSorted((a, b) => a.priority - b.priority || a.id.localeCompare(b.id))
)
const active = computed(() =>
    route.query.proposal === 'done'
        ? null
        : queue.value.find(item => item.id === route.query.proposal)
            || queue.value.find(item => status(item.id) === 'open')
            || queue.value[0]
            || null
)
const position = computed(() =>
    active.value
        ? queue.value.findIndex(item => item.id === active.value?.id)
        : queue.value.length - 1
)
const activeId = computed(() => active.value?.entryId || '')
const {
    data: activeEntry,
    pending: entryPending,
    error: entryError,
    refresh: refreshEntry,
} = await useFetch(
    () => `/api/glossary/entries/${encodeURIComponent(activeId.value)}`,
    {
        immediate: !!activeId.value,
        watch: false,
    }
)
watch(activeId, (id) => {
    if (id) refreshEntry()
})
const lastSaved = ref<IProposalReview | null>(null)
const undoing = ref(false)
const cardHeading = ref<HTMLElement | null>(null)
function remaining(items: IProposal[]) {
    return items.filter(item => status(item.id) === 'open').length
}
async function select(kind: string, id: string) {
    if (id !== 'done')
        resume.value = {
            group: kind,
            id,
        }
    await router.push({
        path: '/review',
        query: {
            group: kind,
            proposal: id,
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
    const items
        = kind === 'important'
            ? important.value
            : matching.value.filter(item => item.kind === kind)
    const remembered
        = resume.value?.group === kind
            ? items.find(
                    item => item.id === resume.value?.id && status(item.id) === 'open'
                )
            : null
    const first
        = remembered
            || items
                .toSorted((a, b) => a.priority - b.priority || a.id.localeCompare(b.id))
                .find(item => status(item.id) === 'open')
                || items[0]
    if (first) return select(kind, first.id)
}
function continueReview() {
    if (resume.value) return select(resume.value.group, resume.value.id)
}
function move(delta: number) {
    const next = queue.value[position.value + delta]
    if (next) return select(group.value, next.id)
}
function skip() {
    const next = queue.value[position.value + 1] || queue.value[0]
    if (next) return select(group.value, next.id)
}
function openFirst() {
    if (queue.value[0]) return select(group.value, queue.value[0].id)
}
async function advance(saved: IProposalReview) {
    lastSaved.value = saved
    const candidates = [
        ...queue.value.slice(position.value + 1),
        ...queue.value.slice(0, position.value),
    ]
    const next = candidates.find(item => status(item.id) === 'open')
    await select(group.value, next?.id || 'done')
}
async function undoLast() {
    if (!lastSaved.value) return
    undoing.value = true
    if (await undo(lastSaved.value)) {
        const id = lastSaved.value.proposalId
        lastSaved.value = null
        await select(
            group.value || proposals.value.find(item => item.id === id)?.kind || '',
            id
        )
    }
    undoing.value = false
}
onMounted(() => {
    if (active.value) {
        resume.value = {
            group: group.value,
            id: active.value.id,
        }
        if (!route.query.proposal) router.replace({
            query: {
                group: group.value,
                proposal: active.value.id,
            },
        })
    }
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
