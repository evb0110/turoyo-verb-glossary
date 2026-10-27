<template>
    <article
        :id="`proposal-${proposal.id}`"
        class="proposal"
        :class="[`family-${proposalFamily(proposal.kind)}`, { decided: !!latest, queue }]"
    >
        <DefineSources>
            <span class="sources small">
                <NuxtLink
                    v-for="ref in sources"
                    :key="`${ref.textId}:${ref.v}`"
                    class="ref"
                    :to="verseHref(ref.textId, ref.v)"
                >
                    <span v-text="ref.cite"></span>
                </NuxtLink>
            </span>
        </DefineSources>
        <DefineBody>
            <p v-if="content === 'move'">
                {{ moveDescription }}
                <Sources v-if="sourcesAt === 'body'"/>
            </p>
            <p v-else-if="content === 'duplicate'">
                Compare
                <NuxtLink :to="entryHref(proposal.entryId)">{{ entry?.root || proposal.entryId }}</NuxtLink>
                with
                <NuxtLink :to="entryHref(duplicateRoot)">{{ duplicateRoot.replaceAll("-", " ") }}</NuxtLink>.
                <Sources v-if="sourcesAt === 'body'"/>
            </p>
            <template v-else-if="content === 'diff'">
                <p class="diff" :class="diffClass">
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
                    <Sources v-if="sourcesAt === 'body'"/>
                </p>
                <p v-if="proposal.after && typeof proposal.data.translation === 'string'" class="small">
                    {{ proposal.data.translation }}
                </p>
            </template>
            <template v-else>
                <p v-if="headword" class="serif headword">
                    {{ headword }}
                </p>
                <div class="wording" :class="{ 'pair': pair, 'with-refs': sourcesAt === 'pair' }">
                    <p :class="wording.turoyo ? 'tur' : 'serif'">
                        {{ wording.text }}
                        <Sources v-if="sourcesAt === 'body'"/>
                    </p>
                    <p v-if="wording.translation" class="translation">
                        {{ wording.translation }}
                        <span v-if="machineTranslation" class="small muted">(machine translation)</span>
                    </p>
                    <p v-if="sourcesAt === 'pair'" class="refs">
                        <Sources/>
                    </p>
                </div>
            </template>
        </DefineBody>
        <DefineDetailsToggle>
            <button
                type="button"
                class="btn-link"
                :aria-expanded="detailsOpen"
                :aria-controls="`details-${proposal.id}`"
                @click="detailsOpen = !detailsOpen"
            >
                {{ detailsOpen ? "Hide details" : "Details" }}
            </button>
        </DefineDetailsToggle>
        <p class="proposal-head">
            <span v-if="proposal.priority === 1" class="flag">Important</span>
            <strong class="action" v-text="action"></strong>
            <span v-if="place" class="muted" v-text="` in ${place}`"></span>
            <span v-if="detail" v-text="`: ${detail}`"></span>
            <Sources v-if="sourcesAt === 'head'"/>
        </p>
        <div v-if="queue" class="compare" :class="{ single: !hasBody }">
            <section class="side">
                <h3 class="side-label">
                    In the glossary now
                </h3>
                <ProposalTarget :entry="entry" :proposal="proposal"/>
            </section>
            <section v-if="hasBody" class="side">
                <h3 class="side-label">
                    Suggested
                </h3>
                <Body/>
            </section>
        </div>
        <div v-else-if="hasBody" class="body">
            <Body/>
        </div>
        <p v-if="gateWarning" class="error small">
            The cited text could not be verified. {{ gateWarning }}
        </p>
        <div v-if="latest?.edited" class="accepted-wording">
            <p class="small">
                <strong>Accepted wording</strong>
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
            <strong>Comment from {{ latest.userName }}:</strong> {{ latest.comment }}
        </p>
        <ProposalDecision
            v-if="isApproved"
            :proposal="proposal"
            :shortcuts="queue"
            :dock="queue"
            @reviewed="emit('reviewed', $event)"
            @undone="emit('undone', $event)"
        >
            <DetailsToggle v-if="!queue"/>
        </ProposalDecision>
        <p v-else-if="latest || !queue" class="read-only">
            <ProposalStatus v-if="latest" :review="latest" :question="question"/>
            <DetailsToggle v-if="!queue"/>
        </p>
        <div v-if="queue || detailsOpen" :id="`details-${proposal.id}`" class="details">
            <p v-if="proposal.rationale || confidence">
                <strong>Reason:</strong> {{ plainProposalText(proposal.rationale) }}
                <span v-if="confidence" class="muted">{{ confidence }}</span>
            </p>
            <div v-if="evidence.length" class="passages">
                <p><strong>In the texts:</strong></p>
                <ProposalEvidence
                    v-for="ref in evidence"
                    :key="`${ref.textId}:${ref.v}`"
                    :reference="ref"
                    :label="ref.label === 'Cited passage' ? '' : ref.label"
                />
            </div>
            <p v-if="!queue && !proposal.rationale && !confidence && !evidence.length" class="muted">
                The machine gave no reason or passages for this {{ question ? proposal.kind : "suggestion" }}.
            </p>
            <ProposalHistory :proposal-id="proposal.id" :question="question" :quiet="queue"/>
        </div>
    </article>
