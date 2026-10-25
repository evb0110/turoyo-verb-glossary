<template>
    <article
        :id="`proposal-${proposal.id}`"
        class="proposal"
        :class="`family-${proposalFamily(proposal.kind)}`"
    >
        <div class="proposal-meta">
            <span class="machine-label">Machine proposal</span>
            <span>{{ proposal.kind.replaceAll('-', ' ') }}</span>
            <span
                v-if="proposal.kind === 'note' && proposal.data.type"
                class="pill"
            >{{ proposal.data.type }} note</span>
            <span
                v-if="proposal.data.confidence"
                class="pill confidence"
            >Confidence: {{ proposal.data.confidence }}</span>
            <span v-if="proposal.target.sense">Sense {{ proposal.target.sense }}</span>
            <span class="pill" :data-status="status(proposal.id)">
                {{ status(proposal.id) }}
            </span>
            <span class="priority">P{{ proposal.priority }}</span>
        </div>
        <h4>{{ proposal.summary }}</h4>
        <p v-if="gate && !gate.ok" class="gate-warning" role="alert">
            <strong>Citation check failed.</strong>
            {{ gate.reason || 'The cited text or translation could not be verified.' }}
        </p>
        <div v-if="proposal.before !== null" class="proposal-diff">
            <del>{{ proposal.before }}</del>
            <span aria-label="changes to">→</span>
            <ins>{{ proposal.after || 'Remove' }}</ins>
        </div>
        <p
            v-else-if="proposal.after"
            class="proposed-text serif"
            :class="{ turoyo: proposal.kind === 'add-example' || proposal.kind === 'new-form' }"
        >
            {{ proposal.after }}
        </p>
        <dl v-if="fields.length" class="proposal-fields">
            <div v-for="field in fields" :key="field.key">
                <dt>{{ field.label }}</dt>
                <dd :class="{ turoyo: field.key === 'turoyo' || field.key === 'forms' }">
                    {{ field.value }}
                </dd>
            </div>
        </dl>
        <details class="proposal-details">
            <summary>
                Reason, evidence & review history
                <span class="muted">({{ history(proposal.id).length }})</span>
            </summary>
            <p>{{ proposal.rationale }}</p>
            <div class="row evidence-links">
                <span class="eyebrow">Evidence</span>
                <button
                    v-for="ref in proposal.evidence"
                    :key="`${ref.textId}:${ref.v}`"
                    class="verse-ref"
                    @click="open(ref.textId, ref.v, ref.cite)"
                >
                    {{ ref.cite }}
                </button>
                <span v-if="!proposal.evidence.length" class="muted">
                    No verse evidence supplied
                </span>
            </div>
            <p class="provenance">
                {{ proposal.provenance.model }} · {{ proposal.provenance.effort }} ·
                {{ proposal.stage }} · {{ proposal.provenance.date }}
                <br/>
                {{ proposal.provenance.protocol }} / {{ proposal.provenance.run }}
            </p>
            <ol v-if="history(proposal.id).length" class="history">
                <li v-for="item in history(proposal.id)" :key="item.id">
                    <strong>{{ item.userName }}</strong>
                    · {{ item.verdict }} ·
                    <time :datetime="item.createdAt">
                        {{ formatDate(item.createdAt) }}
                    </time>
                    <p v-if="item.comment">
                        {{ item.comment }}
                    </p>
                </li>
            </ol>
            <p v-else class="muted">
                No reviews yet.
            </p>
        </details>
        <form v-if="isApproved" class="review-form" @submit.prevent>
            <label class="sr-only" :for="`comment-${proposal.id}`">
                Optional comment for {{ proposal.summary }}
            </label>
            <input
                :id="`comment-${proposal.id}`"
                v-model="comment"
                placeholder="Optional review comment…"
                maxlength="5000"
            />
            <div class="row">
                <button
                    v-for="action in actions"
                    :key="action.verdict"
                    class="quiet review-action"
                    :data-verdict="action.verdict"
                    :disabled="pending.includes(proposal.id)"
                    @click="submit(action.verdict)"
                >
                    {{ action.label }}
                </button>
            </div>
        </form>
        <p v-if="history(proposal.id)[0]" class="latest-review muted" aria-live="polite">
            {{ history(proposal.id)[0]?.userName }} ·
            {{ formatDate(history(proposal.id)[0]!.createdAt) }}
        </p>
        <p v-if="saveError" role="alert" class="error">
            {{ saveError }}
        </p>
    </article>
</template>

<script setup lang="ts">
import type { IProposal } from '#shared/types/IProposal'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'
import { proposalFamily } from '#shared/utils/proposalFamily'

