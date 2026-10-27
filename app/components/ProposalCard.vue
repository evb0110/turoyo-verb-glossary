<template>
    <article
        :id="`proposal-${proposal.id}`"
        class="proposal"
        :class="[`family-${proposalFamily(proposal.kind)}`, { decided: !!latest, queue }]"
    >
        <DefineTools>
            <span class="proposal-tools small">
                <span v-for="group in citeGroups" :key="group.label" class="cites">
                    <span v-text="`${group.label}: `"></span>
                    <NuxtLink
                        v-for="ref in group.refs"
                        :key="`${ref.textId}:${ref.v}`"
                        class="cite"
                        :to="verseHref(ref.textId, ref.v)"
                    >
                        <span v-text="ref.cite"></span>
                    </NuxtLink>
                </span>
                <button
                    v-if="!queue && (proposal.rationale || confidence)"
                    type="button"
                    class="btn-link"
                    :aria-expanded="panel === 'why'"
                    @click="toggle('why')"
                >
                    Why
                </button>
                <button
                    v-if="!queue && evidence.length"
                    type="button"
                    class="btn-link"
                    :aria-expanded="panel === 'passages'"
                    @click="toggle('passages')"
                >
                    Passages ({{ evidence.length }})
                </button>
                <button
                    type="button"
                    class="btn-link"
                    :aria-expanded="panel === 'history'"
                    @click="toggle('history')"
                >
                    History
                </button>
                <span v-if="!queue && proposal.priority === 1" class="muted">Priority 1</span>
            </span>
        </DefineTools>
        <header class="proposal-head">
            <span class="proposal-kind">{{ proposalKindLabels[proposal.kind] }}</span>
            <span v-if="target" class="proposal-target">{{ target }}</span>
            <span class="proposal-status" :class="{ open: !latest }">{{ statusText }}</span>
        </header>
        <p v-if="showSummary" class="proposal-summary">
            {{ plainProposalText(proposal.summary) }}
        </p>
        <div class="proposal-body" :class="{ compare: queue }">
            <section v-if="queue" class="side">
                <h3 class="side-label">
                    In the glossary now
                </h3>
                <ProposalTarget :entry="entry" :proposal="proposal"/>
            </section>
            <section class="side">
                <h3 v-if="queue" class="side-label">
                    {{ question ? "For the editors" : "Suggested" }}
                </h3>
                <p v-if="content === 'move'">
                    {{ moveDescription }}
                </p>
                <p v-else-if="content === 'duplicate'">
                    Compare
                    <NuxtLink :to="entryHref(proposal.entryId)">{{ entry?.root || proposal.entryId }}</NuxtLink>
                    with
                    <NuxtLink :to="entryHref(duplicateRoot)">{{ duplicateRoot.replaceAll("-", " ") }}</NuxtLink>.
                    {{ plainProposalText(proposal.summary) }}
                </p>
                <p v-else-if="content === 'question' || content === 'summary'">
                    {{ plainProposalText(proposal.summary) }}
                </p>
                <p v-else-if="content === 'diff'" class="diff" :class="diffClass">
                    <template v-for="(part, i) in diffParts" :key="i">
                        <span v-if="part.lead" v-text="part.lead"></span>
                        <del v-if="part.kind === 'delete'">
                            <span class="sr-only">Remove: </span>
                            <span v-text="part.text"></span>
                        </del>
                        <ins
                            v-else-if="part.kind === 'insert'"
                            :class="{ replaces: diffParts[i - 1]?.kind === 'delete' }"
                        >
                            <span class="sr-only">Add: </span>
                            <span v-text="part.text"></span>
                        </ins>
                        <span v-else v-text="part.text"></span>
                    </template>
                </p>
                <div v-else class="wording" :class="{ pair: !!(wording.text && wording.translation) }">
                    <p v-if="wording.text" :class="wording.turoyo ? 'tur' : 'serif'">
                        {{ wording.text }}
                    </p>
                    <p v-if="wording.translation">
                        {{ wording.translation }}
                        <span v-if="machineTranslation" class="small muted">(machine translation)</span>
                    </p>
                </div>
                <p v-if="content === 'diff' && proposal.after && proposal.data.translation" class="small">
                    {{ proposal.data.translation }}
                </p>
                <p v-if="proposal.before && proposal.after === ''" class="small muted">
                    The marked text would be removed.
                </p>
                <p v-if="machineTranslation && content !== 'data' && content !== 'after'" class="small muted">
                    The translation of the cited passage is a machine translation made for this project; check it
                    against the Turoyo.
                </p>
            </section>
        </div>
        <p v-if="gateWarning" class="error small">
            The cited text could not be verified. {{ gateWarning }}
        </p>
        <div v-if="latest?.edited" class="accepted-wording">
            <p class="small">
                <strong>Accepted wording</strong> · {{ latest.userName }}
            </p>
            <p v-if="latest.edited.headword" class="serif">
                {{ latest.edited.headword }}
            </p>
            <p class="keep-lines" :class="wording.turoyo || diffClass === 'tur' ? 'tur' : 'serif'">
                {{ latest.edited.text }}
            </p>
            <p v-if="latest.edited.translation" class="keep-lines">
                {{ latest.edited.translation }}
            </p>
            <p v-else-if="latest.edited.translation === ''" class="small muted">
                No translation.
            </p>
        </div>
        <p v-if="latest?.comment" class="small">
            <strong>Comment</strong> · {{ latest.userName }}: {{ latest.comment }}
        </p>
        <section v-if="queue && (proposal.rationale || confidence)" class="why">
            <h3 class="side-label">
                Why
            </h3>
            <p>{{ plainProposalText(proposal.rationale) }}</p>
            <p v-if="confidence" class="small muted">
                {{ confidence }}
            </p>
        </section>
        <section v-if="queue && evidence.length" class="passages">
            <h3 class="side-label">
                From the texts
            </h3>
            <ProposalEvidence
                v-for="ref in evidence"
                :key="`${ref.textId}:${ref.v}`"
                :reference="ref"
                :label="ref.label"
            />
        </section>
        <ProposalDecision
            v-if="isApproved"
            :proposal="proposal"
            :shortcuts="queue"
            :dock="queue"
            @reviewed="emit('reviewed', $event)"
            @undone="emit('undone', $event)"
        >
            <ToolsRow v-if="!queue"/>
        </ProposalDecision>
        <ToolsRow v-if="queue || !isApproved"/>
        <div v-if="panel === 'why'" class="panel">
            <p>{{ plainProposalText(proposal.rationale) }}</p>
            <p v-if="confidence" class="small muted">
                {{ confidence }}
            </p>
        </div>
        <div v-if="panel === 'passages'" class="panel passages">
            <ProposalEvidence
                v-for="ref in evidence"
                :key="`${ref.textId}:${ref.v}`"
                :reference="ref"
                :label="ref.label"
            />
        </div>
        <ProposalHistory
            v-if="panel === 'history'"
            class="panel"
            :proposal-id="proposal.id"
            :question="question"
        />
    </article>
