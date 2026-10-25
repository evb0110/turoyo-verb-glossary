<template>
    <article
        :id="`proposal-${proposal.id}`"
        class="proposal stack"
        :class="{ 'queue-card': queue }"
    >
        <h2 class="summary">
            {{ plainProposalText(proposal.summary) }}
        </h2>
        <ProposalTarget :entry="entry" :proposal="proposal"/>
        <section class="stack change-section">
            <h3>{{ question ? "Question for the editors" : "Suggested change" }}</h3>
            <p v-if="proposal.kind === 'move-example'">
                {{ moveDescription }}
            </p>
            <p v-else-if="proposal.kind === 'duplicate-entry'">
                Compare
                <NuxtLink :to="entryHref(proposal.entryId)">{{
                    entry?.root || proposal.entryId
                }}</NuxtLink>
                with
                <NuxtLink :to="entryHref(duplicateRoot)">{{
                    duplicateRoot.replaceAll("-", " ")
                }}</NuxtLink>.
                {{ plainProposalText(proposal.summary) }}
            </p>
            <p v-else-if="question">
                {{ plainProposalText(proposal.summary) }}
            </p>
            <p
                v-else-if="diff.length"
                class="inline-diff serif"
                :class="{ turoyo: isTuroyo }"
            >
                <template v-for="(part, i) in diff" :key="i">
                    <del v-if="part.kind === 'delete'"><span class="sr-only">Remove: </span>{{ part.text }}</del>
                    <template v-else-if="part.kind === 'insert'">
                        <wbr v-if="diff[i - 1]?.kind === 'delete'"/><ins>
                            <span class="sr-only">Add: </span>{{ part.text }}</ins>
                    </template>
                    <template v-else>
                        {{ part.text }}
                    </template>
                </template>
            </p>
            <p
                v-else-if="proposal.after"
                class="serif proposed-text"
                :class="{ turoyo: ['add-example', 'new-form', 'new-idiom'].includes(proposal.kind) }"
            >
                {{ proposal.after }}
            </p>
            <template v-else-if="addition">
                <p v-if="proposal.data.turoyo || proposal.data.forms" class="turoyo">
                    {{ proposal.data.turoyo || proposal.data.forms }}
                </p>
                <p
                    v-if="proposal.data.gloss || proposal.data.translation"
                    class="serif"
                >
                    {{ proposal.data.gloss || proposal.data.translation }}
                </p>
            </template>
            <p v-else>
                {{ plainProposalText(proposal.summary) }}
            </p>
            <p v-if="proposal.data.translation && proposal.after" class="serif">
                {{ proposal.data.translation }}
            </p>
            <p v-if="proposal.before && proposal.after === ''" class="caption">
                The marked text would be removed.
            </p>
        </section>
        <section class="stack why-section">
            <h3>Why</h3>
            <p>{{ plainProposalText(proposal.rationale) }}</p>
            <p v-if="confidence" class="caption">
                {{ confidence }}
            </p>
            <p v-if="gateWarning" class="error">
                The cited text could not be verified. {{ gateWarning }}
            </p>
        </section>
        <section v-if="evidence.length" class="stack">
            <h3>From the texts</h3>
            <ProposalEvidence
                v-for="ref in evidence"
                :key="`${ref.textId}:${ref.v}`"
                :reference="ref"
                :label="ref.label"
            />
        </section>
        <p v-else class="caption">
            No text passage was cited for this suggestion.
        </p>
        <section
            v-if="latest"
            class="decision-history stack"
            aria-label="Current decision"
        >
            <p>
                <strong>{{ verdictLabel(latest.verdict) }}</strong> ·
                {{ latest.userName }}<br/><time :datetime="latest.createdAt">{{
                    formatDate(latest.createdAt)
                }}</time>
            </p>
            <p v-if="latest.comment">
                {{ latest.comment }}
            </p>
            <p class="caption">
                You can change this decision below.
            </p>
        </section>
        <details v-if="history(proposal.id).length > 1" class="history">
            <summary>
                Earlier decisions ({{ history(proposal.id).length - 1 }})
            </summary>
            <p v-for="item in history(proposal.id).slice(1)" :key="item.id">
                {{ verdictLabel(item.verdict) }} · {{ item.userName }} ·
                {{ formatDate(item.createdAt) }}<br/>{{ item.comment }}
            </p>
        </details>
        <form v-if="isApproved" class="review-form stack" @submit.prevent>
            <div v-if="commentOpen" :id="`comment-area-${proposal.id}`" class="stack">
                <label :for="`comment-${proposal.id}`">Comment (optional)</label>
                <textarea
                    :id="`comment-${proposal.id}`"
                    v-model="comment"
                    rows="3"
                    maxlength="5000"
                ></textarea>
            </div>
            <p v-if="saveError" role="alert" class="error">
                {{ saveError }}
            </p>
            <div class="decision-bar" :class="{ 'decision-bar-fixed': queue }">
                <button
                    class="text-button comment-toggle"
                    :aria-expanded="commentOpen"
                    :aria-controls="`comment-area-${proposal.id}`"
                    @click="toggleComment"
                >
                    {{ commentOpen ? 'Hide comment' : 'Add a comment' }}
                </button>
                <button class="accept" :disabled="saving" @click="submit('accept')">
                    {{ question ? "Noted" : "Accept" }}
                </button>
                <button
                    class="quiet reject"
                    :disabled="saving"
                    @click="submit('reject')"
                >
                    {{ question ? "Dismiss" : "Reject" }}
                </button>
                <button
                    class="quiet later"
                    :disabled="saving"
                    @click="submit('discuss')"
                >
                    {{ question ? "Discuss later" : "Decide later" }}
                </button>
                <span
                    v-if="saving"
                    class="sr-only"
                    role="status"
                >Saving decision…</span>
            </div>
        </form>
        <p v-if="saved" role="status">
            Saved.
            <button class="text-button" :disabled="undoing" @click="undoSaved">
                Undo
            </button>
        </p>
    </article>