</template>

<script setup lang="ts">
import { createReusableTemplate } from '@vueuse/core'
import type { TProposalPlacement } from '~/types/TProposalPlacement'
import { inlineDiff } from '~/utils/inlineDiff'
import { proposalAction } from '~/utils/proposalAction'
import { proposalEvidence } from '~/utils/proposalEvidence'
import { proposalPlace } from '~/utils/proposalPlace'
import { verseHref } from '~/utils/verseHref'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import { entryHref } from '#shared/utils/entryHref'
import { glossarySenses } from '#shared/utils/glossarySenses'
import { plainProposalText } from '#shared/utils/plainProposalText'
import { proposalContext } from '#shared/utils/proposalContext'
import { proposalFamily } from '#shared/utils/proposalFamily'

const props = withDefaults(
    defineProps<{ proposal: IProposal
        entry: IEntry | null
        queue?: boolean
        placement?: TProposalPlacement }>(),
    {
        queue: false,
        placement: 'entry',
    }
)
const emit = defineEmits<{ reviewed: [review: IProposalReview]
    undone: [proposalId: string] }>()
const [DefineBody, Body] = createReusableTemplate()
const [DefineDetailsToggle, DetailsToggle] = createReusableTemplate()
const [DefineSources, Sources] = createReusableTemplate()
const { decision } = useProposalReviews()
const { isApproved } = useAuth()
const context = computed(() => proposalContext(props.entry, props.proposal))
const latest = computed(() => decision(props.proposal.id))
const question = computed(() => ['question', 'note'].includes(props.proposal.kind))
const detailsOpen = ref(false)
const addition = computed(() =>
    ['new-sense', 'add-example', 'new-idiom', 'new-stem', 'new-form', 'new-root'].includes(props.proposal.kind)
)
// The card's first words say what accepting it does; the location is added only where the card's
// place on the page does not show it (the review queue shows it under "In the glossary now").
// Under the heading "Notes and questions for the editors" a note or question needs no more than its kind.
const action = computed(() => question.value && props.placement === 'entry' && !props.queue
    ? props.proposal.kind === 'note' ? 'Note' : 'Question'
    : proposalAction(props.proposal))