</template>

<script setup lang="ts">
import { createReusableTemplate } from '@vueuse/core'
import { inlineDiff } from '~/utils/inlineDiff'
import { proposalEvidence } from '~/utils/proposalEvidence'
import { verseHref } from '~/utils/verseHref'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import { entryHref } from '#shared/utils/entryHref'
import { formatReviewDate } from '#shared/utils/formatReviewDate'
import { glossarySenses } from '#shared/utils/glossarySenses'
import { plainProposalText } from '#shared/utils/plainProposalText'
import { proposalContext } from '#shared/utils/proposalContext'
import { proposalFamily } from '#shared/utils/proposalFamily'
import { proposalKindLabels } from '#shared/utils/proposalKindLabels'
import { proposalTarget } from '#shared/utils/proposalTarget'
import { verdictLabel } from '#shared/utils/verdictLabel'

const props = withDefaults(
    defineProps<{ proposal: IProposal
        entry: IEntry | null
        queue?: boolean }>(),
    { queue: false }
)
const emit = defineEmits<{ reviewed: [review: IProposalReview]
    undone: [proposalId: string] }>()
const [DefineTools, ToolsRow] = createReusableTemplate()
const { decision } = useProposalReviews()
const { isApproved } = useAuth()
const context = computed(() => proposalContext(props.entry, props.proposal))
const target = computed(() => proposalTarget(context.value, props.proposal))
const latest = computed(() => decision(props.proposal.id))
const question = computed(() => ['question', 'note'].includes(props.proposal.kind))
const statusText = computed(() => latest.value
    ? `${verdictLabel(latest.value.verdict, question.value, !!latest.value.edited)} · ${latest.value.userName} · ${formatReviewDate(latest.value.createdAt)}`
    : 'Undecided')