</template>

<script setup lang="ts">
import { inlineDiff } from '~/utils/inlineDiff'
import { plainProposalText } from '~/utils/plainProposalText'
import { proposalContext } from '~/utils/proposalContext'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'
import { entryHref } from '#shared/utils/entryHref'
import { glossarySenses } from '#shared/utils/glossarySenses'

const props = withDefaults(
    defineProps<{ proposal: IProposal
        entry: IEntry | null
        queue?: boolean }>(),
    { queue: false }
)
const emit = defineEmits<{ reviewed: [review: IProposalReview] }>()
const {
    history,
    pending,
    review,
    undo,
} = useProposalReviews()
const { isApproved } = useAuth()
const context = computed(() => proposalContext(props.entry, props.proposal))
const comment = ref('')
const commentOpen = ref(false)
async function toggleComment() {
    commentOpen.value = !commentOpen.value
    if (commentOpen.value) {
        await nextTick()
        const field = document.getElementById(`comment-${props.proposal.id}`)
        field?.focus({ preventScroll: true })
        field?.scrollIntoView({ block: 'center' })
    }
}
const saveError = ref('')
const saved = ref<IProposalReview | null>(null)
const undoing = ref(false)
const saving = computed(() => pending.value.includes(props.proposal.id))
const latest = computed(() => history(props.proposal.id)[0])
const question = computed(() =>
    ['question', 'note'].includes(props.proposal.kind)
)
const addition = computed(() =>
    [
        'new-sense',
        'add-example',
        'new-idiom',
        'new-stem',
        'new-form',
        'new-root',
    ].includes(props.proposal.kind)
)
const isTuroyo = computed(() =>
    ['turoyo', 'forms'].includes(props.proposal.target.field || '')
)
const diff = computed(() => {
    const {
        before,
        after,
    } = props.proposal
    if (before === null || after === null || question.value) return []
    const current = context.value.current
    const full = before && current.includes(before) ? current : before
    const proposed
        = before && current.includes(before) ? current.replace(before, after) : after
    return inlineDiff(full, proposed)
})
const confidence = computed(() =>
    props.proposal.data.confidence === 'high'
        ? 'The machine is fairly sure.'
        : props.proposal.data.confidence === 'medium'
            ? 'The machine is unsure. Please check carefully.'
            : props.proposal.data.confidence === 'low'
                ? 'The machine is uncertain. An editor’s judgement is needed.'
                : ''
)
const gateWarning = computed(() => {
    const gate = props.proposal.data.gate
    return gate && typeof gate === 'object' && 'ok' in gate && gate.ok === false
        ? 'reason' in gate
            ? String(gate.reason)
            : 'Check the printed source.'
        : ''
})
const duplicateRoot = computed(() =>
    String(
        props.proposal.data.duplicate_of
        || props.proposal.data.duplicate_of_entry
        || props.proposal.data.duplicate_entry
        || props.proposal.data.merge_entry
        || props.proposal.data.keep_entry
        || props.proposal.data.retain_entry
        || props.proposal.data.other_entry
        || props.proposal.entryId
    )
)
const moveDescription = computed(() => {
    const {
        stem,
        box,
        example,
    } = context.value
    const data = props.proposal.data
    const toStemId = String(data.to_stem || data.to_stem_id || stem?.id || '')
    const toStem
        = props.entry?.stems.find(item => item.id === toStemId) || stem
    const toSense = String(data.to_sense || '')
    const targetSense
        = toStem
            && glossarySenses(toStem).find(
                item => item.key === toSense || item.n === toSense
            )
    const from = context.value.sense
        ? `meaning ${context.value.sense.key} “${context.value.sense.gloss}”`
        : example?.sense
            ? `meaning ${example.sense}`
            : box?.label || 'its current position'
    const rawBox = String(
        data.to_box_label || data.to_box || data.to_box_id || ''
    )
    const toBox
        = toStem?.boxes.find(item => item.id === rawBox)?.label || rawBox
    const destination = [
        toSense
        && `meaning ${toSense}${targetSense ? ` “${targetSense.gloss}”` : ' (not defined in this entry)'}`,
        toBox && `form ${toBox}`,
        toStemId !== stem?.id && toStemId && `Stem ${toStem?.stem || toStemId}`,
        data.to_entry && `verb ${data.to_entry}`,
    ]
        .filter(Boolean)
        .join(' · ')
    return destination
        ? `Move from ${from}${box ? ` · ${box.label}` : ''} to ${destination}.`
        : plainProposalText(props.proposal.summary)
})
const evidence = computed(() => {
    const rows: { textId: string
        v: number
        cite: string
        label: string }[] = []
    function add(textId: string, v: number, cite: string, label: string) {
        if (!rows.some(item => item.textId === textId && item.v === v))
            rows.push({
                textId,
                v,
                cite,
                label,
            })
    }
    function parse(text: string, label: string) {
        for (const match of text.matchAll(
            /(?<![\p{L}\d])(?:R)?(\d{1,3})\/(\d+)(?:[-–](\d+))?/gu
        )) {
            const end = Math.min(Number(match[3] || match[2]), Number(match[2]) + 8)
            for (let v = Number(match[2]); v <= end; v++)
                add(
                    `R${match[1]!.padStart(3, '0')}`,
                    v,
                    `${Number(match[1])}/${v}`,
                    label
                )
        }
        for (const match of text.matchAll(/JL\s*(\d+)\.(\d+)\.(\d+)/gu))
            add(
                `JL${match[1]!.padStart(2, '0')}.${match[2]!.padStart(2, '0')}`,
                Number(match[3]),
                match[0],
                label
            )
    }
    if (props.proposal.kind === 'fix-citation')
        parse(props.proposal.after || '', 'Suggested reference')
    for (const ref of props.proposal.evidence)
        add(ref.textId, ref.v, ref.cite, 'Cited passage')
    for (const ref of context.value.example?.refs || [])
        if (ref.textId && ref.verse !== null)
            add(
                ref.textId,
                ref.verse,
                ref.raw,
                props.proposal.kind === 'fix-citation'
                    ? 'Current reference'
                    : 'Example in the text'
            )
    if (props.proposal.kind === 'fix-citation')
        parse(props.proposal.before || '', 'Current reference')
    for (const value of [props.proposal.data.ref, props.proposal.data.reference]) {
        if (typeof value === 'string') parse(value, 'Source of the suggested addition')
    }
    return rows
})
function verdictLabel(verdict: TReviewVerdict) {
    return verdict === 'accept'
        ? question.value
            ? 'Noted'
            : 'Accepted'
        : verdict === 'reject'
            ? question.value
                ? 'Dismissed'
                : 'Rejected'
            : 'For discussion later'
}
function formatDate(value: string) {
    return new Date(value).toLocaleString('en-GB', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'UTC',
    }) + ' UTC'
}
async function submit(verdict: TReviewVerdict) {
    saveError.value = ''
    const result = await review(
        props.proposal.id,
        props.proposal.entryId,
        verdict,
        comment.value
    )
    if (result) {
        saved.value = result
        comment.value = ''
        emit('reviewed', result)
    }
    else saveError.value = 'Your decision was not saved. Please try again.'
}
async function undoSaved() {
    if (!saved.value) return
    undoing.value = true
    if (await undo(saved.value)) saved.value = null
    else saveError.value = 'The decision could not be undone. Please try again.'
    undoing.value = false
}
</script>