const place = computed(() => proposalPlace(context.value, props.proposal, props.queue ? 'queue' : props.placement))
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
// A new idiom's heading, shown above its example as in the glossary.
const headword = computed(() =>
    props.proposal.kind === 'new-idiom' && typeof props.proposal.data.headword === 'string'
        ? props.proposal.data.headword
        : ''
)
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
    const meaning = context.value.sense
        ? `meaning ${context.value.sense.key} “${context.value.sense.gloss}”`
        : example?.sense ? `meaning ${example.sense}` : ''
    const from = [meaning, box && `${box.label}${meaning ? '' : ' (unnumbered)'}`]
        .filter(Boolean).join(', ') || 'its current place'
    const rawBox = String(data.to_box_label || data.to_box || data.to_box_id || '')
    const toBox = toStem?.boxes.find(item => item.id === rawBox)?.label || rawBox
    const destination = [
        toSense
        && `meaning ${toSense}${targetSense ? ` “${targetSense.gloss}”` : ' (not defined in this entry)'}`,
        toBox && `form ${toBox}`,
        toStemId !== stem?.id && toStemId && `Stem ${toStem?.stem || toStemId}`,
        data.to_entry && `verb ${data.to_entry}`,
    ].filter(Boolean).join(', ')
    return destination ? `From ${from} to ${destination}.` : ''
})
const content = computed(() => {
    const kind = props.proposal.kind
    if (kind === 'move-example' && moveDescription.value) return 'move'
    // A duplicate within the same entry has no other entry to compare with; its summary says what to do.
    if (kind === 'duplicate-entry' && duplicateRoot.value !== props.proposal.entryId) return 'duplicate'
    if (question.value) return 'question'
    if (diff.value.length) return 'diff'
    if (props.proposal.after) return 'after'
    if (addition.value && wording.value.text) return 'data'
    return 'summary'
})
const hasBody = computed(() => !['question', 'summary'].includes(content.value))
// The machine's summary follows the action when it says something of its own: the text of a note or
// question, or what a correction changes. Summaries of additions only repeat the place and wording.
const detail = computed(() =>
    addition.value || props.proposal.kind === 'gloss-change'
        ? hasBody.value ? '' : plainProposalText(props.proposal.summary)
        : plainProposalText(props.proposal.summary)
)
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
// The passages the suggestion cites. An addition lists them at the right like an example's references,
// other suggestions after their text; the example's own references are linked on its row above the card.
// The review queue shows them in full under the card.
const sources = computed(() => evidence.value.filter(ref =>
    ['Cited passage', 'Source of the suggested addition'].includes(ref.label)))
const pair = computed(() => !!(wording.value.text && wording.value.translation))
const sourcesAt = computed(() => {
    if (props.queue || !sources.value.length) return ''
    if (!hasBody.value) return 'head'
    return ['data', 'after'].includes(content.value) && pair.value ? 'pair' : 'body'
})
</script>

<style scoped>
.proposal {
  --family: var(--correction);
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.3rem 1.5rem;
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
.sources {
  margin-left: 0.5rem;
  color: var(--muted);
  font-family: var(--font-sans);
  font-style: normal;
}
.refs .sources {
  margin-left: 0;
}
.ref + .ref::before {
  display: inline-block;
  margin-right: 0.3em;
  color: var(--muted);
  content: ";";
}
.proposal-head {
  font-size: 0.9375rem;
}
.flag {
  margin-right: 0.45rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.action {
  color: var(--family);
  font-weight: 700;
}
.headword {
  font-size: 1.0625rem;
  font-weight: 700;
  font-style: italic;
}
.wording.pair {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  gap: 0 1.5rem;
  align-items: baseline;
}
.wording.with-refs {
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr) 8rem;
}
.translation {
  font-size: 0.9375rem;
}
.compare {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0.5rem 2rem;
}
.compare.single {
  grid-template-columns: minmax(0, 1fr);
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
.keep-lines {
  white-space: pre-line;
}
.accepted-wording {
  display: grid;
  gap: 0.1rem;
}
.read-only {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.6rem;
}
.details {
  display: grid;
  gap: 0.35rem;
  padding: 0.3rem 0 0.3rem 0.75rem;
  border-left: 1px solid var(--rule);
  font-size: 0.9375rem;
}
.passages {
  display: grid;
  gap: 0.35rem;
}
.queue {
  gap: 0.6rem;
  margin: 0;
  padding: 0;
  border-left: 0;
}
.queue .proposal-head {
  font-size: 1.0625rem;
}
.queue .details {
  padding: 0;
  border-left: 0;
  font-size: 1rem;
}
@media (max-width: 1100px) {
  .wording.with-refs {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }
  .refs {
    grid-column: 2;
  }
}
@media (max-width: 760px) {
  .wording.pair,
  .wording.with-refs,
  .compare {
    grid-template-columns: minmax(0, 1fr);
  }
  .refs {
    grid-column: 1;
  }
}
</style>