const panel = ref<'why' | 'passages' | 'history' | null>(null)
function toggle(name: 'why' | 'passages' | 'history') {
    panel.value = panel.value === name ? null : name
}
const addition = computed(() =>
    ['new-sense', 'add-example', 'new-idiom', 'new-stem', 'new-form', 'new-root'].includes(props.proposal.kind)
)
// Turoyo in italic, meanings and headings in the serif as in the entry, translations and references plain.
const diffClass = computed(() => {
    const field = props.proposal.target.field || ''
    if (['turoyo', 'forms'].includes(field)) return 'tur'
    return ['translation', 'refs', 'note'].includes(field) ? '' : 'serif'
})
const diff = computed(() => {
    const {
        before,
        after,
    } = props.proposal
    if (before === null || after === null || question.value) return []
    const current = context.value.current
    const full = before && current.includes(before) ? current : before
    const proposed = before && current.includes(before) ? current.replace(before, after) : after
    return inlineDiff(full, proposed)
})
// Leading spaces of a change stay outside its mark, so only the changed words are struck or underlined.
const diffParts = computed(() => diff.value.map((part) => {
    const lead = part.kind === 'same' ? '' : /^\s*/u.exec(part.text)?.[0] || ''
    return {
        kind: part.kind,
        lead,
        text: part.text.slice(lead.length),
    }
}))
// The proposed wording of an addition, or the replacement text of a correction without a diff.
const wording = computed(() => {
    const {
        kind,
        after,
        data,
    } = props.proposal
    const turoyo = ['add-example', 'new-form', 'new-idiom'].includes(kind)
    if (after) return {
        text: after,
        translation: typeof data.translation === 'string' ? data.translation : '',
        turoyo,
    }
    const text = String(data.turoyo || data.forms || '')
    const gloss = String(data.gloss || data.translation || '')
    return text
        ? {
                text,
                translation: gloss,
                turoyo: true,
            }
        : {
                text: gloss,
                translation: '',
                turoyo: false,
            }
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
    const toStem = props.entry?.stems.find(item => item.id === toStemId) || stem
    const toSense = String(data.to_sense || '')
    const targetSense = toStem
        && glossarySenses(toStem).find(item => item.key === toSense || item.n === toSense)
    const from = context.value.sense
        ? `meaning ${context.value.sense.key} “${context.value.sense.gloss}”`
        : example?.sense
            ? `meaning ${example.sense}`
            : box?.label || 'its current position'
    const rawBox = String(data.to_box_label || data.to_box || data.to_box_id || '')
    const toBox = toStem?.boxes.find(item => item.id === rawBox)?.label || rawBox
    const destination = [
        toSense
        && `meaning ${toSense}${targetSense ? ` “${targetSense.gloss}”` : ' (not defined in this entry)'}`,
        toBox && `form ${toBox}`,
        toStemId !== stem?.id && toStemId && `Stem ${toStem?.stem || toStemId}`,
        data.to_entry && `verb ${data.to_entry}`,
    ].filter(Boolean).join(' · ')
    return destination ? `Move from ${from}${box ? ` · ${box.label}` : ''} to ${destination}.` : ''
})
const content = computed(() => {
    const kind = props.proposal.kind
    if (kind === 'move-example' && moveDescription.value) return 'move'
    if (kind === 'duplicate-entry') return 'duplicate'
    if (question.value) return 'question'
    if (diff.value.length) return 'diff'
    if (props.proposal.after) return 'after'
    if (addition.value && wording.value.text) return 'data'
    return 'summary'
})
// The summary is the content itself for notes, questions and suggestions without wording.
// A summary that only repeats the proposed wording is left out.
const showSummary = computed(() => !['question', 'summary', 'duplicate'].includes(content.value)
    && !(wording.value.text && ['after', 'data'].includes(content.value)
        && props.proposal.summary.includes(wording.value.text)))
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
        ? 'reason' in gate && gate.reason ? String(gate.reason) : 'Check the printed source.'
        : ''
})
const machineTranslation = computed(() => {
    const gate = props.proposal.data.gate
    return !!gate && typeof gate === 'object' && 'machineTranslation' in gate && !!gate.machineTranslation
})
const evidence = computed(() => proposalEvidence(props.proposal, context.value.example))
const citeGroups = computed(() => {
    const groups: Array<{ label: string
        refs: typeof evidence.value }> = []
    for (const ref of evidence.value) {
        const group = groups.find(item => item.label === ref.label)
        if (group) group.refs.push(ref)
        else groups.push({
            label: ref.label,
            refs: [ref],
        })
    }
    return groups
})
</script>