const props = defineProps<{ proposal: IProposal }>()
const emit = defineEmits<{ reviewed: [] }>()
const {
    history,
    status,
    pending,
    review,
} = useProposalReviews()
const { isApproved } = useAuth()
const { open } = useEvidence()
const comment = ref('')
const saveError = ref('')
const gate = computed(() => {
    const value = props.proposal.data.gate
    if (!value || typeof value !== 'object' || !('ok' in value) || typeof value.ok !== 'boolean')
        return null
    return {
        ok: value.ok,
        reason: 'reason' in value ? String(value.reason || '') : '',
    }
})
const fields = computed(() =>
    Object.entries(props.proposal.data).flatMap(([key, value]) => {
        if (
            value === null
            || value === undefined
            || value === ''
            || key.endsWith('Id')
            || key === 'confidence'
            || (key === 'type' && props.proposal.kind === 'note')
        )
            return []
        if (typeof value !== 'string' && typeof value !== 'number' && typeof value !== 'boolean')
            return []
        if (String(value) === props.proposal.after) return []
        return [
            {
                key,
                label: key.replace(/([A-Z])/gu, ' $1').replaceAll('_', ' '),
                value: String(value),
            },
        ]
    })
)
const actions: { verdict: TReviewVerdict
    label: string }[] = [
    {
        verdict: 'accept',
        label: 'Accept',
    },
    {
        verdict: 'reject',
        label: 'Reject',
    },
    {
        verdict: 'discuss',
        label: 'Discuss',
    },
]
function formatDate(value: string) {
    return (
        new Date(value).toLocaleString('en-GB', {
            dateStyle: 'medium',
            timeStyle: 'short',
            timeZone: 'UTC',
        }) + ' UTC'
    )
}
async function submit(verdict: TReviewVerdict) {
    saveError.value = ''
    if (await review(props.proposal.id, props.proposal.entryId, verdict, comment.value)) {
        comment.value = ''
        emit('reviewed')
    }
    else saveError.value = 'Review was not saved. Please retry.'
}
</script>

<style scoped>
.proposal {
    --family: var(--addition);
    border-left: 3px solid var(--family);
    background: color-mix(in srgb, var(--family) 5%, var(--paper));
    padding: 0.9rem 1.1rem;
    margin: 0.9rem 0;
    font-size: 0.83rem;
}
.family-correction {
    --family: var(--correction);
}
.family-note {
    --family: var(--note);
}
.proposal-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.55rem;
    color: var(--family);
    font-size: 0.65rem;
}
.machine-label {
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.priority {
    margin-left: auto;
}
h4 {
    font-weight: 600;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}
.gate-warning {
    border: 1px solid var(--correction);
    color: var(--correction);
    background: color-mix(in srgb, var(--correction) 8%, var(--paper));
    padding: 0.6rem 0.8rem;
    margin: 0.6rem 0;
}
.proposal-fields {
    display: grid;
    gap: 0.3rem;
    margin-top: 0.7rem;
}
.proposal-fields > div {
    display: grid;
    grid-template-columns: 6rem 1fr;
    gap: 0.6rem;
}
.proposal-fields dt {
    color: var(--muted);
    font-size: 0.65rem;
    text-transform: capitalize;
}
.proposal-fields dd {
    overflow-wrap: anywhere;
    font-family: var(--font-serif);
    font-size: 1.05rem;
}
.proposed-text {
    font-size: 1.2rem;
    white-space: pre-wrap;
}
.proposal-diff {
    display: flex;
    gap: 0.7rem;
    align-items: baseline;
    flex-wrap: wrap;
    font-family: var(--font-serif);
    font-size: 1.15rem;
    white-space: pre-wrap;
}
del {
    color: var(--muted);
    text-decoration-color: var(--correction);
}
ins {
    text-decoration: none;
    background: color-mix(in srgb, var(--addition) 12%, transparent);
}
.proposal-details {
    margin-top: 0.7rem;
}
summary {
    cursor: pointer;
    color: var(--muted);
    font-size: 0.75rem;
}
.proposal-details p {
    margin-top: 0.7rem;
}
.evidence-links {
    margin: 0.8rem 0;
}
.verse-ref {
    color: var(--accent);
    text-decoration: underline;
    font-size: 0.8rem;
}
.provenance {
    font-size: 0.65rem;
    color: var(--muted);
    overflow-wrap: anywhere;
}
.review-form {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 0.9rem;
}
.review-form input {
    flex: 1;
    min-width: 160px;
    font-size: 0.75rem;
    background: transparent;
}
.review-action {
    font-size: 0.72rem;
}
.review-action[data-verdict='accept'] {
    color: var(--addition);
}
.review-action[data-verdict='reject'] {
    color: var(--correction);
}
.history {
    border-top: 1px solid var(--rule);
    margin-top: 0.7rem;
    padding-top: 0.7rem;
    display: grid;
    gap: 0.5rem;
    font-size: 0.72rem;
}
.latest-review {
    margin-top: 0.5rem;
    font-size: 0.65rem;
}
[data-status='rejected'] {
    opacity: 0.7;
}
</style>