<style scoped>
.proposal {
  gap: 1.5rem;
}
.summary {
  font-size: 1.65rem;
}
.change-section,
.why-section {
  gap: 0.7rem;
}
.inline-diff {
  white-space: pre-wrap;
  font-size: 1.3rem;
}
del {
  color: var(--deletion);
  background: color-mix(in srgb, var(--deletion) 8%, var(--paper));
  text-decoration-thickness: 2px;
}
ins {
  color: var(--addition);
  background: color-mix(in srgb, var(--addition) 10%, var(--paper));
  text-decoration: underline;
  text-decoration-thickness: 2px;
}
del + ins { margin-left: .12em; }
.proposed-text {
  font-size: 1.3rem;
}
.decision-history {
  border-left: 3px solid var(--accent);
  background: var(--panel);
  padding: 1rem;
  gap: 0.5rem;
}
.history p {
  margin: 0.8rem 0;
}
.comment-toggle {
  grid-column: 1 / -1;
  order: 2;
  justify-self: center;
}
.decision-bar {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  padding: 0.7rem 0;
}
.decision-bar button {
  flex: 1;
  min-height: 54px;
  padding: 0.55rem;
}
.accept {
  background: var(--accent);
  color: var(--paper);
  border-radius: 6px;
  font-weight: 600;
}
.reject {
  color: var(--deletion);
}
@media (max-width: 760px) {
  .queue-card {
    padding-bottom: 8rem;
  }
  .decision-bar-fixed {
    position: fixed;
    z-index: 20;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0.65rem max(0.6rem, env(safe-area-inset-right))
      calc(0.65rem + env(safe-area-inset-bottom));
    background: var(--paper);
    border-top: 1px solid var(--rule);
    gap: 0.4rem;
  }
  .decision-bar-fixed button {
    font-size: 0.889rem;
  }
}
</style>