<style scoped>
.proposal {
  --family: var(--correction);
  display: grid;
  gap: 0.3rem;
  margin: 0.4rem 0 0.6rem;
  padding: 0.15rem 0 0.15rem 0.75rem;
  border-left: 3px solid var(--family);
}
.family-addition {
  --family: var(--addition);
}
.family-note {
  --family: var(--note);
}
.decided {
  border-left-style: dotted;
}
.proposal-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.75rem;
  font-size: 0.875rem;
}
.proposal-kind {
  color: var(--family);
  font-weight: 700;
}
.proposal-target {
  color: var(--muted);
}
.proposal-status {
  margin-left: auto;
  font-weight: 600;
}
.proposal-status.open {
  color: var(--muted);
  font-weight: 400;
}
.proposal-summary {
  font-size: 0.9375rem;
}
.wording.pair {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0 1.5rem;
}
.compare {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0.5rem 2rem;
}
.compare .wording.pair {
  grid-template-columns: minmax(0, 1fr);
}
.side {
  display: grid;
  align-content: start;
  gap: 0.15rem;
}
.side-label {
  color: var(--muted);
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.diff {
  white-space: pre-wrap;
}
del {
  color: var(--deletion);
  text-decoration-thickness: 2px;
}
ins {
  color: var(--addition);
  text-decoration: underline;
  text-decoration-thickness: 2px;
}
ins.replaces {
  margin-left: 0.12em;
}
.cite + .cite::before {
  display: inline-block;
  margin-right: 0.3em;
  color: var(--muted);
  content: ",";
}
.keep-lines {
  white-space: pre-line;
}
.accepted-wording {
  display: grid;
  gap: 0.1rem;
}
.why,
.passages {
  display: grid;
  gap: 0.35rem;
}
.proposal-tools {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.9rem;
  margin-left: 0.6rem;
}
.queue .proposal-tools {
  margin-left: 0;
}
.cites {
  color: var(--muted);
}
.panel {
  padding: 0.35rem 0 0.35rem 0.75rem;
  border-left: 1px solid var(--rule);
}
.queue {
  gap: 0.6rem;
  margin: 0;
  padding: 0;
  border-left: 0;
}
.queue .proposal-summary {
  font-size: 1.0625rem;
  font-weight: 600;
}
@media (max-width: 760px) {
  .wording.pair,
  .compare {
    grid-template-columns: minmax(0, 1fr);
  }
  .proposal-status {
    margin-left: 0;
  }
}
</style>
